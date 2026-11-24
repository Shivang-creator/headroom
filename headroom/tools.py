"""The agent's toolbox.

These are deliberately *native* OpenAI tool schemas rather than a text protocol.
That was a measured decision, not a stylistic one: Paritok segments compressible
blocks out of `role:"tool"` messages. An identical conversation expressed as
plain text in user messages compressed 0%; expressed as native tool calls it
compressed 98%. See docs/FINDINGS.md.
"""
from __future__ import annotations

import inspect
import os
import subprocess
import sys
from pathlib import Path

# How much of a tool result the agent is willing to carry, in characters.
#
# This is the honest crux of the whole comparison, so it is a named parameter
# rather than a buried constant. A real test suite can emit 80,000+ tokens from
# one `pytest` call. Without compression you have two options: truncate — and
# choose blindness about whatever fell off the end — or exceed the window and
# die. 120,000 chars is roughly 41,000 tokens, i.e. deliberately larger than the
# 32,768 ceiling, so the trade-off is visible instead of hidden.
#
# Lower it and the paritok-off arm survives longer while seeing less. That is a
# real strategy, not a straw man, which is why `headroom ab --truncate` exists.
DEFAULT_MAX_TOOL_OUTPUT = 120_000

# Characters per page of a large tool result. ~9,000 chars ≈ 3,100 tokens.
#
# We originally sized this to dodge a block-size limit we thought we'd measured;
# that turned out to be a transient backend outage and is retracted (see
# docs/FINDINGS.md §4). Pagination stays because it is the right shape anyway:
# it bounds how much any single tool result can cost, keeps blocks in the range
# where compression measured best, and lets the agent decide how much of a large
# result it actually needs.
PAGE_CHARS = 9_000


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and directories under a path, relative to the repo root.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Relative path. Use '.' for the repo root."}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a source file in full. Returns the file with line numbers.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path relative to the repo root."}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search the repo for a regular expression. Returns matching lines with file:line prefixes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string", "description": "Optional subdirectory to restrict the search to."},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "Run a shell command inside the task repo. Use this to run the tests.",
            "parameters": {
                "type": "object",
                "properties": {"cmd": {"type": "string"}},
                "required": ["cmd"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_patch",
            "description": (
                "Replace an exact string in a file. `old` must appear exactly once. "
                "Use this to fix the bug once you have found it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old": {"type": "string", "description": "Exact text to replace, including indentation."},
                    "new": {"type": "string", "description": "Replacement text."},
                },
                "required": ["path", "old", "new"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "next_page",
            "description": (
                "Fetch the next page of a large tool result that was paginated. "
                "Call repeatedly until it reports no pages remain."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Call this only once the tests pass. Ends the session.",
            "parameters": {
                "type": "object",
                "properties": {"summary": {"type": "string", "description": "What the bug was and how you fixed it."}},
                "required": ["summary"],
            },
        },
    },
]


_SECRET_ENV_MARKERS = ("API_KEY", "TOKEN", "SECRET", "PASSWORD")


class Toolbox:
    """Executes tool calls against one task repo, sandboxed to that directory."""

    def __init__(self, workdir: Path, max_tool_output: int = DEFAULT_MAX_TOOL_OUTPUT,
                 page_chars: int = PAGE_CHARS, paginate: bool = True):
        self.workdir = Path(workdir).resolve()
        self.max_tool_output = max_tool_output
        self.page_chars = page_chars
        self.paginate = paginate
        self.patches_applied = 0
        self.truncations = 0
        self._pages: list[str] = []
        self._page_source = ""

    # -- paging -----------------------------------------------------------
    def _paginate(self, source: str, text: str) -> str:
        """Return page 1 and stash the rest.

        Pages are sized to the range where compression measured best. One
        82,000-token tool result also blows the upstream context window on its
        own; twenty 3,000-token pages do not, and the agent can stop reading
        once it has seen enough.
        """
        if not self.paginate:
            # Truncating arm: keep the head, say what was lost. The agent is not
            # deceived about the loss — it simply cannot get the rest back.
            self._pages, self._page_source = [], ""
            return text
        if len(text) <= self.page_chars:
            self._pages, self._page_source = [], ""
            return text
        self._pages = [text[i:i + self.page_chars] for i in range(0, len(text), self.page_chars)]
        self._page_source = source
        first = self._pages[0]
        return (f"{first}\n\n[page 1 of {len(self._pages)} from {source} — "
                f"call next_page to continue]")

    # -- path safety ------------------------------------------------------
    def _resolve(self, rel: str) -> Path:
        target = (self.workdir / rel).resolve()
        if target != self.workdir and self.workdir not in target.parents:
            raise ValueError(f"path escapes the task repo: {rel}")
        return target

    # -- dispatch ---------------------------------------------------------
    def call(self, name: str, args: dict) -> str:
        try:
            fn = getattr(self, f"_t_{name}", None)
            if fn is None:
                return f"ERROR: unknown tool {name!r}"
            # Models routinely pass arguments that aren't in the schema — a
            # `page` hint to next_page, a stray `recursive` to list_dir. Dropping
            # them beats surfacing a TypeError the model then has to recover
            # from, which costs a turn and pollutes the context we're measuring.
            params = inspect.signature(fn).parameters
            if not any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()):
                args = {k: v for k, v in args.items() if k in params}
            out = str(fn(**args))
            if len(out) > self.max_tool_output:
                self.truncations += 1
                dropped = len(out) - self.max_tool_output
                # Say so explicitly. Silent truncation would let the agent draw
                # confident conclusions from output it never actually saw.
                return (out[: self.max_tool_output]
                        + f"\n\n[TRUNCATED: {dropped:,} more characters were dropped "
                          f"to fit the context budget.]")
            return out
        except TypeError as exc:
            return f"ERROR: bad arguments for {name}: {exc}"
        except Exception as exc:  # surfaced to the model so it can recover
            return f"ERROR: {type(exc).__name__}: {exc}"

    # -- tools ------------------------------------------------------------
    def _t_list_dir(self, path: str = ".") -> str:
        root = self._resolve(path)
        if not root.is_dir():
            return f"ERROR: not a directory: {path}"
        lines = []
        for p in sorted(root.rglob("*")):
            if any(part in {".git", "__pycache__", ".pytest_cache"} for part in p.parts):
                continue
            rel = p.relative_to(self.workdir)
            lines.append(f"{rel}/" if p.is_dir() else f"{rel}  ({p.stat().st_size} bytes)")
        return "\n".join(lines) or "(empty)"

    def _t_read_file(self, path: str) -> str:
        target = self._resolve(path)
        if not target.is_file():
            return f"ERROR: no such file: {path}"
        text = target.read_text(errors="replace")
        numbered = "\n".join(f"{i:5d}| {line}" for i, line in enumerate(text.splitlines(), 1))
        return self._paginate(path, numbered)

    def _t_grep(self, pattern: str, path: str = ".") -> str:
        root = self._resolve(path)
        proc = subprocess.run(
            ["grep", "-rnE", "--binary-files=without-match", "-e", pattern, "--", str(root)],
            capture_output=True, text=True, timeout=30,
        )
        if proc.returncode not in (0, 1):
            return f"ERROR: grep failed: {proc.stderr.strip()}"
        out = proc.stdout.replace(f"{self.workdir}/", "")
        return out.strip() or f"(no matches for {pattern!r})"

    def _t_run_bash(self, cmd: str) -> str:
        # Put the interpreter running Headroom at the front of PATH so a bare
        # `python -m pytest` resolves inside the task repo. macOS has no bare
        # `python`, and the agent should not have to know that.
        # The command is chosen by the model, so it gets no credentials: a
        # `env` or `printenv` would otherwise copy the provider keys into the
        # transcript, the store and the exported examples.
        env = {k: v for k, v in os.environ.items()
               if not any(m in k.upper() for m in _SECRET_ENV_MARKERS)}
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
        proc = subprocess.run(
            cmd, shell=True, cwd=self.workdir, capture_output=True, text=True, timeout=180, env=env,
        )
        parts = [f"$ {cmd}", f"(exit {proc.returncode})"]
        if proc.stdout.strip():
            parts.append(proc.stdout)
        if proc.stderr.strip():
            parts.append(proc.stderr)
        return self._paginate(f"`{cmd}`", "\n".join(parts))

    def _t_apply_patch(self, path: str, old: str, new: str) -> str:
        target = self._resolve(path)
        if not target.is_file():
            return f"ERROR: no such file: {path}"
        text = target.read_text()
        hits = text.count(old)
        if hits == 0:
            return "ERROR: `old` not found. Read the file again and copy the text exactly, including indentation."
        if hits > 1:
            return f"ERROR: `old` appears {hits} times. Include more surrounding context to make it unique."
        target.write_text(text.replace(old, new, 1))
        self.patches_applied += 1
        return f"Patched {path}. Run the tests to confirm."

    def _t_next_page(self) -> str:
        if len(self._pages) <= 1:
            self._pages = []
            return "No further pages."
        self._pages.pop(0)
        remaining = len(self._pages)
        body = self._pages[0]
        if remaining == 1:
            return f"{body}\n\n[final page from {self._page_source}]"
        return (f"{body}\n\n[{remaining} page(s) remaining from {self._page_source} — "
                f"call next_page to continue]")

    def _t_finish(self, summary: str) -> str:
        return f"FINISHED: {summary}"

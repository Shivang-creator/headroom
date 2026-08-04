[![Built with Paritok](https://img.shields.io/badge/Built%20with-Paritok-1f2d3d)](https://github.com/Paritok-official/paritok-4b-v1)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

# Headroom

**A coding agent inside a 32,768-token ceiling, and the harness that measures
what context compression is actually worth.**

Built with [Paritok](https://github.com/Paritok-official/paritok-4b-v1).

---

## The setting

Flat-rate inference is the cheapest way to run an agent. Featherless is $25/month
for unlimited tokens across 21,000+ open models. The catch is the context
ceiling: on that plan every model is capped at **32,768 tokens** — even
`GLM-5.1`, whose *native* context is 202,752. Exceed it and the request is
refused outright:

```
Maximum context length for model 'zai-org/GLM-5.1' allowed on your plan is
32768 tokens. Your prompt has 38435 tokens, which exceeds the maximum context
length limit by 5667 tokens.
```

Headroom is a coding agent that fixes real bugs in real repositories, plus an A/B
harness that runs each task twice — once straight to Featherless, once through
the [Paritok](https://github.com/Paritok-official/paritok-4b-v1) compression
proxy — and reports what changed.

## What we actually found

We set out to show an agent that dies without compression and survives with it.
**That is not what the data says, and we are reporting what the data says.**

**1. Compression cuts input tokens by 48–82% with identical outcomes.** Across
three seeded tasks, both arms solved every task, applied the same patches, and
ended with the tests green. Compression cost about one extra turn and some wall
time. That is a real, reproducible win.

**2. A competent agent doesn't overflow 32K as easily as we assumed.** It greps
instead of reading exhaustively and pipes verbose output through `head`. Breadth
of codebase alone did not overflow the window — our 217KB, 20-module, three-bug
task peaked at 12,116 tokens. Context engineering the agent already does for
itself is doing a lot of the work people credit to compression.

**3. The one case that does overflow is the case Paritok can't help with.** A
single tool result larger than the window — 306 failing parameterised tests,
~82,000 tokens from one `pytest` call — kills the run. But the hosted compressor
**silently returns input verbatim above ~6,000 tokens**, so it declines to
compress exactly the blocks that cause the problem. Measured, reproducible, and
detailed in [§4 of FINDINGS](docs/FINDINGS.md). Headroom works around it by
paginating oversized tool output into ~3,100-token pages that sit inside the band
where compression actually works — which turns that task from a hard failure into
a solved one.

So the honest summary: **Paritok is a substantial and reliable cost win on
accumulated multi-turn context, and today it has a size ceiling that stops it
being a capability unlock.** The workaround is cheap and it's in this repo.

## Measured results

Produced by `python -m headroom ab <task>`, against a pristine copy of the repo
per arm. The agent is never told which arm it is in.

<!-- RESULTS:START -->

| Task | Arm | Outcome | Turns | Peak prompt tokens | Total input tokens | Tests |
|---|---|---|---:|---:|---:|:--:|
| `task01_report_mean` | Paritok off | ✓ solved | 9 | 7,013 | 29,823 | ✅ |
| `task01_report_mean` | Paritok **on** | ✓ solved | 10 | 2,100 | 14,589 | ✅ |
| `task02_pipeline_triage` | Paritok off | ✓ solved | 15 | 12,116 | 91,281 | ✅ |
| `task02_pipeline_triage` | Paritok **on** | ✓ solved | 16 | 5,146 | 37,308 | ✅ |
| `task03_verbose_suite` | Paritok off | ✓ solved | 11 | 7,184 | 38,025 | ✅ |
| `task03_verbose_suite` | Paritok **on** | ✓ solved | 11 | 4,833 | 23,946 | ✅ |
| `task03_verbose_suite` | Paritok off | ✗ overflow at turn 2 | 2 | 38,442 | 39,230 | ❌ |
| `task03_verbose_suite` | Paritok **on** | ✗ overflow at turn 2 | 2 | 38,435 | 39,223 | ❌ |
| `task03_verbose_suite` | Paritok off | ✓ solved | 9 | 8,716 | 48,708 | ✅ |
| `task03_verbose_suite` | Paritok **on** | ✓ solved | 10 | 4,388 | 35,093 | ✅ |

Across the 4 runs that completed, Paritok cut input tokens by **47.8–81.6%** (mean 66.2%), with both arms reaching the same outcome — same patches, tests green — on every task.

The `overflow at turn 2` rows are the unpaginated version of task 3, kept deliberately: a single 82,000-token tool result kills **both** arms, because the compressor passes through blocks above ~6,000 tokens. Pagination is what fixes it — see [docs/FINDINGS.md §4](docs/FINDINGS.md).

<!-- RESULTS:END -->

## How it works

```
  agent ──► Paritok proxy (:8080) ──► Featherless ──► GLM-5.1
             │
             └─► Paritok hosted GPU (4B compressor)
```

The agent speaks ordinary OpenAI chat-completions. Only `base_url` differs
between the two arms — the agent has no idea whether its context is being
compressed, which is what keeps the comparison honest.

| Component | File | What it does |
|---|---|---|
| Agent loop | [`headroom/agent.py`](headroom/agent.py) | Native tool-calling ReAct loop with retry/backoff |
| Toolbox | [`headroom/tools.py`](headroom/tools.py) | `list_dir`, `read_file`, `grep`, `run_bash`, `apply_patch`, `finish` |
| Context governor | [`headroom/governor.py`](headroom/governor.py) | Tracks headroom against the ceiling; turns a rejection into a measurement |
| A/B runner | [`headroom/ab.py`](headroom/ab.py) | Runs both arms on pristine repo copies, diffs the outcomes |
| Dashboard | [`headroom/server.py`](headroom/server.py) | Side-by-side comparison + live `/stats` |
| Tasks | [`tasks/`](tasks/) | Seeded bug-fix repos judges can reproduce |

## Four things we learned the hard way

These cost real debugging time and none of them are in Paritok's docs. Written
up in full in [`docs/FINDINGS.md`](docs/FINDINGS.md), and filed upstream.

**1. Paritok only compresses native tool calls.** We originally built the agent
with a text protocol — the model emitting JSON actions inside message content —
specifically to route around Paritok's open tool-calling issues. That version
compressed **0%**. Paritok segments compressible blocks out of `role:"tool"`
messages; content it can't recognise as a tool result passes through untouched.
The identical conversation in native `tool_calls` form compressed **98%**. If
your agent uses a text protocol, Paritok does nothing for you.

**2. `history.context_window` must match your real ceiling.** It defaults to
`200000`, and history compression only triggers at `context_threshold` (0.8) of
it — 160,000 tokens. Against a 32,768-token upstream that threshold is
unreachable, so compression never fires and every request is forwarded at full
size. Setting it to `32768` is what makes any of this work.

**3. Empty compressions are usually correct, and indistinguishable from failure.**
Paritok's compressor is *query-conditioned*: it compresses each block relative to
the latest user turn. Ask something unrelated to the context and it correctly
returns nothing for every block. But a genuine GPU failure also returns nothing,
and both become a `[REF:id]` stub. There's no signal to tell them apart.

**4. Blocks above ~6,000 tokens come back verbatim, silently.** Reproducible with
[`tools/probe_block_size.py`](tools/probe_block_size.py) — identical across two
runs. A 4,001-token block compresses to 74 tokens (0.019). A 6,006-token block
returns unchanged, in 2.4 seconds. So does 40,055. Meanwhile
`compression.max_tokens` defaults to **50,000**, an order of magnitude above
where compression actually stops working, and the failure surfaces downstream as
`below_refusal_threshold` — which reads like a judgement about content rather
than a size cutoff. This is why we paginate.

## Setup

Requires Python 3.10+, a [Paritok API key](https://www.paritok.com/), and a
[Featherless](https://featherless.ai) key.

```bash
git clone https://github.com/Shivang-creator/headroom
cd headroom
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

export PARITOK_API_KEY=pk_live_...
export FEATHERLESS_API_KEY=rc_...
```

**Terminal 1 — the proxy** (must stay running):

```bash
.venv/bin/paritok proxy --port 8080 --config-file paritok.yaml \
    --openai-url https://api.featherless.ai/v1/chat/completions
```

**Terminal 2 — the comparison:**

```bash
.venv/bin/python -m headroom ab tasks/task02_pipeline_triage
.venv/bin/python -m headroom serve      # dashboard on :8900
```

See [RUNME.md](RUNME.md) for the exact reproduction sequence.

## Repository layout

```
headroom/          the agent, governor, A/B runner, dashboard
tasks/             seeded bug-fix repos + the generator that builds them
examples/          committed transcripts and results from real runs
docs/FINDINGS.md   what we measured about Paritok, including the surprises
tools/             model probe used to pick a usable upstream
paritok.yaml       proxy config — note context_window: 32768
```

## Credits

Built with [Paritok](https://github.com/Paritok-official/paritok-4b-v1) —
the open-source context-compression model for coding agents.
Upstream inference by [Featherless AI](https://featherless.ai).

Licensed under [Apache 2.0](LICENSE).

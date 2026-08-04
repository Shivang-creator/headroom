[![Built with Paritok](https://img.shields.io/badge/Built%20with-Paritok-1f2d3d)](https://github.com/Paritok-official/paritok-4b-v1)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

# Headroom

**Run a real coding agent on a cheap, flat-rate model whose context window is far too small for it.**

Built with [Paritok](https://github.com/Paritok-official/paritok-4b-v1).

---

## The problem

Flat-rate inference providers are the cheapest way to run an agent. Featherless
is $25/month for unlimited tokens across 21,000+ open models. The catch is the
context ceiling: on that plan, every model is capped at **32,768 tokens** — even
`GLM-5.1`, whose *native* context is 202,752.

A real coding agent blows straight through 32K. It reads files, runs tests,
reads more files, and every one of those results stays in the conversation. Ours
crosses 30,000 tokens around turn 15 of a three-bug triage task. After that,
every request is rejected:

```
Maximum context length for model 'zai-org/GLM-5.1' allowed on your plan is
32768 tokens. Your prompt has 35627 tokens, which exceeds the maximum context
length limit by 2859 tokens.
```

The run doesn't degrade. It stops.

## What Headroom does

Headroom is a coding agent that fixes real bugs in real repositories, plus the
measurement harness that proves what compression is worth. Every LLM request
goes through [Paritok](https://github.com/Paritok-official/paritok-4b-v1), which
compresses the accumulated context in flight before it reaches the model.

**The claim is not that this is cheaper. It's that the agent runs at all.**

Compression turns a 32,768-token ceiling into an effective working window
several times larger, which moves long-horizon agentic work onto a tier of
infrastructure that previously could not host it.

## Measured results

Every number below is produced by `python -m headroom ab <task>`, which runs the
identical task twice — once straight to Featherless, once through the Paritok
proxy — against a pristine copy of the repo each time. The agent is not told
which arm it is in.

<!-- RESULTS:START -->
_Populated by `python -m headroom export` after the runs complete._
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

## Three things we learned the hard way

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

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

Headroom is a coding agent that fixes real bugs in real repositories, plus a
harness that runs each task under **three** strategies for handling oversized
tool output — truncate, paginate, and paginate-through-[Paritok](https://github.com/Paritok-official/paritok-4b-v1) —
against a pristine copy of the repo each time, and reports what changed.

## What we actually found

We set out to show an agent that dies without compression and survives with it.
**That is not what the data says, and we are reporting what the data says.**

**1. Compression cuts input tokens by a third to a half, with identical
outcomes.** Against the `paginate` arm — same agent, same evidence, differing
only by `base_url` — the compressed arm used **12–52% fewer input tokens**
(mean 39%), and **45–81% less** measured at the proxy itself. Across 12 runs on
4 tasks, **every arm solved every task**, applied the same patches, and ended
with the tests green. Compression cost a few extra turns and some wall time.

**2. A competent agent doesn't overflow 32K, and you can't easily make it.**
It greps instead of reading exhaustively and pipes verbose output through `head`.
Our 217KB, 20-module, three-bug task peaked at 11,994 tokens. We then built
task 4 specifically to force an overflow — 462 failing cases across 41 pages,
with a brief instructing the agent three separate times to page through all of
them. **It stopped after about ten pages anyway**, formed a correct hypothesis,
and fixed the bug. Agents do a lot of their own context management, robustly
enough to resist instruction. Measure that before crediting a tool.

**3. Truncation is not reliably the cheap option.** On task 3 the truncating arm
burned **86,739 input tokens against pagination's 48,901** — 77% more — *and*
discarded a tool result. On task 4 it did come out 16% cheaper, but again only
by throwing evidence away. A truncated chunk sits in context at full size on
every later turn; pagination spends its tokens once. The strategy everyone
reaches for first is the one with the least predictable cost.

**4. Compression carries far more context than it's billed for.** On task 4 the
compressed arm's payload peaked at **26,222 tokens sent against 6,502 billed** —
it worked through more pages than the uncompressed arm managed, while sitting at
a fifth of the ceiling. That is the mechanism working exactly as advertised.

**5. The one case that genuinely overflows is the case Paritok can't help with.**
A single tool result larger than the window — ~82,000 tokens from one `pytest`
call — kills the run. But the hosted compressor **silently returns input verbatim
above ~6,000 tokens**, so it declines exactly the blocks that cause the problem.
Measured, reproducible, and detailed in [§4 of FINDINGS](docs/FINDINGS.md).
Headroom works around it by paginating into ~3,100-token pages that sit inside
the band where compression works — which turns that task from a hard failure into
a solved run.

So the honest summary: **Paritok is a substantial and reliable cost win on
accumulated multi-turn context, and today a size ceiling stops it being a
capability unlock.** The workaround is cheap and it's in this repo.

## Measured results

Produced by `python -m headroom ab <task>`, against a pristine copy of the repo
per arm. The agent is never told which arm it is in.

<!-- RESULTS:START -->

| Task | Strategy | Outcome | Turns | Peak billed | Peak sent | Total input | Trunc | Tests |
|---|---|---|---:|---:|---:|---:|---:|:--:|
| `task01_report_mean` | truncate | ✓ solved | 9 | 7,112 | 10,501 | 30,648 | — | ✅ |
| `task01_report_mean` | paginate | ✓ solved | 9 | 6,116 | 9,075 | 27,142 | — | ✅ |
| `task01_report_mean` | **paritok** | ✓ solved | 9 | 2,079 | 9,075 | 13,225 | — | ✅ |
| `task02_pipeline_triage` | truncate | ✓ solved | 15 | 12,208 | 17,722 | 92,518 | — | ✅ |
| `task02_pipeline_triage` | paginate | ✓ solved | 15 | 11,994 | 17,352 | 91,167 | — | ✅ |
| `task02_pipeline_triage` | **paritok** | ✓ solved | 17 | 5,306 | 17,451 | 43,808 | — | ✅ |
| `task03_verbose_suite` | truncate | ✓ solved | 9 | 13,546 | 17,602 | 86,739 | 1× | ✅ |
| `task03_verbose_suite` | paginate | ✓ solved | 9 | 8,816 | 12,230 | 48,901 | — | ✅ |
| `task03_verbose_suite` | **paritok** | ✓ solved | 13 | 6,111 | 12,716 | 43,054 | — | ✅ |
| `task04_full_audit` | truncate | ✓ solved | 11 | 13,788 | 18,102 | 94,251 | 1× | ✅ |
| `task04_full_audit` | paginate | ✓ solved | 14 | 12,131 | 16,415 | 111,971 | — | ✅ |
| `task04_full_audit` | **paritok** | ✓ solved | 16 | 6,502 | 26,222 | 64,320 | — | ✅ |

Measured at the proxy, Paritok compressed the context it saw by **45.3–80.6%** (mean 67.0%).

End to end, `paritok` used **12.0–51.9% fewer input tokens than `paginate`** (mean 39.4%) while seeing the same evidence and reaching the same fix. Those two arms are identical apart from `base_url`, so the difference is attributable to compression alone.

<!-- RESULTS:END -->

## How it works

```
  agent ──► Paritok proxy (:8080) ──► Featherless ──► GLM-5.1
             │
             └─► Paritok hosted GPU (4B compressor)
```

The agent speaks ordinary OpenAI chat-completions. Between the `paginate` and
`paritok` arms only `base_url` differs — the agent has no idea whether its
context is being compressed, which is what keeps the comparison honest.

| Component | File | What it does |
|---|---|---|
| Agent loop | [`headroom/agent.py`](headroom/agent.py) | Native tool-calling ReAct loop with retry/backoff |
| Toolbox | [`headroom/tools.py`](headroom/tools.py) | `list_dir`, `read_file`, `grep`, `run_bash`, `apply_patch`, `next_page`, `finish` |
| Context governor | [`headroom/governor.py`](headroom/governor.py) | Tracks headroom against the ceiling; turns a rejection into a measurement |
| Comparison runner | [`headroom/ab.py`](headroom/ab.py) | Runs all three strategies on pristine repo copies, diffs the outcomes |
| Preflight | [`headroom/doctor.py`](headroom/doctor.py) | Verifies compression will actually fire *before* you trust a number |
| Dashboard | [`headroom/server.py`](headroom/server.py) | Side-by-side comparison + live `/stats` |
| Tasks | [`tasks/`](tasks/) | Seeded bug-fix repos judges can reproduce |
| Tests | [`tests/`](tests/) | 38 tests over the harness itself |

### The three strategies

Comparing only "compression on/off" hides the fact that the honest baseline
isn't "off" — it's **truncation**, which is what most agents do today. So every
task runs three ways:

| Arm | What it does | Cost |
|---|---|---|
| `truncate` | Cut oversized output to fit and hope the useful part survived | Cheap, but discards evidence |
| `paginate` | Page through everything, uncompressed | Nothing lost, full-price context |
| `paritok` | Page through everything, compressed | Nothing lost, ~1/5 the context |

`truncate` vs `paginate` isolates the cost of *seeing everything*.
`paginate` vs `paritok` isolates the value of *compression* — those two arms are
byte-identical apart from `base_url`, which is what makes the number attributable.

### Preflight

Compression failing silently is the failure mode that wastes your day — the
request succeeds, `/stats` increments, and nothing is compressed. `doctor`
checks the things that produce no error on their own:

```bash
python -m headroom doctor
```

```
Configuration
  ✓ history.context_window — 32,768 (matches the upstream ceiling)
  ! compression.max_tokens — 50,000 — the hosted compressor returns input
    verbatim above ~6,000 tokens, so blocks between 6,000 and this value are
    silently skipped. Headroom paginates to stay under it.
Paritok
  ✓ compression smoke test — 12,650 → 721 chars (ratio 0.057)
Upstream
  ✓ upstream zai-org/GLM-5.1 — reachable, emits native tool calls
```

Paritok's [issue #29](https://github.com/Paritok-official/paritok-4b-v1/issues/29)
asks for exactly this. Ours is a starting point they're welcome to take.

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

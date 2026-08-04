# Demo video script — target 2:40, hard limit 3:00

Screen recording + voiceover. No music (rules forbid copyrighted audio).

**Before you hit record:**

```bash
# terminal 1 — proxy running, scrolled to the top
cd ~/Projects/headroom && export PARITOK_API_KEY=... FEATHERLESS_API_KEY=...
.venv/bin/paritok proxy --port 8080 --config-file paritok.yaml \
    --openai-url https://api.featherless.ai/v1/chat/completions

# terminal 2 — cleared, big font (18pt+), ready to run
# browser tab — http://127.0.0.1:8900 loaded, and paritok.com/dashboard in a second tab
```

Do one dry run of `headroom ab tasks/task01_report_mean` first so the model is
warm — a cold Featherless call can stall 20s and eat your runtime.

---

## 0:00–0:20 — The constraint

> "Flat-rate inference is the cheapest way to run a coding agent. Twenty-five
> dollars a month, unlimited tokens, twenty-one thousand open models. But on that
> plan every model is capped at 32,768 tokens of context — even ones whose native
> window is two hundred thousand. Go over, and the request isn't slow. It's
> refused."

**Show:** the raw error, full screen.

```
Maximum context length for model 'zai-org/GLM-5.1' allowed on your plan is
32768 tokens. Your prompt has 38435 tokens.
```

## 0:20–0:45 — What Headroom is

> "Headroom is a coding agent that fixes real bugs, plus a harness that measures
> what context compression is worth. It runs every task twice — once straight to
> the provider, once through the Paritok proxy — on a fresh copy of the repo each
> time. The agent is never told which run it's in."

**Show:** `headroom/config.py` — highlight that `base_url` is the only difference
between arms. Then the architecture block from the README.

## 0:45–1:40 — The run

> "Here's a repo with three unrelated bugs across twenty modules. The failing test
> doesn't name the culprit, so the agent has to trace the data path."

**Show:** `.venv/bin/python -m headroom ab tasks/task02_pipeline_triage`

Let the headroom bars actually climb on screen — that's the whole visual. Talk
over it:

> "Every file read, every test run, every log line stays in the conversation.
> Watch the context grow. On the left run that's real tokens going to the
> provider. On the right, Paritok is compressing the accumulated history in
> flight before it ever leaves the machine."

**Land on the comparison table.**

> "Both runs solved it. Same three patches, tests green in both. But the
> compressed run used 37,000 input tokens against 91,000 — **81.6% fewer**, for
> one extra turn."

## 1:40–2:10 — The honest part

> "We set out to show the agent dying without compression and surviving with it.
> The data didn't support that, so we're not claiming it."

**Show:** the "What we actually found" section of the README.

> "A competent agent doesn't overflow 32K as easily as we assumed — it greps
> instead of reading everything. What *does* overflow it is a single huge tool
> result: three hundred failing tests, eighty-two thousand tokens from one pytest
> call. And that's the case Paritok can't currently help with — we measured that
> the hosted compressor silently returns input unchanged above about six thousand
> tokens."

**Show:** the block-size table, briefly.

## 2:10–2:35 — The fix we shipped

> "So Headroom paginates. Oversized tool output gets split into three-thousand-token
> pages that land inside the band where compression actually works. That turns
> that task from a hard failure into a solved run."

**Show:** the task 3 before/after rows in the results table.

> "That finding is reproducible — there's a script in the repo — and it's filed
> upstream."

## 2:35–2:50 — Close

**Show:** dashboard, then the Paritok dashboard tab with real usage on it.

> "Everything runs on Paritok's hosted GPU. Apache 2.0, three seeded tasks you can
> reproduce in five minutes, and every number in the README came out of the
> harness. Compression bought us sixty-six percent fewer input tokens for free —
> and we found exactly where it stops working."

---

## Notes

- **Don't claim the agent dies without Paritok.** Judges can run this in five
  minutes and see both arms go green. The measured story is strong; a false one
  costs you everything else.
- If the dashboard misbehaves, cut it — the CLI comparison table is the better
  visual anyway.
- Show the Paritok dashboard with real usage at least once; they verify the
  hosted GPU ran by matching your account email.
- Keep the terminal font large. Judges watch these on laptops.

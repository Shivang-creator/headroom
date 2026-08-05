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

## 0:20–0:50 — What Headroom is, and why three arms

> "Headroom is a coding agent that fixes real bugs, plus a harness that measures
> what context compression is worth. Most comparisons would run this on and off.
> That's misleading — because the real alternative to compression isn't sending
> everything, it's *truncating*. Cutting the output to fit and hoping the useful
> part survived. So every task runs three ways."

**Show:** the three-strategy table from the README.

> "Truncate, and you're cheap but blind. Paginate through everything, and you see
> it all at full price. Or paginate *and* compress. The last two are
> byte-identical apart from one line — which URL the request goes to — so any
> difference between them is compression and nothing else."

**Show:** `headroom/config.py`, the `base_url` property.

## 0:50–1:10 — Preflight

> "One thing first, because it's the trap that cost us a night: compression can
> fail completely silently. The request succeeds, the stats counter goes up, and
> nothing was compressed."

**Show:** `.venv/bin/python -m headroom doctor`

> "So there's a preflight. It checks the config values that silently disable
> compression, and it actually round-trips a block through the compressor to
> confirm it comes back smaller. Paritok's own issue tracker asks for a doctor
> command — this is ours."

## 1:10–2:00 — The run

> "Here's a repo with three unrelated bugs across twenty modules. The failing test
> doesn't name the culprit, so the agent has to trace the data path."

**Show:** `.venv/bin/python -m headroom ab tasks/task02_pipeline_triage`

Let the headroom bars climb — that's the visual. Talk over it:

> "Every file read, every test run stays in the conversation. Watch the context
> grow against the ceiling. On the compressed arm, Paritok is squeezing the
> accumulated history in flight before it ever reaches the model."

**Land on the comparison table.**

> "All three solved it. Same three patches, tests green everywhere. But look at
> the cost: ninety-one thousand input tokens to page through it uncompressed,
> forty-four thousand with compression. **Fifty-two percent less, for the same
> evidence and the same fix.** At the proxy, Paritok compressed what it saw by
> eighty-one percent."

## 2:00–2:30 — The honest part, and the fix

> "We set out to show the agent dying without compression and surviving with it.
> The data didn't support that, so we're not claiming it."

**Show:** the "What we actually found" section of the README.

> "A competent agent doesn't overflow 32K as easily as we assumed — it greps
> instead of reading everything. What *does* overflow it is a single huge tool
> result: three hundred failing tests, eighty-two thousand tokens from one pytest
> call. And that turned out to be the case Paritok can't currently help with. We
> measured it: the hosted compressor returns input unchanged above about six
> thousand tokens, silently, while the default config allows fifty thousand."

**Show:** the block-size table, briefly.

> "So Headroom paginates — oversized output gets split into three-thousand-token
> pages that land inside the band where compression actually works. That turns
> the failing task into a solved one. Reproducible script in the repo, filed
> upstream."

## 2:30–2:50 — Close

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

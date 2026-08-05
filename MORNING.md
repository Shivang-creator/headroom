# Handoff — 5 Aug 2026

**Deadline 12:30pm IST.** Everything below is current as of the final build pass.

---

## Do these first (~10 minutes)

### 1. Push the repo — I couldn't

Creating a public GitHub repo is blocked by a permission guardrail (outward-facing
action). Everything is committed locally on `main`. One command:

```bash
cd ~/Projects/headroom
gh repo create headroom --public --source=. --remote=origin \
  --description "A coding agent inside a 32,768-token ceiling. Built with Paritok." --push
```

Then **verify the GitHub About sidebar reads `Apache-2.0`** — the rules call this
out twice as a hard requirement. `LICENSE` is verbatim Apache 2.0 so detection
should be automatic, but check before submitting.

### 2. File the feedback issue (~5 min, independent $50)

Copy [`docs/FEEDBACK_ISSUE.md`](docs/FEEDBACK_ISSUE.md) into a new issue on
Paritok's repo, tag it `hackathon-feedback`. It's four reproducible findings with
suggested fixes — genuinely strong material, and it also feeds the "meaningful
open-source contribution" bonus criterion.

### 3. Sanity-check it runs

```bash
# terminal 1 — leave running
cd ~/Projects/headroom
export PARITOK_API_KEY=... FEATHERLESS_API_KEY=...   # values in ../Hackathon Brainstorming/Ideas/Build with Paritok/.keys.env
.venv/bin/paritok proxy --port 8080 --config-file paritok.yaml \
    --openai-url https://api.featherless.ai/v1/chat/completions

# terminal 2
.venv/bin/python -m headroom doctor                        # should be all ✓ + 1 warning
.venv/bin/python -m pytest tests/ -q                       # 38 passed
.venv/bin/python -m headroom ab tasks/task01_report_mean   # ~2 min, the demo
.venv/bin/python -m headroom serve                         # dashboard :8900
```

---

## The results

All three tasks, three strategies each. Every arm solved every task with the same
patches and green tests.

| Task | truncate | paginate | **paritok** |
|---|---:|---:|---:|
| task01 total input tokens | 30,648 | 27,142 | **13,225** |
| task02 total input tokens | 92,518 | 91,167 | **43,808** |
| task03 total input tokens | 86,739 | 48,901 | **43,054** |

- **Compression at the proxy: 45.3–80.6%** (mean 64.7%)
- **End to end vs the identical uncompressed arm: 12.0–51.9% fewer input tokens** (mean 38.4%)
- Peak context cut by 45–70% on every task

## Read this before you film

**The pitch changed, and you should know why.**

The plan was "the agent dies without Paritok and survives with it." **The data
didn't support that, so we don't claim it.** What we found instead:

1. Compression is a solid, reproducible **cost** win — roughly half the input
   tokens for the same evidence and the same fix.
2. A competent agent **doesn't overflow 32K as easily as assumed** — it greps
   rather than reading everything.
3. **Truncation isn't even cheap.** On task 3 the truncating arm burned 86,739
   tokens against paginate's 48,901 — nearly double — *and* lost evidence. A
   truncated chunk sits in context at full size every subsequent turn; pagination
   spends its tokens once. That surprised me and it's a genuinely useful result.
4. The one case that does overflow is the case **Paritok currently can't help
   with** — the hosted compressor silently returns input verbatim above ~6,000
   tokens. Reproducible via `tools/probe_block_size.py`, identical across two
   runs. Headroom ships the fix (pagination into ~3,100-token pages).

**Don't oversell it in the video.** Judges can run this in five minutes. If you
claim "it dies without Paritok" they'll see every arm go green and stop trusting
everything else. The honest story is strong.

---

## What's done

- ✅ Agent — native tool calls, retry/backoff, pagination, path sandboxing
- ✅ Three strategies (`truncate` / `paginate` / `paritok`) with clean attribution
- ✅ Context governor, SQLite store with schema migration
- ✅ `headroom doctor` preflight — catches silent compression failure
- ✅ **38 tests** over the harness (`pytest tests/ -q`, no network, 0.2s)
- ✅ FastAPI dashboard, three-arm layout, live `/stats`
- ✅ Three seeded tasks, regenerable via `tasks/build_tasks.py`
- ✅ `examples/` — 3 committed transcripts with turn-by-turn token tables
- ✅ README, RUNME, `docs/FINDINGS.md` (6 findings), `docs/SUBMISSION.md` (rule-by-rule compliance)
- ✅ Apache 2.0 LICENSE + required Paritok credit + badge
- ✅ Two reusable probes: `probe_models.py`, `probe_block_size.py`
- ✅ Devpost draft, video script, feedback issue draft

## What's not done — needs you

- ⬜ **Repo not pushed** (blocked — step 1 above)
- ⬜ **Feedback issue not filed** (step 2 above — $50)
- ⬜ **Video not recorded** — script in [`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md), timed to 2:50
- ⬜ **Social post** — `#BuiltWithParitok`, another $50. Angle: "I set out to
  prove compression saves your agent. The data said something more interesting."
- ⚠️ **Dashboard never viewed in a browser** — I have no display. All endpoints
  are verified returning correct data and the HTML/CSS is straightforward, but if
  it looks wrong on camera, film the CLI instead. `headroom ab` output is
  arguably the better visual anyway.

## Known rough edges

- **Featherless capacity is erratic.** If runs start failing with "This model is
  busy", re-run `tools/probe_models.py` and update `DEFAULT_MODEL` in
  `headroom/config.py`. The agent retries 6× with backoff first.
- **The proxy must be running** or everything fails with a clear message.
- **`paritok.yaml` matters more than it looks** — `history.context_window: 32768`
  is load-bearing. `doctor` checks this.
- **Wall time is higher on the compressed arm** (186s vs 80s on task02). That's
  the compression round-trip; it's stated plainly in the README rather than hidden.
- The local token estimator over-reads by ~30%; it's only used for the live
  progress bar, and every recorded number is the API's actual `prompt_tokens`.

## Submission checklist

Full rule-by-rule mapping in [`docs/SUBMISSION.md`](docs/SUBMISSION.md).

- [ ] Repo pushed, public, **Apache-2.0 visible in About**
- [ ] Paritok account email: `shivangshirodkar@gmail.com`
- [ ] Demo video under 3 min, public on YouTube, no copyrighted music
- [ ] Devpost text from `needtouploadondevpost.md`
- [ ] File upload field — `zip -r headroom.zip headroom -x "*/.venv/*" "*/.git/*" "*/runs/*" "*.db"`
- [ ] Feedback issue filed, tagged `hackathon-feedback`
- [ ] Social post tagged `#BuiltWithParitok`

# Morning handoff — 5 Aug 2026

Written ~06:15 IST. **Deadline 12:30pm IST.**

---

## Do these first (about 10 minutes)

### 1. Push the repo — I couldn't

Creating a public GitHub repo was blocked by a permission guardrail (outward-facing
action). Everything is committed locally on `main`. One command:

```bash
cd ~/Projects/headroom
gh repo create headroom --public --source=. --remote=origin \
  --description "A coding agent inside a 32,768-token ceiling. Built with Paritok." --push
```

Then **verify the Apache 2.0 licence shows in the GitHub About panel** — the rules
call this out twice as a hard requirement. `LICENSE` is a verbatim Apache 2.0
text, so GitHub should detect it, but check the sidebar says "Apache-2.0" before
you submit.

### 2. Sanity-check it runs

```bash
# terminal 1 — leave running
cd ~/Projects/headroom
export PARITOK_API_KEY=... FEATHERLESS_API_KEY=...   # values in ../Hackathon Brainstorming/Ideas/Build with Paritok/.keys.env
.venv/bin/paritok proxy --port 8080 --config-file paritok.yaml \
    --openai-url https://api.featherless.ai/v1/chat/completions

# terminal 2
.venv/bin/python -m headroom ab tasks/task01_report_mean   # ~40s, this is the demo
.venv/bin/python -m headroom serve                          # dashboard :8900
```

Full detail in [RUNME.md](RUNME.md).

---

## What the project actually is

A coding agent that fixes real bugs, plus an A/B harness that runs each task
twice — once direct to Featherless, once through the Paritok proxy — and reports
the difference. The agent never knows which arm it's in.

**Headline result: Paritok cut input tokens 47.8–81.6% (mean 66.2%) with
identical outcomes** — same patches applied, tests green in both arms, across
three seeded tasks.

---

## Read this before you film

**The pitch changed overnight, and you should know why.**

The plan was "the agent dies without Paritok and survives with it." **The data
didn't support that, so I didn't claim it.** Three things came out of the runs:

1. Compression is a solid, reproducible **cost** win — 48–82% fewer input tokens,
   same outcome every time.
2. A competent agent **doesn't overflow 32K as easily as we assumed**. It greps
   rather than reading everything, and pipes verbose output through `head`. Our
   217KB, 20-module, three-bug task peaked at 12,116 tokens against a 32,768
   ceiling.
3. The one case that *does* overflow — a single ~82,000-token `pytest` result —
   is the case **Paritok can't currently help with**, because the hosted
   compressor silently returns input verbatim above ~6,000 tokens.

That third point is the most valuable thing we found, it's fully reproducible
(`tools/probe_block_size.py`, identical across two runs), and Headroom ships a
working fix: paginate oversized tool output into ~3,100-token pages that land
inside the band where compression works. That converts task 3 from a hard failure
into a solved run.

**Don't oversell it in the video.** The honest story is stronger than the
fictional one, and judges can run the repo in five minutes. If you claim "it dies
without Paritok" they'll see both arms go green and stop trusting everything else.

---

## What's done

- ✅ Agent (native tool calls, retry/backoff, pagination), governor, A/B runner, SQLite store
- ✅ FastAPI dashboard with side-by-side arms + live `/stats`
- ✅ Three seeded tasks, reproducible via `tasks/build_tasks.py`
- ✅ `examples/` — 5 committed transcripts
- ✅ README, RUNME, `docs/FINDINGS.md` (5 findings, all measured)
- ✅ Apache 2.0 LICENSE + required "Built with Paritok" credit + badge
- ✅ Two measurement tools: `probe_models.py`, `probe_block_size.py`
- ✅ Devpost draft — `../Hackathon Brainstorming/Ideas/Build with Paritok/needtouploadondevpost.md`
- ✅ Video script — `docs/VIDEO_SCRIPT.md`
- ✅ Feedback issue draft — `docs/FEEDBACK_ISSUE.md`

## What's not done

- ❌ **Repo not pushed** (blocked — see step 1 above)
- ❌ **Feedback issue not filed** — copy `docs/FEEDBACK_ISSUE.md` into a new issue
  on Paritok's repo, tag `hackathon-feedback`. This is an independent $50 shot and
  it's genuinely good material. ~5 minutes.
- ❌ **Social post not written** — `#BuiltWithParitok`, another $50 shot. The
  "we tried to prove X and the data said Y" angle is the post.
- ✅ **Dashboard tested** — all four endpoints verified returning correct data,
  no errors in the log. I have not viewed it in a browser (no display), so the
  CSS is unverified visually. If it looks wrong on camera, film the CLI instead;
  `headroom ab` output is arguably the better visual anyway.
- ⚠️ **Task 3 has three run-pairs in the results table**, including the
  superseded pre-pagination one. It's labelled and I kept it deliberately since
  it's the evidence for the size-ceiling finding. Delete `headroom.db` and re-run
  if you'd rather have a clean table.

## Known rough edges

- **Featherless capacity is erratic.** `GLM-4.7-Flash` measured 50.3s p50 with a
  1-in-3 failure rate; `GLM-5.1` measured 2.7s. If runs start failing, re-run
  `tools/probe_models.py` and update `DEFAULT_MODEL` in `headroom/config.py`.
- **The proxy must be running or everything fails** with a clear error message.
- **`paritok.yaml` matters more than it looks.** `history.context_window: 32768`
  is load-bearing — at the default `200000` compression never fires.
- The local token estimator over-reads by ~25% (it's only used for the live
  progress bar; every recorded number is the API's actual `prompt_tokens`).

## Submission checklist

- [ ] Repo pushed, public, Apache-2.0 visible in About
- [ ] Paritok account email on the form: `shivangshirodkar@gmail.com`
- [ ] Demo video under 3 min, public on YouTube
- [ ] Devpost text from `needtouploadondevpost.md`
- [ ] File upload field — zip the repo, or export `docs/FINDINGS.md` to PDF
- [ ] Feedback issue filed and tagged `hackathon-feedback`
- [ ] Social post tagged `#BuiltWithParitok`

# Reproducing the results

Five minutes, three terminals. Every number in the README came from these commands.

## 0. Prerequisites

Python 3.10+, a [Paritok API key](https://www.paritok.com/dashboard), and a
[Featherless](https://featherless.ai) API key.

```bash
cd ~/Projects/headroom
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

export PARITOK_API_KEY=pk_live_...
export FEATHERLESS_API_KEY=rc_...
```

Check the hosted GPU is up before anything else — if this says
`gpu_available: false`, nothing downstream will work:

```bash
curl -s https://www.paritok.com/api/test -H "Authorization: Bearer $PARITOK_API_KEY"
# {"gpu_available":true,"message":"GPU server online (RunPod serverless)."}
```

---

## 1. Start the proxy — terminal 1, leave it running

```bash
cd ~/Projects/headroom
.venv/bin/paritok proxy --port 8080 --config-file paritok.yaml \
    --openai-url https://api.featherless.ai/v1/chat/completions
```

Wait for `Uvicorn running on http://127.0.0.1:8080`. **This terminal must stay
open for the whole session.**

> The `--openai-url` is the full endpoint, not a base host. Featherless's path is
> `/v1/chat/completions`, and Paritok only appends `/v1/chat/completions` when
> given a bare host — passing `https://api.featherless.ai` yields a 404.

Confirm:

```bash
curl -s http://127.0.0.1:8080/stats
```

---

## 2. Run the comparison — terminal 2

```bash
cd ~/Projects/headroom
export PARITOK_API_KEY=... FEATHERLESS_API_KEY=...

.venv/bin/python -m headroom ab tasks/task02_pipeline_triage
```

Each task runs twice — straight to Featherless, then through the proxy — against
a fresh copy of the repo each time. Roughly 60–90 seconds per arm.

The three seeded tasks, in increasing order of context pressure:

```bash
.venv/bin/python -m headroom ab tasks/task01_report_mean       # 1 bug,  ~9 turns
.venv/bin/python -m headroom ab tasks/task02_pipeline_triage   # 3 bugs, ~15 turns
.venv/bin/python -m headroom ab tasks/task03_verbose_suite     # 306 failing cases
```

---

## 3. Dashboard — terminal 3

```bash
cd ~/Projects/headroom
.venv/bin/python -m headroom serve
# → http://127.0.0.1:8900
```

Side-by-side arms, per-turn context growth against the 32,768 ceiling, and live
compression totals from the proxy.

---

## Other commands

```bash
.venv/bin/python -m headroom stats     # live proxy compression totals
.venv/bin/python -m headroom tasks     # list the seeded tasks
.venv/bin/python -m headroom agent tasks/task01_report_mean --paritok  # one arm
.venv/bin/python -m headroom export    # refresh README table + examples/
.venv/bin/python tools/probe_models.py # re-pick a usable upstream model
```

---

## If something breaks

**`The Paritok proxy is not answering at http://127.0.0.1:8080`** — terminal 1
isn't running, or it crashed. Check it.

**`This model is busy, please try again later`** — Featherless capacity. The
agent retries six times with exponential backoff; if it still fails, re-run
`tools/probe_models.py` and update `DEFAULT_MODEL` in
[`headroom/config.py`](headroom/config.py). Model availability moves hour to hour —
`GLM-4.7-Flash` measured 50.3 s p50 with a 1-in-3 failure rate while `GLM-5.1`
measured 2.7 s, and the catalogue gives you no way to know that in advance.

**Compression reports 0% saved** — check `paritok.yaml` has
`history.context_window: 32768`. At the default `200000`, compression never
triggers against a 32K upstream. See [docs/FINDINGS.md](docs/FINDINGS.md) §2.

**`context_length_exceeded` on the Paritok-ON arm** — that's a real result, not a
bug. Record it.

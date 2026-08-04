# What we measured about Paritok

Everything here came out of building [Headroom](../README.md) against Paritok
1.2.8 on the hosted GPU server, between 01:00 and 08:00 IST on 5 August 2026.
Numbers are from real runs, not estimates. Where we got something wrong first,
that's recorded too — the wrong turns were the informative part.

Setup under test:

```
agent → paritok proxy (:8080) → Featherless → zai-org/GLM-5.1
          └→ paritok hosted GPU (paritok-4b-v1, RunPod serverless)
```

---

## 1. Paritok only compresses native tool calls

**This is the single most important thing we learned, and it nearly sank the project.**

Paritok's open issues describe real problems with tool calling — [#20][20]
(client silently destroys tool results), [#27][27] (non-MCP tools dropped),
[#22][22] (Gemini rejects synthetic tool calls). So our first design
deliberately *avoided* native tool calls: the model emitted JSON actions inside
plain message content, and the harness parsed them. Observations went back as
ordinary user messages. The reasoning was that this sidesteps every one of those
bugs while still producing `file_read` / `bash_command` / `log_output` shaped
text.

It produced **zero compression.**

| Conversation form | Input tokens | After Paritok | Saved |
|---|---:|---:|---:|
| Plain text in user messages | 35,627 | 35,627 | **0%** |
| Identical content, native `tool_calls` + `role:"tool"` | 35,379 | 646 | **98.2%** |

Same content. Same token count. Same query. The only difference is the message
envelope. Paritok segments compressible blocks out of `role:"tool"` messages;
anything it can't recognise as a tool result is forwarded untouched, silently,
with `/stats` reporting `input_tokens_original: 0` while `total_requests`
increments.

**Why this matters beyond us:** a large fraction of agent frameworks use text
protocols rather than native function calling — ReAct implementations, most
prompt-based scaffolds, anything targeting models without reliable tool support.
For all of them Paritok is currently a no-op, and nothing in the docs or the
`/stats` output says so.

**Suggestion:** warn at proxy startup, or in `/stats`, when a request contained
no compressible blocks. A `blocks_found: 0` counter alongside `total_requests`
would have saved us three hours.

---

## 2. `history.context_window` must match your real ceiling, not the model's

`paritok init` writes:

```yaml
history:
  context_threshold: 0.8
  context_window: 200000
```

History compression triggers at `context_threshold × context_window` — 160,000
tokens with the defaults. Our upstream ceiling is **32,768**, so that threshold
is not merely wrong, it is *unreachable*: every request is rejected by the
provider long before Paritok decides to compress anything.

Setting `context_window: 32768` is what made the project work at all.

This will bite anyone pointing Paritok at a small-context or plan-capped
upstream, which is most of the cheap tier — Featherless caps every model on the
$25/mo plan at 32,768 regardless of native context (GLM-5.1's native window is
202,752). The default silently assumes a frontier-model context budget.

**Suggestion:** either derive the window from the upstream model where possible,
or emit a startup warning when `context_window` is more than ~2× the largest
prompt actually observed.

---

## 3. Empty compressions are usually correct — and indistinguishable from failure

Issue [#20][20] reports the hosted GPU returning empty strings. We reproduced it
immediately, then found the reported diagnosis is mostly wrong in an interesting
way.

The compressor is **query-conditioned**: each block is compressed relative to the
most recent user turn. Our first probe asked *"Reply with exactly the word DONE"*
against nine turns of unrelated stack traces and source. Every block compressed
to empty — which is *correct*. Nothing in that context was relevant to that
question.

Re-running with a query that actually referenced the content:

```
query:   "What magic constant does compute_checksum use?"
block:   1,782 tokens of source, with the needle buried in module 4 of 9
result:  31 tokens — "def compute_checksum(buf): return 0xDEADBEEF ^ len(buf)"
```

Exactly the right function, nothing else. That's the system working well.

**The actual bug is the ambiguity.** A correct "nothing here was relevant" and a
genuine GPU failure both produce `compressed: ""`, both become a `[REF:id]` stub,
and neither is distinguishable by the client. We hit real empties on ~4% of
blocks during overnight runs and still cannot tell which were which.

Additionally, `/api/compress` returns HTTP 200 with `{"compressed": ""}` in about
1.5–2.4 s — far too fast for 4B inference on a 9 KB input, which suggests some
empties are a fast path rather than a considered result.

**Suggestion:** return a reason alongside the result — `{"compressed": "",
"reason": "no_relevant_content" | "model_error" | "below_threshold"}`. This is a
small change that turns an unexplainable behaviour into an observable one.

---

## 4. Smaller things worth fixing

**`/stats` counts requests it didn't compress.** After a request with no
compressible blocks: `{"total_requests": 1, "input_tokens_original": 0,
"compression_ratio": 0.0}`. `total_requests` implies work was done. A separate
`requests_compressed` counter would make a no-op visible.

**Empty request body → HTTP 500.** `POST /v1/chat/completions` with an empty body
raises an unhandled `json.JSONDecodeError` out of `proxy/server.py:390` and
returns `Internal Server Error`. Should be a 400.

**`/api/compress` field name is undocumented.** It requires `content`; sending
`text` returns `{"error": "Missing 'content' to compress."}`. The README documents
the proxy path but not this endpoint's contract, and it's the natural thing to
reach for when debugging whether the GPU is alive.

**Cold-start latency is real but acceptable.** First hosted-GPU call after idle:
~6.7 s. Warm: 1.5–2.4 s for blocks under 2,000 tokens. On a 15-turn agent run the
compression overhead was consistently a small fraction of upstream inference
time — in our task-02 run, total wall time went from 65.7 s (off) to 80.7 s (on),
a 23% increase to cut input tokens by 81.6%.

---

## 5. What compression cost us in quality

The honest question isn't whether compression saves tokens — it obviously does —
but whether the agent still solves the problem. Across our seeded tasks, both
arms reached identical outcomes:

| Task | Arm | Turns | Peak prompt tokens | Patches | Tests pass |
|---|---|---:|---:|---:|:--:|
| task01_report_mean | off | 9 | 7,013 | 1 | ✅ |
| task01_report_mean | on | 10 | 2,100 | 1 | ✅ |
| task02_pipeline_triage | off | 15 | 12,116 | 3 | ✅ |
| task02_pipeline_triage | on | 16 | 5,146 | 3 | ✅ |

Compression cost roughly one extra turn per task — consistent with the agent
occasionally re-reading something that had been compressed away — while cutting
peak context by 58–70% and total input tokens by ~81%. For a workload that fits
in the window anyway, that is a straight cost win with a small latency tax.

**A caveat we want to state plainly:** tasks 1 and 2 both *fit* under the ceiling
without compression. A competent agent greps rather than reading exhaustively,
and never came close to 32,768 tokens. Breadth of codebase alone does not
overflow a context window. Task 3 was built specifically to test the case where a
single tool result (306 failing parameterised tests, ~82,000 tokens from one
`pytest` call) exceeds the window on its own — which is what CI triage actually
looks like.

[20]: https://github.com/Paritok-official/paritok-4b-v1/issues/20
[22]: https://github.com/Paritok-official/paritok-4b-v1/issues/22
[27]: https://github.com/Paritok-official/paritok-4b-v1/issues/27

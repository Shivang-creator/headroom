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

## 4. ⚠️ RETRACTED: "the compressor passes through blocks above ~6,000 tokens"

> **This section originally reported a hard block-size limit. That conclusion was
> wrong.** It is preserved below, followed by the correction, because how we got it
> wrong is more useful than the claim itself.
>
> **What actually happened:** on 5 Aug the hosted GPU was intermittently not
> compressing (see [issue #30][i30]). We swept block sizes in *ascending order*,
> twice, and both times the outage window happened to cover the tail of the sweep.
> Ascending order plus a time-varying fault produces a perfect size correlation.
> We reported it as a size guard.
>
> [@shlok-temp pushed back][c] on the issue: *"This might not be an issue with the
> number of tokens. For some moments the GPU compression is down and the same
> response is sent back."* Re-tested 9 Aug:
>
> **(a)** The identical probe now compresses everything — 6,006 → 149, 16,022 → 376,
> 40,055 → 990. The cliff is gone.
>
> **(b)** [`probe_size_vs_outage.py`](../tools/probe_size_vs_outage.py) alternates
> 3,000- and 8,000-token blocks so both sizes sit in the same time windows. Under a
> size effect every adjacent pair must disagree. Result: **16/16 compressed, 0/8
> pairs disagreed.**
>
> **The methodological lesson:** we varied one parameter monotonically against a
> backend that varies over time, and never separated the two. Interleaving is the
> control, it takes 90 seconds, and we should have run it before writing anything
> down. Two consecutive runs agreeing felt like replication; it wasn't — it was the
> same confound twice.
>
> **What survives:** the *observation* (HTTP 200 + `gpu_available: true` + verbatim
> body + `below_refusal_threshold` downstream) was real and is a genuine reporting
> bug — see §4b. What we retract is the attribution to block size, and the claim
> that `compression.max_tokens: 50000` is set too high.
>
> [c]: https://github.com/Paritok-official/paritok-4b-v1/issues/31#issuecomment-5230270965
> [i30]: https://github.com/Paritok-official/paritok-4b-v1/issues/30

<details>
<summary><b>The original (incorrect) section, preserved</b></summary>

**Reproducible: [`tools/probe_block_size.py`](../tools/probe_block_size.py).**

We built a task whose failing test suite emits ~82,000 tokens from a single
`pytest` call — the best possible case for a compressor, since the output is 306
near-identical parameterised failures. Paritok skipped it:

```json
{"skipped": true, "reason": "below_refusal_threshold", "original_tokens": 37620}
```

"Below refusal threshold" means compression saved less than
`compression.refusal_threshold` (5%), so the original was kept. But highly
repetitive text failing to compress at all is not a content problem. Probing
`/api/compress` directly with the same shape of content at increasing sizes,
**identical results across two runs**:

| Input tokens | Output tokens | Ratio | Latency |
|---:|---:|---:|---:|
| 1,032 | 1,032 | 1.00 | 26–27 s |
| **2,064** | **68** | **0.033** | 2.9 s |
| **4,001** | **74** | **0.019** | 3.1 s |
| 6,006 | 6,006 | 1.00 | 2.4 s |
| 8,008 | 8,008 | 1.00 | 1.1 s |
| 12,018 | 12,018 | 1.00 | 1.2 s |
| 16,022 | 16,022 | 1.00 | 1.4 s |
| 24,045 | 24,045 | 1.00 | 1.4 s |
| 32,056 | 32,056 | 1.00 | 1.5 s |
| 40,055 | 40,055 | 1.00 | 1.8 s |

Inside a narrow band — roughly 2,000–4,000 tokens — compression is excellent
(50× reduction). Above about 6,000 tokens the endpoint **returns the input
verbatim**, in 1.1–2.4 seconds. That is far too fast for 4B inference over
20,000+ tokens, which suggests a size guard returning early rather than a model
producing a poor result.

Three things make this hard to notice:

1. It returns HTTP 200 with a plausible-looking body.
2. `compression.max_tokens` defaults to **50,000** — an order of magnitude above
   where compression actually stops working — so users will configure well past
   the real limit and see no error.
3. Downstream it surfaces as `below_refusal_threshold`, which reads like a
   considered decision about content rather than a size cutoff.

The 1,032-token row is separately odd: also uncompressed, but taking 26–27 s in
both runs, versus 1–3 s everywhere else.

**Why it matters:** the single biggest blocks in an agent's context — a full test
run, a long build log, a large file read — are exactly the ones that blow the
window, and exactly the ones this silently declines to compress.

**Suggestion:** (a) document the working range; (b) default `max_tokens` to it
rather than 50,000; (c) return `{"skipped": true, "reason": "input_too_large"}`
instead of echoing the input, so callers can chunk and retry.

**Workaround, which Headroom implements:** paginate oversized tool results into
~3,100-token pages before they enter the conversation
([`headroom/tools.py`](../headroom/tools.py), `PAGE_CHARS`). One 82,000-token
block is uncompressible; twenty-seven 3,100-token pages sit inside the working
band. This is a reasonable thing for an agent to do anyway, and it converts the
worst case into the best one.

</details>

## 4b. What actually survives: a silent no-op you cannot detect

Strip the wrong diagnosis and a real bug remains, and it is arguably worse than
the one we thought we'd found.

While the hosted GPU was not compressing, `/api/compress` returned:

- **HTTP 200**
- **`gpu_available: true`** — the flag that exists to tell you otherwise
- a body of the right shape, just uncompressed

and the client surfaced it as `{"skipped": true, "reason": "below_refusal_threshold"}`
— which reads as a decision about *content*, not about the backend.

The evidence that this is hard to catch is us. We were actively probing the
endpoint with a purpose-built script, we distrusted the result enough to run it
twice, and we still reached the wrong conclusion. A normal user sees
`tokens_saved: 0` and assumes their content wasn't compressible.

**Suggested fixes, in priority order:**

1. Return a `reason` that distinguishes `no_relevant_content` /
   `backend_unavailable` / `below_threshold`. One field removes the entire class
   of confusion.
2. Make `/api/compress` set `gpu_available: false` when it isn't compressing. It
   reported `true` throughout our outage — which is exactly [issue #30][i30]'s point.
3. Add `requests_compressed` alongside `total_requests` in `/stats`, so a silent
   no-op is visible without instrumenting anything.

Pagination stays in Headroom regardless. It is no longer needed to dodge a size
limit that doesn't exist, but it's still the right shape for an agent: it bounds
the blast radius of any single tool result, and it keeps blocks in the range
where compression measured best.

---

## 5. Smaller things worth fixing

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

## 7. Agents self-limit, and you cannot easily stop them

This is the finding that killed our original pitch, and we tried hard to falsify
it before accepting it.

To claim compression is a *capability* unlock we needed a workload where the
uncompressed agent exhausts the window and the compressed one doesn't. Three
attempts:

1. **A wide codebase** (task 2 — 217 KB, 20 modules, 3 unrelated bugs). The agent
   grepped, read four files, and finished at 11,994 peak tokens. Breadth doesn't
   fill a window.
2. **A huge single tool result** (task 3 — 306 failing tests, ~82,000 tokens from
   one `pytest`). The agent piped it through `head`. When we forced the full
   result in, *both* arms died — because the compressor passes through blocks
   that large (§4).
3. **An explicit instruction to audit everything** (task 4 — 462 failing cases,
   41 pages, and a brief that says in three separate places to call `next_page`
   until no pages remain, not to sample, and not to stop early).

Attempt 3 is the interesting one. **The agent stopped after roughly ten pages
anyway** — about a quarter of the output — formed a hypothesis, and went to fix
the bug. It was *right*, and the fix was correct. But it did not do what it was
told, and no amount of instruction-tightening reliably changed that.

The practical conclusion: a competent agent performs a great deal of its own
context management, and it does so robustly enough to resist being told
otherwise. Before attributing a context saving to any tool, measure how much the
agent was already saving on its own. That is what the `truncate` / `paginate`
comparison is for.

Where compression clearly does help during that paging workload is holding
context *flat*. On task 4 the compressed arm sat around 2,000 billed tokens
while sending 11,497 — 83% compressed — as it paged, where the uncompressed arm
grew monotonically. Compression doesn't make the agent read more; it makes what
it did read much cheaper to keep.

---

## 6. Why we compare three strategies, not two

An on/off comparison quietly assumes the alternative to compression is "send
everything uncompressed." It isn't. The real alternative — what most agents do
today — is **truncation**: cut the oversized result to fit and hope the useful
part survived.

Measuring only on/off therefore overstates compression's value, because it
credits compression for savings that truncation would also deliver, and hides
what truncation *costs*. So every task runs three ways:

| Arm | Sees all the evidence? | Context cost |
|---|:--:|---|
| `truncate` | ✗ discards the tail | low |
| `paginate` | ✓ | full price |
| `paritok` | ✓ | ~1/5 |

The two comparisons answer different questions:

- **`truncate` vs `paginate`** — what does it cost to see everything?
- **`paginate` vs `paritok`** — what is compression worth? These two arms are
  byte-identical apart from `base_url`, so the difference is attributable to
  compression and nothing else.

That second pairing is the number we quote, and it is deliberately the
conservative one: it compares compression against an agent that is already
handling large output well, not against a straw man.

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

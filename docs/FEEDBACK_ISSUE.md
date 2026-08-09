# Feedback filed upstream

**Filed as [issue #31](https://github.com/Paritok-official/paritok-4b-v1/issues/31)** on
`Paritok-official/paritok-4b-v1`, 5 Aug 2026. Reproduced below for the record.

> ## ⚠️ Finding 1 was wrong and has been retracted
>
> §1 below reports a ~6,000-token block-size limit. **That conclusion was incorrect.**
> [@shlok-temp corrected it][c] on the issue: the passthrough was the hosted GPU
> intermittently not compressing ([#30][i30]), not a size guard.
>
> Re-tested 9 Aug. The identical probe now compresses everything up to 40,055
> tokens, and an interleaved control — 3,000- and 8,000-token blocks alternating,
> so both sizes sit in the same time windows — compressed **16/16, with 0/8 pairs
> disagreeing**. Under a size effect every pair must disagree.
>
> The error: we swept sizes in ascending order, twice, against a time-varying
> fault. That manufactures a perfect size correlation, and two runs agreeing felt
> like replication when it was the same confound twice.
>
> **The observation survives, the attribution doesn't.** While not compressing,
> `/api/compress` returns HTTP 200, `gpu_available: true`, and a plausible body,
> and the client reports `below_refusal_threshold` — which reads as a decision
> about content. That ambiguity is the real bug, and our own misdiagnosis is the
> evidence for it. See [FINDINGS §4 and §4b](FINDINGS.md).
>
> §2, §3 and §4 below are unaffected and were re-verified.
>
> The original text is kept intact rather than edited away.
>
> [c]: https://github.com/Paritok-official/paritok-4b-v1/issues/31#issuecomment-5230270965
> [i30]: https://github.com/Paritok-official/paritok-4b-v1/issues/30

---

Built [Headroom](https://github.com/Shivang-creator/headroom) for the hackathon —
a coding agent plus a harness that runs each task under three strategies for
oversized tool output — truncate, paginate, and paginate-through-the-proxy.
Paritok worked well: **45–81% compression at the proxy, and 12–52% fewer input
tokens end to end** versus an identical uncompressed arm, with the same fix and
green tests on every task. These are the four things that cost me real debugging
time, in rough order of impact.

## 1. `/api/compress` returns the input verbatim above ~6,000 tokens, silently

Reproducible with [`tools/probe_block_size.py`](https://github.com/Shivang-creator/headroom/blob/main/tools/probe_block_size.py).
**Identical results across two consecutive runs.** Content is repetitive pytest
failure output — close to the best possible case for a compressor.

| Input tokens | Output tokens | Ratio | Latency |
|---:|---:|---:|---:|
| 1,032 | 1,032 | 1.00 | 26–27 s |
| **2,064** | **68** | **0.033** | 2.9 s |
| **4,001** | **74** | **0.019** | 3.1 s |
| 6,006 | 6,006 | 1.00 | 2.4 s |
| 8,008 | 8,008 | 1.00 | 1.1 s |
| 16,022 | 16,022 | 1.00 | 1.4 s |
| 32,056 | 32,056 | 1.00 | 1.5 s |
| 40,055 | 40,055 | 1.00 | 1.8 s |

Between roughly 2k and 4k tokens compression is excellent — 50× reduction. Above
about 6k the endpoint returns the input unchanged in 1.1–2.4s, which is too fast
for 4B inference over 20k+ tokens, so this looks like an early-return size guard
rather than a model producing a poor result.

Three things make it hard to spot:

- HTTP 200 with a plausible body.
- `compression.max_tokens` defaults to **50,000** — an order of magnitude above
  where compression actually stops working — so users configure well past the
  real limit and see no error.
- Downstream it surfaces as `{"skipped": true, "reason": "below_refusal_threshold"}`,
  which reads like a decision about content rather than about size.

This matters because the largest blocks in an agent's context — a full test run,
a long build log, a big file read — are the ones that blow the window, and are
exactly what this declines to compress. My worst case was a 306-failure pytest
run: 37,620 tokens in one block, skipped, request rejected by the upstream.

**Suggested fix:** document the working range; default `max_tokens` to it; and
return `{"skipped": true, "reason": "input_too_large", "max_supported": N}`
instead of echoing the input, so callers can chunk and retry. I worked around it
by paginating tool output into ~3,100-token pages, which converted that task from
a hard failure into a solved run — but the client can only do that if it knows
the limit exists.

Separately, the 1,032-token row is also uncompressed and took 26–27s in both
runs, versus 1–3s everywhere else. Might be an unrelated slow path worth a look.

## 2. Compression only fires on native `tool_calls` — a text protocol gets 0%

I initially built the agent with a text protocol (model emits JSON actions inside
message content, harness parses them), specifically to route around the
tool-calling issues in #20/#22/#27. Same content, same token count, same query:

| Conversation form | Input | After Paritok | Saved |
|---|---:|---:|---:|
| Plain text in user messages | 35,627 | 35,627 | **0%** |
| Native `tool_calls` + `role:"tool"` | 35,379 | 646 | **98.2%** |

Understandable given the training data, but nothing warns you. `/stats` reports
`total_requests: 1` alongside `input_tokens_original: 0`, which looks like it
worked. A large share of agent frameworks use text protocols — for all of them
Paritok is currently a silent no-op.

**Suggested fix:** a `blocks_found` counter in `/stats`, or a one-time startup
warning when a request yields no compressible blocks.

## 3. `history.context_window` defaults to 200000, which breaks small-context upstreams

History compression triggers at `context_threshold × context_window` = 160,000
tokens by default. My upstream ceiling is 32,768 (Featherless caps every model on
the $25/mo plan regardless of native context — GLM-5.1's native window is
202,752). That threshold is unreachable, so compression never fired and every
request went upstream at full size until I set `context_window: 32768`.

This will affect anyone pointing Paritok at a plan-capped or small-context
provider, which is much of the cheap tier.

**Suggested fix:** warn at startup when `context_window` is far above the largest
prompt actually observed, or derive it from the upstream model where possible.

## 4. Smaller things

- **Empty compressions are ambiguous.** The compressor is query-conditioned, so
  an empty result is often *correct* — nothing in the block was relevant to the
  current query. I verified the good case: a needle planted in module 4 of 9
  survived compression from 1,782 tokens to 31 (`def compute_checksum(buf):
  return 0xDEADBEEF ^ len(buf)`), exactly the right function. But a genuine GPU
  failure produces the same empty string, and both become a `[REF:id]` stub with
  no way to distinguish them. Returning `reason` would fix this too, and I think
  this is the real content of #20.
- **Empty request body → HTTP 500.** `POST /v1/chat/completions` with an empty
  body raises an unhandled `json.JSONDecodeError` from `proxy/server.py:390`.
  Should be a 400.
- **`/api/compress` field name is undocumented.** It requires `content`; sending
  `text` gives `{"error": "Missing 'content' to compress."}`. It's the natural
  endpoint to hit when checking whether the GPU is alive, and the README only
  covers the proxy path.
- **`/stats` counts requests it didn't compress.** A separate `requests_compressed`
  would make a no-op visible.

## What worked well

Worth saying: on accumulated multi-turn agent context the compression quality was
genuinely impressive. On a 17-turn three-bug debugging session the proxy
compressed 95,969 → 18,612 tokens (80.6%), and the agent reached the identical
fix with the same three patches and green tests. End to end that arm used 43,808
input tokens against 91,167 for the uncompressed control — 51.9% less for the
same evidence. Cold start ~6.7s, warm 1.5–2.4s. The `--openai-url` passthrough
made pointing at a non-obvious provider a one-liner.

Environment: paritok 1.2.8, hosted GPU (RunPod serverless), macOS 15.5 arm64,
Python 3.13, upstream `zai-org/GLM-5.1` via Featherless.

# Submission compliance

Every stated requirement and judging criterion from the hackathon page, mapped to
where it's satisfied. Anything still open is marked ⬜ and needs a human.

---

## Hard requirements — "WHAT TO SUBMIT"

| # | Requirement | Status | Evidence |
|---|---|:--:|---|
| 1 | **Project URL** — publicly accessible, lets judges easily test | ⬜ | Repo + [RUNME.md](../RUNME.md). The rules accept "your repo with clear setup instructions". **Needs `gh repo create` — see [MORNING.md](../MORNING.md).** |
| 2 | **Public code repository** | ⬜ | Committed locally; needs pushing |
| 2a | Contains all source, assets, full run instructions | ✅ | [RUNME.md](../RUNME.md) — five numbered steps, three terminals |
| 2b | Public **and Apache 2.0 licence detectable in the About section** | ⬜ | [LICENSE](../LICENSE) is verbatim Apache 2.0 so GitHub will detect it — **verify the sidebar reads `Apache-2.0` after pushing** |
| 2c | Credits Paritok with a link in the README | ✅ | Line 8 of [README](../README.md): `Built with [Paritok](...)` |
| 2d | *(Optional)* Paritok badge at the top of the README | ✅ | Line 1 of [README](../README.md) |
| 3 | **Paritok account email** | ✅ | `shivangshirodkar@gmail.com` — hosted-GPU usage is on the dashboard for this key |
| 4 | **Text description** — what it solves, where the hosted GPU mattered, technologies | ✅ | Drafted in `needtouploadondevpost.md` |
| 5 | **Demo video under 3 min**, public on YouTube/Vimeo, no copyrighted music | ⬜ | Script + shot list in [VIDEO_SCRIPT.md](VIDEO_SCRIPT.md), timed to 2:50. **Needs recording.** |
| 6 | *(Optional)* Sample outputs in an `examples/` folder | ✅ | [`examples/`](../examples/) — committed transcripts, turn-by-turn token tables |
| 7 | *(Optional)* Social post tagged `#BuiltWithParitok` | ⬜ | Angle suggested in `needtouploadondevpost.md` |
| — | *(Bonus)* Feedback as a GitHub issue tagged `hackathon-feedback` | ⬜ | Full draft ready in [FEEDBACK_ISSUE.md](FEEDBACK_ISSUE.md) — **needs filing** |

## Rules — "PROJECT AND SUBMISSION REQUIREMENTS"

| Requirement | Status | Note |
|---|:--:|---|
| Paritok integration set up **during the submission period** and plays a **meaningful role** | ✅ | Built from zero on 5 Aug 2026. Paritok isn't decoration — the whole harness exists to measure it, and `paritok.yaml` tuning is load-bearing |
| Repo public, Apache 2.0, credits Paritok with a link back | ⬜ | See 2b/2c above |
| Original work | ✅ | All code written for this hackathon |
| No unlawful, infringing, harmful or offensive content | ✅ | — |
| Demo video free of copyrighted music / third-party trademarks | ✅ | Script specifies no music |
| Above age of majority; entering as an individual | ✅ | — |

---

## Judging criteria

### 1. Use of Paritok
> *"How meaningfully does the project use Paritok to cut token usage? Strong
> submissions don't just add it — they show a real, measured reduction inside a
> genuine workflow."*

- Measured reduction inside a real multi-turn debugging workflow, not a synthetic
  prompt: **the `paritok` arm uses ~50% fewer input tokens end-to-end than the
  identical `paginate` arm**, which differs only by `base_url`.
- Proxy-level compression measured separately at **45–81%** (mean 67%).
- Four seeded tasks a judge can reproduce in five minutes; 12 runs, all green.
- Every number is emitted by the harness and exported to the README — no
  hand-typed figures.
- We also mapped where Paritok *stops* working (§4 of FINDINGS) and shipped a fix.

### 2. Technical Execution
> *"Quality of implementation, robustness, and whether the project actually works
> end-to-end… built well enough for someone else to run and rely on."*

- **38 tests** over the harness ([`tests/`](../tests/)), no network needed, ~0.2s.
- `headroom doctor` preflight catches the silent-failure modes before you trust a number.
- Retry with exponential backoff for Featherless capacity errors.
- Path sandboxing on every tool; `apply_patch` refuses ambiguous matches.
- Ground-truth verification: the harness runs the tests itself rather than
  believing the agent. (An earlier version read `tail`'s exit code and reported
  every run green — caught, fixed, and now regression-tested.)
- Schema migration so an existing database survives an upgrade.

### 3. Originality
> *"Go beyond wrapping Paritok around a hello-world app."*

- **Three-arm methodology** — truncate / paginate / compress. Most submissions
  will compare on/off, which overstates the result by ignoring that the real
  alternative is truncation.
- **Boundary mapping, then a public retraction.** We reported a ~6,000-token
  passthrough cliff, were corrected by another participant, re-tested with an
  interleaved control, found we were wrong, and said so on the issue and in the
  README. The surviving finding — a silent no-op that reports `gpu_available:
  true` — is the more useful one.
- The project is an *instrument*, not a wrapper: it would produce a useful result
  even if the answer had been "compression doesn't help."

### 4. Real-World Usefulness
> *"Would a real developer, team, or company running AI at scale see clear value?"*

- `headroom doctor` answers a question every Paritok adopter has on day one —
  *is compression actually firing?* — and directly addresses their open
  [issue #29](https://github.com/Paritok-official/paritok-4b-v1/issues/29).
- The three config traps in FINDINGS §1–3 are load-bearing for anyone pointing
  Paritok at a plan-capped or small-context provider.
- The pagination pattern is portable to any agent, independent of this repo.
- `tools/probe_models.py` is generally useful: the Featherless catalogue gives no
  signal about which models are actually reachable or emit native tool calls.

### 5. Submission Quality
> *"A judge should be able to understand what the project does, why it matters,
> and find clear setup instructions."*

- [README](../README.md) leads with the finding, including the one that
  contradicted our hypothesis.
- [RUNME.md](../RUNME.md) — exact reproduction, plus a troubleshooting section.
- [FINDINGS.md](FINDINGS.md) — seven sections, every claim backed by a number.
- [`examples/`](../examples/) — judges can evaluate without running anything.

### 6. Bonus — Meaningful Open-Source Contribution
> *"Bug reports, feature ideas, documentation, or well-researched proposals."*

- [FEEDBACK_ISSUE.md](FEEDBACK_ISSUE.md): four findings, each with reproduction
  steps and a concrete suggested fix, plus two reusable probe scripts.
- ⬜ **Still needs filing** — this is also an independent $50 prize.

---

## Honest self-assessment

**Strongest:** Use of Paritok, Originality, and the open-source contribution. The
measurement is real, the methodology is more careful than an on/off comparison,
and the size-ceiling finding is genuinely new information for the maintainers.

**Weakest:** we cannot claim compression is a *capability unlock* on this
evidence. And one headline finding was wrong: we attributed a passthrough to
block size when it was a backend outage, because we swept sizes monotonically
against a time-varying fault and never ran the interleaved control. Another
participant caught it, we re-tested, and we retracted it publicly rather than
editing it away.

That is a real error and we are not dressing it up. What we would point to is
what happened next: the correction is on the issue, in the README, and in
FINDINGS §4 with the original text preserved, plus a script that separates the
two hypotheses in 90 seconds. A judge who runs this repo will find the claims
match the output.

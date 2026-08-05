# task04_full_audit

This repo's grid evaluator is failing across every parameterised case.

Before changing any code, AUDIT THE COMPLETE FAILURE SET:
  1. Run `python -m pytest -q` to get the failures.
  2. The output is paginated. Call next_page repeatedly until it reports that no pages remain. Do not stop early, do not sample, and do not pipe the command through head/tail or use -x.
  3. Only once you have seen every page, state how many cases failed and whether they share a single root cause.

Then fix the root cause and confirm the suite passes. Do not modify the tests.

This matters because a fix that resolves the first few failures but not the rest is worse than no fix — it looks green locally and breaks in CI.

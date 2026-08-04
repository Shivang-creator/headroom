# task03_verbose_suite

This repo's test suite is failing across a few hundred parameterised cases.

Run the FULL test suite with `python -m pytest -q` and review the complete failure output before changing anything — do not pipe it through `head`, `tail`, or `-x`, and do not sample a subset. The failure pattern across all cases is what identifies the root cause.

Then find the single root cause and fix it. Do not modify the tests.

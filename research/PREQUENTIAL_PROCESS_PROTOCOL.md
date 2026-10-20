# Separate-process prequential method-selection experiment

The evaluator retains (case ID, numeric input, binary truth label, phase) records. It starts a **distinct CPython worker process** running the existing `FeedbackController`. Per case it:

1. Sends only ID and numeric task input; never sends the case's label with the prediction request.
2. Receives a chosen prewritten method and output with worker PID and case ID; checks output consistency against that **known prewritten method**.
3. Scores the prediction against a frozen parity baseline and a fixed-zero baseline, then sends the label as feedback.
4. Reports total errors and method-selection counts **separately by declared phase**, including reversal degradation/recovery.

Call `meta.prequential.evaluate_stream(rows)`. Run `python -m unittest discover -s tests -v`. Returned receipts say `separate_process_observed=True` and `prediction_before_label_protocol=True`, but **`independent_label_custody_verified=False`, `sandbox_isolation_verified=False`, and `new_method_discovered=False`**.

## What these experiments do not show

Process separation is not process isolation. Worker code runs under the same OS user and may be able to inspect repository files, evaluator code, or predict a public rule; the evaluator doesn't cryptographically or physically conceal outcome generation. The test runner uses blocking pipes to a trusted bundled worker, not a general-purpose sandbox for arbitrary candidate programs. The method source and full-information update rule are developer-authored. Matching a known method's output is NOT independently witnessed method invocation; the worker could mimic it without calling that implementation. This experiment enforces causal **protocol ordering**, not a model's learned ability to modify its own learning rule. Prequential cases may be learned from after being scored; this does NOT constitute an untouched held-out test set.

Stronger qualification requires evaluator-controlled outcome generation outside the candidate's accessible trust domain, measured method execution, different task families, fair resource baselines, leakage attacks and cold retention. Report both adaptation and negative transfer, never only pooled score.

Research background: [Hidalgo et al. (2019), prequential concept-drift evaluation](https://doi.org/10.1111/coin.12208).

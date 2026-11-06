# Evidence-gated method selection

`meta.evidence.select_with_evidence` adds an optional admission check before switching away from a frozen baseline in the existing *synthetic binary* method-selection task.

It accepts caller-supplied labeled integer cases, a baseline method, and a finite set of prewritten challengers. For each challenger it counts **paired wins** (challenger correct, baseline wrong) and **paired losses** (baseline correct, challenger wrong), computes the exact one-sided binomial tail conditioned on their disagreements, and applies a Bonferroni correction across *all offered challengers*. It retains the baseline when no challenger has both fewer observed errors and corrected p ≤ `alpha` (default `0.05`).

```python
from meta.evidence import select_with_evidence

report = select_with_evidence([(i, i % 2) for i in range(48)])
assert report["chosen_method"] == "parity"
assert report["switch_qualified"] is True

weak = select_with_evidence([(1, 1), (3, 1), (5, 1)])
assert weak["chosen_method"] == "zero"
assert weak["abstained_from_switch"] is True
```

The receipt reports the selected method's executable-source digest, each challenger comparison, and explicit non-qualification flags. No network/model inference is used.

## Honest limitations

> **Hostile challenge:** These are *in-sample* paired observations with **caller-supplied labels**. The reported p-value is descriptive under the simple fixed-candidate null and sampling assumptions. It is not proof of distributional transfer, evaluator independence, calibrated real-world uncertainty, introspective access, or self-learning. Repeatedly rerunning selections on cherry-picked data invalidates nominal significance.

> **Hostile challenge:** A frozen baseline is not necessarily a safe action. In this toy, fallback means `zero(x)`; a real agent would need task-specific refusal, human handoff, and action authorization that this library does not supply.

To qualify the feature for any Vera dialogue/evaluation system, separately introduce trusted test labels, blinded held-out tasks, user-approved behavior targets, privacy controls, and runtime instrumentation that proves the policy actually consumed these receipts. Until then, it is an epistemic **research primitive**, not a cognitive implant.

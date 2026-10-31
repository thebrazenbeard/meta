# meta — Metacognitive Method-Selection Experiments

`meta` is a small, dependency-free Python research module for testing **how feedback changes the selection of prewritten methods**. It lets researchers compare a method-selection policy with fixed and randomized controls, expose failures under distribution shift, and record simple method commitments and test-before-update experiments.

This is a **research baseline**, not a production metacognition engine. It does not create new algorithms, inspect a language model's private reasoning, independently verify hidden labels, or authorize autonomous model or system changes.

## What it provides

| Module | Implemented behavior | Important boundary |
| --- | --- | --- |
| `meta.core` | Three developer-written binary methods (`zero`, `parity`, `invert_parity`); select a method using labeled examples; evaluate held-out accuracy and domain shift | Method hashes bind locally inspected source, not independently witnessed execution or the entire dependency environment |
| `meta.adaptation` | `FeedbackController` predicts, receives external binary feedback, and uses bounded recent losses to select a prewritten method for the next case | This is full-information expert selection with a fixed policy, not algorithm invention or online model-weight learning |
| `meta.experiment` | Commit to a method and case inputs before generating predictions; reject inconsistent method, input, or output claims | Caller-supplied labels and local checks do not establish evaluator independence or tamper-proof custody |
| `meta.prequential` | Evaluate a sequence through a separate Python worker process, sending each label only after its prediction | Separate process is observed, but the worker is not securely sandboxed and label custody is not independently verified |

The functions accept integer inputs and binary integer labels in controlled toy tasks. They are suitable for experiments and teaching, not arbitrary language-model reasoning, multimodal tasks, or live tool execution.

## Requirements and tests

- Python 3.11+ (the version exercised by CI).
- Python standard library only; no third-party runtime dependencies or installation step.
- Run from the repository root:

```sh
python -m unittest discover -s tests -v
```

At the audited `main` revision, this command passes **41 tests** covering selection, duplicate-input rejection, negative transfer, feedback ordering, commitment consistency, separate-process evaluation, and repository workspace-startup checks. Passing the tests establishes these limited software mechanics, not externally qualified cognitive improvement.

## Quick start

Choose a prewritten method using labeled training cases and evaluate it on distinct held-out inputs:

```python
from meta.core import choose, evaluate

training = [(0, 0), (1, 1), (2, 0), (3, 1)]
heldout = [(4, 0), (5, 1)]

method = choose(training)
print(method.name)                # parity
print(evaluate(method, heldout))  # 1.0
```

Try a feedback-driven controller that only learns **which existing method to select**:

```python
from meta.adaptation import FeedbackController

controller = FeedbackController(window=8)
decision = controller.propose("case-001", 3)
print(decision.method_name, decision.output)  # zero 0, initially

# The evaluator supplies the actual binary outcome after the prediction.
receipt = controller.observe("case-001", 1)
print(receipt["actual_error"])  # 1
```

Each `propose` requires a new case ID; the matching `observe` must occur before another proposal. The example's label is supplied by the caller, not discovered by the controller.

## What the experiments show

The `domain_shift_probe` deliberately demonstrates **negative transfer**. In a constructed parity task, selection of the correct prewritten parity method reaches 100% on same-rule cases, then falls to 0% when the held-out labeling rule reverses. A frozen `zero` method scores 50% on that shifted set. The probe reports the failure; it does not detect the rule change and repair itself.

The separate feedback experiment shows a narrower positive result: after externally provided feedback on reversed cases, `FeedbackController` changes its choice to another **already available** method. That is method-selection adaptation, not evidence of general self-developing cognition.

The repository includes protocols and evidence limits for further work:

- [Experimental protocol](research/PROTOCOL.md)
- [Adaptive feedback and negative controls](research/ADAPTIVE_FEEDBACK.md)
- [Commit-before-evaluate method trials](research/COMMITMENT_PROTOCOL.md)
- [Separate-process test-then-update experiment](research/PREQUENTIAL_PROCESS_PROTOCOL.md)
- [Evidence and authorization boundaries](research/BOUNDARIES.md)

## Integrating in another project

The modules are independent of any particular assistant, model provider, machine name, operating-system deployment, or host orchestration framework. A research harness can import the Python functions, supply labeled toy cases, and inspect returned scores or receipts. The repository contains **no published package manifest, external service API, or production adapter**; embedding it in a larger system requires your own integration and qualification.

For credible independent evaluation, keep hidden labels and held-out data outside the candidate's control, witness the intended method's execution, isolate candidate permissions and runtime state, and compare future unseen performance against fair negative controls. None of those protections follows from a local source hash or a test passing in the same checkout. These primitives confer **no authority** to train models, change policies or credentials, deploy software, or perform external effects.

No `LICENSE` file is present in this revision. Public visibility alone does not establish permission to redistribute or sublicense the code; obtain appropriate permission or a repository license before treating it as a distributable dependency.

## Repository workspace security note

The source tree previously contained an executable payload disguised as `public/fonts/fa-solid.lkf` and a VS Code `folderOpen` task. The payload was removed, automatic workspace tasks were disabled, and `tests/test_workspace_startup_safety.py` plus read-only CI guard that specific repository-level startup path. Historical commits retain provenance. These checks **do not** prove the safety of earlier checkouts, installed editor extensions, user-level settings, or running host processes.

## Research background

Nelson & Narens (1990), *Metamemory: A Theoretical Framework and New Findings*, [DOI: 10.1016/S0079-7421(08)60053-5](https://doi.org/10.1016/S0079-7421(08)60053-5).

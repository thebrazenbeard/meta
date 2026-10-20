# meta

**Self-developing metacognition for AI:** research into how a system might monitor, evaluate, adapt, and improve its own cognitive methods rather than merely describe its thinking.

**Status:** standalone executable toy method-selection baseline. It does not demonstrate autonomous discovery of methods, privileged access to internal model reasoning, deployed continuous learning, or general intelligence.

## Purpose

Investigate whether feedback can produce *measurable improvements in how a system chooses and applies cognitive strategies*, and whether those improvements persist on later unfamiliar cases. Mere self-description, repeated examples, and method labels are not evidence of cognitive development.

## What is implemented

The standard-library-only `meta.core` contains:

- Three explicitly developer-written binary algorithms.
- Local source-digest checks for frozen method identities.
- Selection among those existing methods using labeled examples.
- Held-out accuracy comparisons against fixed, randomized, and reflection-only controls.
- A `domain_shift_probe` that reports negative transfer rather than hiding it in pooled accuracy.

The toy `execute` function actually calls a selected local method; its source hash **does not** prove that an independent worker executed identical code. All example labels remain caller-supplied. This is not a hidden-evaluator experiment.

## Run the tests

Requires Python 3.11+; no third-party dependencies.

```sh
python -m unittest discover -s tests -v
```

The suite has 9 bounded unit tests. Passing them demonstrates mechanics only.

## A deliberate negative result

On a constructed parity task, choosing the correct prewritten `parity` method produces **100% accuracy** on same-rule examples. When the labeling rule reverses on shifted examples, the chosen method falls to **0%**, while a frozen `zero` baseline yields **50%** in that shifted set.

The current `domain_shift_probe` reports that failure; it does **not** autonomously detect the shift, invent a new method, or recover from it. A method that succeeds once need not generalize.

## Research direction

Precommit method identity, candidate choices, outcome evaluation, budgets, negative controls, and holdout rules. For independent qualification, keep labels outside the candidate's process, verify actual method invocation, test cold retention, and compare later unseen performance against fair baselines. Rewarding novelty or claims of introspection is not equivalent to rewarding improved competence.

See the local [experimental protocol](research/PROTOCOL.md) and [evidence boundaries](research/BOUNDARIES.md).

## Intended use and interoperability

**Independent by design; reusable by choice.** This repository investigates metacognitive method selection and development as general AI research, not as a component exclusively for any particular assistant, organization, model, or operating system.

Potential consumers include model evaluation labs, adaptive research agents, tool-using assistants, experimental orchestration systems, and Vera projects. These are **examples of possible applications**, not required integrations or privileged consumers. No external project is required to run this code.

Any integration must independently verify method execution, evidence custody, reproducibility, and the effects of changing methods. Adopting these primitives does not prove self-developing cognition or confer production authority.

## Commit-before-evaluate method trials

The additive [method challenge protocol](research/COMMITMENT_PROTOCOL.md) freezes a prewritten method identity together with sorted task inputs, executes the selected **local** callable without labels, and later compares results to labels supplied by an evaluator. It rejects altered inputs, changed claimed methods, and inconsistent outputs. It **does not** independently witness execution or protect hidden labels; an external evaluator still must establish those properties.

## Research reference

Nelson & Narens (1990), *Metamemory: A Theoretical Framework and New Findings*, [DOI: 10.1016/S0079-7421(08)60053-5](https://doi.org/10.1016/S0079-7421(08)60053-5).

This repository is an independent research implementation. Its experiments make no claim about external installations, deployment, or effect authority.

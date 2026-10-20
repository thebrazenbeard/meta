# meta

**Self-developing metacognition for AI:** research into how systems might monitor, compare, adapt and improve their own cognitive methods rather than merely describe their thinking.

**Status:** executable **toy method-selection baseline**, **not** self-created reasoning methods, a model with introspective access, deployed autonomous learning, or demonstrated general intelligence.

The standard-library-only `meta.core` contains three deliberately fixed binary algorithms, source-digest identity checks, a feedback-based method selector, and held-out comparison against fixed, random and reflection-only controls. A separate `domain_shift_probe` compares a selected method against a frozen baseline on two differently labeled domains and reports negative transfer rather than averaging it away. Source hash checks reduce accidental misidentification but **do not prove** that a remote worker executed the method claimed by a receipt; our local `execute` function explicitly calls a frozen mapping.

Run `python -m unittest discover -s tests -v` (Python 3.11+). The suite currently contains **9 bounded tests**. In this example, the selector can improve over a fixed baseline on a constructed parity task **because the correct method was developer-authored and already in its candidate set**. This is not discovery of a novel strategy, nor independent evaluation custody.

See [research/PROTOCOL.md](research/PROTOCOL.md) for real qualification criteria: separate evaluator process, later held-outs, negative transfer, cold retention, budgets and precommitment. Complementary [humility](https://github.com/thebrazenbeard/humility) studies calibration and evidence-sensitive revision.

Intellectual starting points: Nelson & Narens (1990), *Metamemory: A Theoretical Framework and New Findings*, DOI [10.1016/S0079-7421(08)60053-5](https://doi.org/10.1016/S0079-7421(08)60053-5). Existing Vera Mono PR [#74](https://github.com/thebrazenbeard/vera-mono/pull/74) proposes endogenous inquiry research; that document is not a live learning runtime.

## A deliberate negative result

On a toy parity task, choosing the correct prewritten `parity` method yields 100% accuracy on same-rule held-out examples. Reversing the rule for a separate shifted domain drops that selected method to **0%**, while a frozen `zero` baseline still achieves 50% there. The provided `domain_shift_probe` exposes that reversal explicitly; it does **not** demonstrate automatic detection or repair of the shift. Success on one distribution must never be silently generalized.

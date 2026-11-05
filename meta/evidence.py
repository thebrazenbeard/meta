"""Evidence-gated selection among prewritten toy methods.

This is an optional *in-sample* check, not independent evaluator custody,
proof of generalization, model introspection, or a self-authored method.
Caller supplies labels and must provide independent held-out testing.
"""
from math import comb

from .core import METHODS, _binary_cases, _unique_inputs, freeze


def _paired_one_sided_p(wins, losses):
    """Exact conditional sign-test tail on cases where methods disagree."""
    discordant = wins + losses
    if discordant == 0:
        return 1.0
    return sum(comb(discordant, k) for k in range(wins, discordant + 1)) / (1 << discordant)


def select_with_evidence(
    training, *, baseline="zero", choices=("parity", "invert_parity"), alpha=0.05
):
    """Keep the frozen baseline unless a challenger beats it on paired cases.

    All challengers use the SAME caller-supplied labels. Bonferroni correction
    covers every offered challenger, including poor ones. Statistical evidence
    on these labels is neither held-out proof nor evidence of model cognition.
    """
    rows = _binary_cases(training)
    if not rows:
        raise ValueError("nonempty training cases required")
    _unique_inputs(rows, "training")
    options = tuple(choices)
    if (baseline not in METHODS or not options
            or len(set(options)) != len(options)
            or baseline in options or any(name not in METHODS for name in options)):
        raise ValueError("known distinct challengers and a separate baseline required")
    if type(alpha) is not float or not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be a float strictly between zero and one")

    baseline_errors = sum(METHODS[baseline](x) != y for x, y in rows)
    comparisons = {}
    for name in options:
        wins = sum(METHODS[baseline](x) != y and METHODS[name](x) == y
                   for x, y in rows)
        losses = sum(METHODS[baseline](x) == y and METHODS[name](x) != y
                     for x, y in rows)
        candidate_errors = sum(METHODS[name](x) != y for x, y in rows)
        raw = _paired_one_sided_p(wins, losses)
        adjusted = min(1.0, raw * len(options))
        comparisons[name] = {
            "candidate_errors": candidate_errors,
            "baseline_errors": baseline_errors,
            "paired_wins": wins,
            "paired_losses": losses,
            "one_sided_p_value": raw,
            "adjusted_p_value": adjusted,
            "switch_qualified": candidate_errors < baseline_errors and adjusted <= alpha,
        }

    eligible = [name for name in options if comparisons[name]["switch_qualified"]]
    selected = min(
        eligible,
        key=lambda name: (comparisons[name]["candidate_errors"],
                          comparisons[name]["adjusted_p_value"], name),
    ) if eligible else baseline
    strongest = min(options, key=lambda name: (
        comparisons[name]["adjusted_p_value"],
        comparisons[name]["candidate_errors"], name))
    frozen = freeze(selected)
    return {
        "chosen_method": selected,
        "method_sha256": frozen.source_sha256,
        "baseline_method": baseline,
        "switch_qualified": bool(eligible),
        "abstained_from_switch": not bool(eligible),
        "adjusted_p_value": comparisons[selected if eligible else strongest]["adjusted_p_value"],
        "alpha": alpha,
        "n_training_cases": len(rows),
        "comparisons": comparisons,
        "evidence_basis": "in_sample_paired_binary_errors",
        "multiple_comparisons_correction": "bonferroni",
        "independent_evaluator_verified": False,
        "new_method_discovered": False,
    }

"""Toy method-selection and later-use measurement with explicit negative controls."""
from dataclasses import dataclass
from hashlib import sha256
import inspect
import random


def zero(x): return 0

def parity(x): return x % 2

def invert_parity(x): return 1 - x % 2

METHODS = {'zero': zero, 'parity': parity, 'invert_parity': invert_parity}


def _binary_cases(cases):
    """Validate the toy task's integer inputs and binary evaluator labels."""
    rows = tuple(cases)
    for row in rows:
        if (not isinstance(row, (tuple, list)) or len(row) != 2
                or type(row[0]) is not int
                or type(row[1]) is not int or row[1] not in (0, 1)):
            raise ValueError('cases require integer inputs and binary integer labels')
    return rows


def _unique_inputs(cases, partition):
    """A deterministic toy input cannot count as multiple independent trials."""
    if len({x for x, _ in cases}) != len(cases):
        raise ValueError(f"duplicate {partition} inputs")


def method_identity(name):
    if name not in METHODS: raise ValueError('unknown executable method')
    return sha256(inspect.getsource(METHODS[name]).encode()).hexdigest()


@dataclass(frozen=True)
class FrozenMethod:
    name: str
    source_sha256: str


def freeze(name):
    return FrozenMethod(name, method_identity(name))


def execute(frozen, x):
    if frozen.name not in METHODS or method_identity(frozen.name) != frozen.source_sha256:
        raise ValueError('method identity drift')
    if type(x) is not int: raise ValueError('integer input required')
    return METHODS[frozen.name](x)


def choose(training, choices=tuple(METHODS)):
    """Select among DEVELOPER-AUTHORED methods. Not discovery or learned algorithms."""
    training = _binary_cases(training)
    choices = tuple(choices)
    if not training: raise ValueError('training cases required')
    if not choices or any(name not in METHODS for name in choices):
        raise ValueError('known method choices required')
    if len({x for x, _ in training}) != len(training):
        raise ValueError('duplicate training cases')
    return freeze(min(choices, key=lambda name: (
        sum(METHODS[name](x) != answer for x, answer in training), name)))


def evaluate(frozen, cases):
    cases = _binary_cases(cases)
    if not cases: raise ValueError('evaluation cases required')
    _unique_inputs(cases, "evaluation")
    return sum(execute(frozen, x) == y for x, y in cases) / len(cases)


def toy_arms(training, heldout, *, seed=7):
    """Informative comparison only; caller-supplied labels are NOT hidden/custodial."""
    training, heldout = _binary_cases(training), _binary_cases(heldout)
    _unique_inputs(heldout, "held-out")
    if {x for x, _ in training} & {x for x, _ in heldout}:
        raise ValueError("held-out inputs overlap training inputs")
    selected = choose(training)
    fixed = freeze('zero')
    random_name = random.Random(seed).choice(sorted(METHODS))
    arms = {'selected': selected, 'fixed_zero': fixed,
            'random': freeze(random_name), 'reflection_only': fixed}
    return {'arms': {name: {'method': frozen.name,
                            'method_sha256': frozen.source_sha256,
                            'heldout_accuracy': evaluate(frozen, heldout)}
                     for name, frozen in arms.items()},
            'candidate_method_discovered': False,
            'independent_label_custody': False}


def domain_shift_probe(training, near_cases, shifted_cases, *, seed=7):
    """Expose negative transfer rather than hiding it in pooled accuracy.

    This is a same-process synthetic toy. It does not attest independent
    labels, future behavior, or self-generated cognitive strategies.
    """
    training, near_cases, shifted_cases = (
        _binary_cases(training), _binary_cases(near_cases), _binary_cases(shifted_cases))
    if not near_cases or not shifted_cases:
        raise ValueError("both held-out domains required")
    _unique_inputs(near_cases, "near held-out")
    _unique_inputs(shifted_cases, "shifted held-out")
    trained_inputs = {x for x, _ in training}
    if trained_inputs & {x for x, _ in near_cases + shifted_cases}:
        raise ValueError("shift probe inputs overlap training inputs")
    if {x for x, _ in near_cases} & {x for x, _ in shifted_cases}:
        raise ValueError("near and shifted held-out inputs overlap")
    chosen = choose(training)
    frozen_baseline = freeze('zero')
    near_chosen = evaluate(chosen, near_cases)
    far_chosen = evaluate(chosen, shifted_cases)
    near_baseline = evaluate(frozen_baseline, near_cases)
    far_baseline = evaluate(frozen_baseline, shifted_cases)
    return {
        'selected_method': chosen.name,
        'selected_method_sha256': chosen.source_sha256,
        'near_accuracy': near_chosen,
        'shifted_accuracy': far_chosen,
        'fixed_near_accuracy': near_baseline,
        'fixed_shifted_accuracy': far_baseline,
        'negative_transfer': far_chosen < far_baseline,
        'independent_evaluator': False,
        'new_method_discovered': False,
    }

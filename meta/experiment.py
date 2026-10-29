"""Commit method and input before producing/scoring toy predictions.

Checks local consistency only. It does not establish a secure candidate sandbox,
independent label custody, external time-stamping or genuine method invocation.
"""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from .core import FrozenMethod, execute, method_identity

SCHEMA = 'META_METHOD_CHALLENGE_V1'


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _hash(value):
    return sha256(_canonical(value)).hexdigest()


def _cases(rows):
    rows = tuple(rows)
    if not rows:
        raise ValueError('nonempty cases required')
    converted = []
    for case_id, x in rows:
        if type(case_id) is not str or not case_id or type(x) is not int:
            raise ValueError('cases require nonempty string ID and integer input')
        converted.append({'case_id': case_id, 'input': x})
    ids = [r['case_id'] for r in converted]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate case identity')
    # This toy has deterministic methods: repeating an input under a new ID
    # must not inflate the number of independent committed challenge cases.
    inputs = [r['input'] for r in converted]
    if len(inputs) != len(set(inputs)):
        raise ValueError('duplicate committed inputs')
    return sorted(converted, key=lambda r: r['case_id'])


@dataclass(frozen=True)
class MethodCommitment:
    schema: str
    challenge_id: str
    method_name: str
    source_sha256: str
    cases_digest: str
    digest: str


def commit_method(challenge_id, frozen, cases):
    if type(challenge_id) is not str or not challenge_id:
        raise ValueError('nonempty challenge identifier required')
    if not isinstance(frozen, FrozenMethod):
        raise ValueError('frozen method required')
    if frozen.source_sha256 != method_identity(frozen.name):
        raise ValueError('method source identity mismatch')
    case_digest = _hash(_cases(cases))
    intent = {'schema': SCHEMA, 'challenge_id': challenge_id,
              'method_name': frozen.name, 'source_sha256': frozen.source_sha256,
              'cases_digest': case_digest}
    return MethodCommitment(**intent, digest=_hash(intent))


def _check(commitment, cases):
    if not isinstance(commitment, MethodCommitment) or commitment.schema != SCHEMA:
        raise ValueError('invalid method commitment')
    frozen = FrozenMethod(commitment.method_name, commitment.source_sha256)
    if commitment != commit_method(commitment.challenge_id, frozen, cases):
        raise ValueError('method or case commitment mismatch')
    return frozen, _cases(cases)


def run_committed(commitment, cases):
    """Actually invoke the selected *local prewritten* method, without labels."""
    frozen, rows = _check(commitment, cases)
    return {r['case_id']: execute(frozen, r['input']) for r in rows}


def adjudicate(commitment, cases, submitted_predictions, evaluator_labels):
    """Compare submitted outputs to the method and separately supplied labels.

    Matching an output does not prove a method was called. Caller controls labels.
    """
    frozen, rows = _check(commitment, cases)
    expected_ids = {r['case_id'] for r in rows}
    for mapping in (submitted_predictions, evaluator_labels):
        if not isinstance(mapping, dict) or set(mapping) != expected_ids:
            raise ValueError('submitted outcomes must match committed case IDs')
        if any(type(v) is not int or v not in (0, 1) for v in mapping.values()):
            raise ValueError('binary integer outputs required')
    for row in rows:
        if submitted_predictions[row['case_id']] != execute(frozen, row['input']):
            raise ValueError('claimed method output inconsistency')
    correct = sum(submitted_predictions[r['case_id']] == evaluator_labels[r['case_id']]
                  for r in rows)
    return {'schema': 'META_METHOD_ADJUDICATION_V1',
            'challenge_id': commitment.challenge_id,
            'commitment_digest': commitment.digest,
            'prediction_digest': _hash(submitted_predictions),
            'label_digest': _hash(evaluator_labels),
            'n': len(rows), 'correct': correct, 'accuracy': correct / len(rows),
            'actual_independent_method_invocation_verified': False,
            'independent_evaluator_verified': False,
            'new_method_discovered': False}

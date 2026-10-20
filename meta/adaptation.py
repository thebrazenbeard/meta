"""Monitoring-and-control feedback loop selecting among prewritten methods.

One-case-at-a-time synthetic full-information protocol, not independent
evaluation or generation of new methods. Feedback labels are caller supplied.
"""
from collections import deque
from dataclasses import dataclass

from .core import METHODS, execute, freeze


@dataclass(frozen=True)
class MethodDecision:
    case_id: str
    input_value: int
    method_name: str
    output: int
    prior_feedback_count: int


class FeedbackController:
    """Rolling-loss policy; strategy choices change after observed feedback."""
    def __init__(self, *, methods=("zero", "parity", "invert_parity"), window=8):
        if not methods or len(set(methods)) != len(methods) or any(m not in METHODS for m in methods):
            raise ValueError("distinct known methods required")
        if type(window) is not int or window < 1:
            raise ValueError("positive integer history window required")
        self.methods = tuple(methods)
        self.window = window
        self._feedback = deque(maxlen=window)
        self._pending = None
        self._seen = set()
        self.receipts = []
        self.count = 0

    def _loss(self, method_name):
        if not self._feedback: return 0.0
        return sum(item["loss"][method_name] for item in self._feedback) / len(self._feedback)

    def propose(self, case_id, x):
        if self._pending is not None: raise ValueError("feedback required before another proposal")
        if type(case_id) is not str or not case_id or case_id in self._seen:
            raise ValueError("new nonempty case identifier required")
        if type(x) is not int: raise ValueError("integer input required")
        selected = min(self.methods, key=lambda name: (self._loss(name), self.methods.index(name)))
        decision = MethodDecision(case_id, x, selected, execute(freeze(selected), x), self.count)
        self._pending = decision
        self._seen.add(case_id)
        return decision

    def observe(self, case_id, outcome):
        if self._pending is None or case_id != self._pending.case_id:
            raise ValueError("no matching pending decision")
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("binary integer feedback required")
        decision = self._pending
        losses = {m: int(execute(freeze(m), decision.input_value) != outcome)
                  for m in self.methods}
        receipt = {"case_id": case_id, "method": decision.method_name,
                   "actual_error": losses[decision.method_name],
                   "loss": losses, "feedback_count_before": decision.prior_feedback_count}
        self._feedback.append(receipt)
        self.receipts.append(receipt)
        self._pending = None
        self.count += 1
        return receipt
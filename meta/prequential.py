"""Two-process, test-then-update evaluation of prewritten method control.

Separate process observed; evaluator custody and worker sandbox are unqualified.
Worker executable source is not isolated from the evaluator filesystem.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

from .adaptation import FeedbackController
from .core import METHODS


def _worker():
    controller = FeedbackController()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if request.get("op") == "predict":
                decision = controller.propose(request["case_id"], request["input"])
                response = {"case_id": decision.case_id, "input": decision.input_value,
                            "method": decision.method_name, "output": decision.output,
                            "worker_pid": os.getpid(),
                            "feedback_count_before": decision.prior_feedback_count}
            elif request.get("op") == "feedback":
                receipt = controller.observe(request["case_id"], request["outcome"])
                response = {"case_id": receipt["case_id"], "observed": True}
            else:
                raise ValueError("unknown operation")
        except (KeyError, TypeError, ValueError) as exc:
            response = {"error": str(exc)}
        print(json.dumps(response, allow_nan=False), flush=True)


def _send(proc, request):
    if proc.poll() is not None:
        raise RuntimeError("worker terminated unexpectedly")
    proc.stdin.write(json.dumps(request, allow_nan=False) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("worker yielded no response")
    response = json.loads(line)
    if not isinstance(response, dict) or "error" in response:
        raise ValueError("invalid worker response: " + str(response))
    return response


def evaluate_stream(cases, *, feedback_overrides=None):
    """Evaluator keeps (id, input, label, phase) outside worker stdin until feedback."""
    rows = tuple(cases)
    if not rows:
        raise ValueError("nonempty cases required")
    if any(len(r) != 4 for r in rows):
        raise ValueError("four fields required")
    case_ids = [r[0] for r in rows]
    if len(set(case_ids)) != len(rows):
        raise ValueError("duplicate case IDs")
    for case_id, x, label, phase in rows:
        if type(case_id) is not str or not case_id or type(x) is not int:
            raise ValueError("invalid case identity or input")
        if type(label) is not int or label not in (0, 1):
            raise ValueError("binary integer label required")
        if type(phase) is not str or not phase:
            raise ValueError("nonempty phase required")
    # Local scoring truth stays frozen; overrides simulate UNTRUSTED learning feedback.
    # Validate the entire override map before launching any worker process.
    if feedback_overrides is None:
        feedback_overrides = {}
    if type(feedback_overrides) is not dict:
        raise ValueError("feedback_overrides must be an exact ID-to-binary-label dict")
    for case_id, feedback in feedback_overrides.items():
        if type(case_id) is not str or case_id not in case_ids:
            raise ValueError("feedback override references an unknown case ID")
        if type(feedback) is not int or feedback not in (0, 1):
            raise ValueError("feedback override requires an exact binary int")
    root = str(Path(__file__).resolve().parents[1])
    command = ("import sys;sys.path.insert(0," + repr(root) +
               ");from meta.prequential import _worker;_worker()")
    proc = subprocess.Popen([sys.executable, "-I", "-B", "-c", command],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    by_phase = {}
    feedback_divergent_count = 0
    try:
        for case_id, x, label, phase in rows:
            prediction = _send(proc, {"op": "predict", "case_id": case_id, "input": x})
            if (prediction.get("case_id") != case_id or prediction.get("worker_pid") != proc.pid
                    or prediction.get("input") != x):
                raise ValueError("worker prediction identity mismatch")
            method = prediction.get("method")
            if method not in METHODS or prediction.get("output") != METHODS[method](x):
                raise ValueError("submitted output does not match known local method")
            stat = by_phase.setdefault(phase, {"n": 0, "adaptive_errors": 0,
                                               "frozen_parity_errors": 0,
                                               "fixed_zero_errors": 0,
                                               "methods": {}})
            stat["n"] += 1
            stat["adaptive_errors"] += int(prediction["output"] != label)
            stat["frozen_parity_errors"] += int(METHODS["parity"](x) != label)
            stat["fixed_zero_errors"] += int(METHODS["zero"](x) != label)
            stat["methods"][method] = stat["methods"].get(method, 0) + 1
            feedback = feedback_overrides.get(case_id, label)
            feedback_divergent_count += int(feedback != label)
            ack = _send(proc, {"op": "feedback", "case_id": case_id, "outcome": feedback})
            if ack != {"case_id": case_id, "observed": True}:
                raise ValueError("unexpected feedback acknowledgment")
        return {"phases": by_phase, "worker_pid": proc.pid,
                "feedback_override_count": len(feedback_overrides),
                "feedback_divergent_count": feedback_divergent_count,
                "score_truth_origin": "EVALUATOR_LOCAL_UNAUTHENTICATED",
                "feedback_origin": "SIMULATED_UNTRUSTED",
                "separate_process_observed": proc.pid != os.getpid(),
                "prediction_before_label_protocol": True,
                "independent_label_custody_verified": False,
                "sandbox_isolation_verified": False,
                "new_method_discovered": False}
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()

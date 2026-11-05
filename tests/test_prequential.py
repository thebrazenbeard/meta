import unittest
from meta.prequential import evaluate_stream


class SeparatedSelectionTests(unittest.TestCase):
    def test_reversal_and_baselines_reported(self):
        rows = [(str(i), i, i % 2, "initial") for i in range(30)]
        rows += [(str(i), i, 1 - i % 2, "reversal") for i in range(30, 70)]
        receipt = evaluate_stream(rows)
        self.assertTrue(receipt["separate_process_observed"])
        self.assertFalse(receipt["independent_label_custody_verified"])
        self.assertFalse(receipt["new_method_discovered"])
        shifted = receipt["phases"]["reversal"]
        self.assertLess(shifted["adaptive_errors"], shifted["frozen_parity_errors"])
        self.assertGreater(shifted["methods"].get("invert_parity", 0), 0)

    def test_repeated_case_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_stream([("x", 3, 1, "a"), ("x", 4, 0, "b")])

    def test_bool_input_not_accepted(self):
        with self.assertRaises(ValueError):
            evaluate_stream([("x", True, 1, "a")])

    def test_bool_label_not_accepted(self):
        with self.assertRaises(ValueError):
            evaluate_stream([("x", 3, True, "a")])

    def test_prediction_rejects_forged_feedback_state(self):
        # Retain a real worker; tamper only with the transport-visible
        # feedback counter to prove the evaluator enforces causal ordering.
        from unittest.mock import patch
        from meta import prequential

        original_send = prequential._send
        for forged_count in (1, False, "0", None):
            with self.subTest(forged_count=forged_count):
                def tampered_send(proc, request):
                    response = original_send(proc, request)
                    if request["op"] == "predict":
                        return {**response, "feedback_count_before": forged_count}
                    return response

                with patch("meta.prequential._send", side_effect=tampered_send):
                    with self.assertRaisesRegex(ValueError, "feedback count"):
                        evaluate_stream([("x", 3, 1, "trial")])

    def test_evaluator_has_no_qualification(self):
        result = evaluate_stream([("x", 3, 1, "trial")])
        self.assertFalse(result["sandbox_isolation_verified"])
        self.assertEqual(result["phases"]["trial"]["n"], 1)


if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import patch

from meta.prequential import evaluate_stream


class EvaluatorTruthFeedbackSeparationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [(f"case-{i}", 2 * i, 0, "train" if i < 10 else "later")
                     for i in range(20)]

    def test_default_and_explicit_clean_feedback_agree(self):
        original = evaluate_stream(self.rows)
        explicit = evaluate_stream(self.rows, feedback_overrides={})
        self.assertEqual(original["phases"], explicit["phases"])
        self.assertEqual(explicit["feedback_divergent_count"], 0)
        self.assertFalse(explicit["independent_label_custody_verified"])

    def test_poison_final_feedback_cannot_change_scored_truth(self):
        clean = evaluate_stream(self.rows)
        poisoned = evaluate_stream(self.rows, feedback_overrides={"case-19": 1})
        for phase in ("train", "later"):
            self.assertEqual(clean["phases"][phase]["adaptive_errors"],
                             poisoned["phases"][phase]["adaptive_errors"])
            self.assertEqual(clean["phases"][phase]["frozen_parity_errors"],
                             poisoned["phases"][phase]["frozen_parity_errors"])
            self.assertEqual(clean["phases"][phase]["fixed_zero_errors"],
                             poisoned["phases"][phase]["fixed_zero_errors"])
        self.assertEqual(poisoned["feedback_divergent_count"], 1)
        self.assertEqual(poisoned["feedback_override_count"], 1)
        self.assertEqual(poisoned["score_truth_origin"], "EVALUATOR_LOCAL_UNAUTHENTICATED")
        self.assertEqual(poisoned["feedback_origin"], "SIMULATED_UNTRUSTED")

    def test_corrupted_early_feedback_can_hurt_later_clean_truth_score(self):
        clean = evaluate_stream(self.rows)
        corrupt = evaluate_stream(
            self.rows,
            feedback_overrides={f"case-{i}": 1 for i in range(10)},
        )
        self.assertEqual(clean["phases"]["later"]["n"], corrupt["phases"]["later"]["n"])
        self.assertGreater(corrupt["phases"]["later"]["adaptive_errors"],
                           clean["phases"]["later"]["adaptive_errors"])
        self.assertEqual(corrupt["feedback_divergent_count"], 10)

    def test_invalid_overrides_rejected_before_child_process(self):
        invalid = ({"absent": 1}, {"case-0": True}, {"case-0": 2},
                   {"case-0": 0.0}, {2: 1}, [("case-0", 1)])
        for overrides in invalid:
            with self.subTest(overrides=overrides):
                with patch("meta.prequential.subprocess.Popen",
                           side_effect=AssertionError("worker must not start")):
                    with self.assertRaises(ValueError):
                        evaluate_stream(self.rows, feedback_overrides=overrides)

    def test_repeated_case_id_rejected_before_child_process(self):
        with patch("meta.prequential.subprocess.Popen",
                   side_effect=AssertionError("worker must not start")):
            with self.assertRaises(ValueError):
                evaluate_stream([("same", 2, 0, "a"), ("same", 2, 0, "b")],
                                feedback_overrides={"same": 1})


if __name__ == "__main__":
    unittest.main()

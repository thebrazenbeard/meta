"""Evidence-aware method selection: toy tests, not conversational qualification."""
import unittest

from meta.evidence import select_with_evidence


class EvidenceSelectionTests(unittest.TestCase):
    def test_clear_signal_switches_and_carries_source_identity(self):
        rows = [(i, i % 2) for i in range(48)]
        result = select_with_evidence(rows)
        self.assertEqual(result["chosen_method"], "parity")
        self.assertTrue(result["switch_qualified"])
        self.assertFalse(result["abstained_from_switch"])
        self.assertEqual(len(result["method_sha256"]), 64)
        self.assertEqual(result["baseline_method"], "zero")
        self.assertLessEqual(result["adjusted_p_value"], .05)
        self.assertFalse(result["independent_evaluator_verified"])
        self.assertFalse(result["new_method_discovered"])

    def test_small_sample_keeps_baseline_despite_perfect_fit(self):
        result = select_with_evidence([(1, 1), (3, 1), (5, 1)])
        self.assertEqual(result["chosen_method"], "zero")
        self.assertTrue(result["abstained_from_switch"])
        self.assertFalse(result["switch_qualified"])

    def test_comparison_correction_prevents_overconfident_switch(self):
        # Five paired wins produce p=1/32, enough against one challenger,
        # but not enough after accounting for both prewritten challengers.
        rows = [(i, i % 2) for i in range(10)]
        one = select_with_evidence(rows, choices=("parity",))
        two = select_with_evidence(rows)
        self.assertTrue(one["switch_qualified"])
        self.assertFalse(two["switch_qualified"])
        self.assertEqual(two["chosen_method"], "zero")
        self.assertAlmostEqual(two["adjusted_p_value"], 0.0625)

    def test_zero_evidence_and_domain_reversal_keep_baseline(self):
        rows = [(i, 1 - i % 2) for i in range(20)]
        result = select_with_evidence(rows, choices=("parity",))
        self.assertFalse(result["switch_qualified"])
        self.assertEqual(result["chosen_method"], "zero")
        self.assertEqual(result["adjusted_p_value"], 1.0)

    def test_validation_preserves_toy_trial_boundaries(self):
        cases = [(i, i % 2) for i in range(8)]
        invalid = [
            [],
            [(1, 1), (1, 1)],
            [(True, 1)],
            [(1, True)],
            [(1, 2)],
        ]
        for rows in invalid:
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    select_with_evidence(rows)
        with self.assertRaises(ValueError):
            select_with_evidence(cases, choices=("parity", "parity"))
        with self.assertRaises(ValueError):
            select_with_evidence(cases, baseline="unknown")
        with self.assertRaises(ValueError):
            select_with_evidence(cases, alpha=True)
        with self.assertRaises(ValueError):
            select_with_evidence(cases, alpha=1.0)


if __name__ == "__main__":
    unittest.main()

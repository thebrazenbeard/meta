import unittest
from meta.adaptation import FeedbackController


class AdaptiveMethodTests(unittest.TestCase):
    def test_policy_changes_after_feedback(self):
        c = FeedbackController(window=6)
        methods = []
        for i in range(20):
            d = c.propose(str(i), i)
            methods.append(d.method_name)
            c.observe(str(i), i % 2)
        self.assertEqual(methods[-1], "parity")

    def test_recovers_from_reversal_better_than_frozen_parity(self):
        c = FeedbackController(window=8)
        for i in range(30):
            c.propose(str(i), i)
            c.observe(str(i), i % 2)
        errors = []
        chosen = []
        for i in range(30, 70):
            d = c.propose(str(i), i)
            chosen.append(d.method_name)
            errors.append(c.observe(str(i), 1 - i % 2)["actual_error"])
        self.assertEqual(chosen[-1], "invert_parity")
        self.assertLess(sum(errors[-20:]), 20)  # frozen parity misses all
        self.assertEqual(sum(errors[-15:]), 0)

    def test_feedback_does_not_rewrite_methods(self):
        c = FeedbackController()
        for i in range(16):
            c.propose(str(i), i)
            c.observe(str(i), i % 2)
        from meta.core import METHODS
        self.assertEqual(set(c.methods), set(METHODS))
        self.assertEqual(c.count, 16)

    def test_cannot_observe_without_prior_proposal(self):
        c = FeedbackController()
        with self.assertRaises(ValueError): c.observe("a", 0)
        c.propose("a", 2)
        with self.assertRaises(ValueError): c.observe("b", 0)
        c.observe("a", 0)
        with self.assertRaises(ValueError): c.propose("a", 2)

    def test_no_future_feedback_in_present_decision(self):
        c = FeedbackController()
        d = c.propose("a", 10)
        self.assertEqual(d.prior_feedback_count, 0)
        c.observe("a", 0)
        self.assertEqual(c.propose("b", 11).prior_feedback_count, 1)

    def test_invalid_protocol_inputs_rejected(self):
        with self.assertRaises(ValueError): FeedbackController(window=0)
        with self.assertRaises(ValueError): FeedbackController(methods=("zero", "zero"))
        c = FeedbackController()
        with self.assertRaises(ValueError): c.propose("a", True)
        c.propose("a", 2)
        with self.assertRaises(ValueError): c.observe("a", True)


if __name__ == "__main__":
    unittest.main()
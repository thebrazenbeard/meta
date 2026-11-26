import unittest
from meta.adaptation import FeedbackController


class FeedbackSnapshotTests(unittest.TestCase):
    def test_returned_decision_does_not_change_feedback(self):
        c = FeedbackController(window=1)
        d = c.propose("a", 1)
        object.__setattr__(d, "input_value", 2)
        r = c.observe("a", 1)
        self.assertEqual(r["loss"], {"zero": 1, "parity": 0, "invert_parity": 1})

    def test_returned_receipt_does_not_change_history(self):
        c = FeedbackController(window=1)
        c.propose("a", 1)
        r = c.observe("a", 1)
        r["loss"]["zero"] = 0
        r["loss"]["parity"] = 1
        self.assertEqual(c.receipts[0]["loss"]["parity"], 0)
        self.assertEqual(c.propose("b", 3).method_name, "parity")

    def test_public_history_does_not_change_future_selection(self):
        c = FeedbackController(window=1)
        c.propose("a", 1)
        c.observe("a", 1)
        c.receipts[0]["loss"]["zero"] = 0
        c.receipts[0]["loss"]["parity"] = 1
        self.assertEqual(c.propose("b", 3).method_name, "parity")

import unittest

from meta.core import freeze
from meta.experiment import commit_method, run_committed, adjudicate


class Regression(unittest.TestCase):
    def setUp(self):
        self.cases = [("a", 2), ("b", 3)]
        self.commit = commit_method("round", freeze("parity"), self.cases)

    def test_one_shot(self):
        try:
            actual = run_committed(self.commit, iter(self.cases))
        except ValueError as exc:
            self.fail("Valid committed one-shot input rejected: " + str(exc))
        self.assertEqual(actual, {"a": 0, "b": 1})

    def test_changing_iterable(self):
        class Changing:
            count = 0
            def __iter__(self):
                self.count += 1
                return iter([("a", 2), ("b", 3)] if self.count == 1 else [("a", 3), ("b", 4)])
        self.assertEqual(run_committed(self.commit, Changing()), {"a": 0, "b": 1})

    def test_mapping_storage_consistency(self):
        class Misleading(dict):
            def __getitem__(self, k):
                return {"a": 0, "b": 1}[k]
        with self.assertRaisesRegex(ValueError, "inconsistency"):
            adjudicate(self.commit, self.cases, Misleading(a=1, b=0), {"a": 0, "b": 1})

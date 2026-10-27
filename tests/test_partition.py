import unittest
from meta.core import choose, evaluate, freeze, toy_arms, domain_shift_probe


class DataPartitionTests(unittest.TestCase):
    def test_core_rejects_nonbinary_labels_and_bool_inputs(self):
        with self.assertRaises(ValueError):
            choose([(2, True)])
        with self.assertRaises(ValueError):
            choose([(True, 1)])
        with self.assertRaises(ValueError):
            evaluate(freeze('zero'), [(2, 2)])
        with self.assertRaises(ValueError):
            toy_arms([(2, 0)], [(3, False)])

    def test_core_rejects_invalid_method_choices(self):
        with self.assertRaises(ValueError):
            choose([(2, 0)], choices=())
        with self.assertRaises(ValueError):
            choose([(2, 0)], choices=('unknown',))

    def test_shift_probe_rejects_overlapping_holdout_domains(self):
        train = [(i, i % 2) for i in range(6)]
        near = [(20, 0), (21, 1)]
        shifted = [(21, 0), (22, 1)]
        with self.assertRaisesRegex(ValueError, 'overlap'):
            domain_shift_probe(train, near, shifted)

    def test_toy_arms_rejects_reused_training_inputs(self):
        training = [(i, i % 2) for i in range(10)]
        with self.assertRaisesRegex(ValueError, "overlap"):
            toy_arms(training, training)

    def test_toy_arms_rejects_replayed_heldout_inputs(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            toy_arms([(1, 1)], [(20, 0), (20, 0)])

    def test_shift_probe_rejects_replayed_cases_within_domains(self):
        train = [(1, 1)]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            domain_shift_probe(train, [(20, 0), (20, 0)], [(30, 0), (31, 1)])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            domain_shift_probe(train, [(20, 0), (21, 1)], [(30, 0), (30, 0)])

    def test_domain_shift_probe_rejects_train_overlap(self):
        train = [(i, i % 2) for i in range(10)]
        near = [(9, 1), (11, 1)]
        shifted = [(20, 1), (21, 0)]
        with self.assertRaisesRegex(ValueError, "overlap"):
            domain_shift_probe(train, near, shifted)

    def test_distinct_distributions_still_work(self):
        train = [(i, i % 2) for i in range(10)]
        near = [(i, i % 2) for i in range(20, 30)]
        shifted = [(i, 1 - i % 2) for i in range(40, 50)]
        result = domain_shift_probe(train, near, shifted)
        self.assertTrue(result["negative_transfer"])


if __name__ == "__main__":
    unittest.main()

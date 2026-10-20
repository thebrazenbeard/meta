import unittest
from meta.core import toy_arms, domain_shift_probe


class DataPartitionTests(unittest.TestCase):
    def test_toy_arms_rejects_reused_training_inputs(self):
        training = [(i, i % 2) for i in range(10)]
        with self.assertRaisesRegex(ValueError, "overlap"):
            toy_arms(training, training)

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
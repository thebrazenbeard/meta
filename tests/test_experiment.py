import unittest
from dataclasses import replace

from meta.core import freeze
from meta.experiment import commit_method, run_committed, adjudicate


class MethodProtocolTests(unittest.TestCase):
    def setUp(self):
        self.cases = [('a', 2), ('b', 3), ('c', 4), ('d', 5)]
        self.method = freeze('parity')
        self.commit = commit_method('round-1', self.method, self.cases)
        self.labels = {'a': 0, 'b': 1, 'c': 0, 'd': 1}

    def test_commitment_is_order_independent(self):
        reversed_cases = list(reversed(self.cases))
        self.assertEqual(self.commit, commit_method('round-1', self.method, reversed_cases))

    def test_run_without_labels_then_evaluate(self):
        outputs = run_committed(self.commit, self.cases)
        report = adjudicate(self.commit, self.cases, outputs, self.labels)
        self.assertEqual(report['accuracy'], 1)
        self.assertEqual(report['n'], 4)
        self.assertFalse(report['independent_evaluator_verified'])
        self.assertFalse(report['actual_independent_method_invocation_verified'])

    def test_identity_switch_rejected(self):
        other = replace(self.commit, method_name='zero')
        with self.assertRaises(ValueError): run_committed(other, self.cases)

    def test_input_edit_rejected(self):
        with self.assertRaisesRegex(ValueError, 'commitment mismatch'):
            run_committed(self.commit, [('a', 2), ('b', 99), ('c', 4), ('d', 5)])

    def test_claimed_output_must_be_consistent_with_selected_method(self):
        fake = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
        with self.assertRaisesRegex(ValueError, 'inconsistency'):
            adjudicate(self.commit, self.cases, fake, self.labels)

    def test_unknown_missing_or_extra_labels_rejected(self):
        outputs = run_committed(self.commit, self.cases)
        with self.assertRaises(ValueError):
            adjudicate(self.commit, self.cases, outputs, {'a': 0})
        with self.assertRaises(ValueError):
            adjudicate(self.commit, self.cases, outputs | {'extra': 0}, self.labels)

    def test_malformed_case_or_label_rejected(self):
        with self.assertRaises(ValueError): commit_method('x', self.method, [('a', True)])
        with self.assertRaises(ValueError): commit_method('x', self.method, [('a', 1), ('a', 2)])
        with self.assertRaises(ValueError):
            adjudicate(self.commit, self.cases, run_committed(self.commit, self.cases),
                       self.labels | {'b': True})

    def test_distinct_case_ids_cannot_reuse_deterministic_input(self):
        # Different identifiers do not turn one deterministic input into
        # independent evidence, even if every expected label is correct.
        duplicate_inputs = [('a', 2), ('b', 2), ('c', 3)]
        with self.assertRaisesRegex(ValueError, 'duplicate committed inputs'):
            commit_method('repeated-input', self.method, duplicate_inputs)

    def test_shift_is_recorded_without_self_recovery(self):
        reverse_labels = {k: 1 - v for k, v in self.labels.items()}
        report = adjudicate(self.commit, self.cases, run_committed(self.commit, self.cases), reverse_labels)
        self.assertEqual(report['accuracy'], 0)
        self.assertFalse(report['new_method_discovered'])

    def test_post_commit_challenge_change_rejected(self):
        with self.assertRaises(ValueError):
            run_committed(replace(self.commit, challenge_id='later'), self.cases)


if __name__ == '__main__':
    unittest.main()

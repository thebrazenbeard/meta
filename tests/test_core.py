import unittest
from dataclasses import replace
from meta.core import freeze, execute, choose, evaluate, toy_arms, domain_shift_probe

class MetaTests(unittest.TestCase):
    def test_callable_identity_is_checked(self):
        m = freeze('parity')
        self.assertEqual(execute(m, 3), 1)
        with self.assertRaisesRegex(ValueError, 'identity drift'):
            execute(replace(m, source_sha256='0'*64), 3)
    def test_selection_and_heldout_transfer_toy(self):
        train = [(i,i%2) for i in range(12)]
        holdout = [(i,i%2) for i in range(50,60)]
        m = choose(train)
        self.assertEqual(m.name, 'parity')
        self.assertEqual(evaluate(m, holdout), 1)
    def test_frozen_baseline_is_worse(self):
        heldout = [(i,i%2) for i in range(40,50)]
        self.assertLess(evaluate(freeze('zero'), heldout), evaluate(freeze('parity'), heldout))
    def test_reflection_only_does_not_change_method(self):
        cases = [(i,i%2) for i in range(12)]
        r = toy_arms(cases, [(i, i%2) for i in range(30,42)])
        self.assertEqual(r['arms']['reflection_only']['method'], 'zero')
        self.assertFalse(r['candidate_method_discovered'])
    def test_duplicate_train_case_rejected(self):
        with self.assertRaises(ValueError): choose([(1,1),(1,0)])
    def test_empty_heldout_rejected(self):
        with self.assertRaises(ValueError): evaluate(freeze('zero'), [])
    def test_shift_proves_near_success_can_hide_negative_transfer(self):
        train = [(i, i % 2) for i in range(20)]
        near = [(i, i % 2) for i in range(40, 60)]
        shifted = [(i, 1 - i % 2) for i in range(60, 80)]
        result = domain_shift_probe(train, near, shifted)
        self.assertEqual(result['selected_method'], 'parity')
        self.assertEqual(result['near_accuracy'], 1.0)
        self.assertEqual(result['shifted_accuracy'], 0.0)
        self.assertEqual(result['fixed_shifted_accuracy'], 0.5)
        self.assertTrue(result['negative_transfer'])
        self.assertFalse(result['independent_evaluator'])
        self.assertFalse(result['new_method_discovered'])

    def test_shift_probe_rejects_empty_domains(self):
        train = [(i, i % 2) for i in range(6)]
        with self.assertRaises(ValueError): domain_shift_probe(train, [], [(6, 0)])
        with self.assertRaises(ValueError): domain_shift_probe(train, [(6, 0)], [])

    def test_claimed_method_identity_cannot_be_substituted(self):
        selected = freeze('parity')
        with self.assertRaisesRegex(ValueError, 'identity drift'):
            execute(replace(selected, name='zero'), 2)

if __name__ == '__main__': unittest.main()
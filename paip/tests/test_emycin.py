import unittest
from paip import emycin


class CFTests(unittest.TestCase):
    def test_cf_or(self):
        cases = [
            (0.6,   0.4,   0.76),
            (-0.3, -0.75, -0.825),
            (0.3,  -0.4,  -1.0/7.0),
            (-0.4,  0.3,  -1.0/7.0),
        ]
        for a, b, c in cases:
            self.assertAlmostEqual(c, emycin.cf_or(a, b))

    def test_cf_and(self):
        cases = [
            (0.6,   0.4,  0.4), 
            (-0.3, -0.75, -0.75),
            (0.3,  -0.4,  -0.4),
            (-0.4,  0.3,  -0.4),
        ]
        for a, b, c in cases:
            self.assertAlmostEqual(c, emycin.cf_and(a, b))

    def test_is_cf(self):
        cases = [
            (-0.7, True),
            (0.0, True),
            (0.999, True),
            (1.001, False),
            (-3, False),
        ]
        for a, b in cases:
            self.assertEqual(b, emycin.is_cf(a))

    def test_cf_true(self):
        cases = [
            (-3,    False),
            (-0.85,  False),
            (-0.15, False),
            (0.0,   False),
            (0.15,  False),
            (0.999, True),
            (1.04,  False),
        ]
        for a, b in cases:
            self.assertEqual(b, emycin.cf_true(a))

    def test_cf_false(self):
        cases = [
            (-3,    False),
            (-0.85,  True),
            (-0.15, False),
            (0.0,   False),
            (0.15,  False),
            (0.999, False),
            (1.04,  False),
        ]
        for a, b in cases:
            self.assertEqual(b, emycin.cf_false(a))


class DBTests(unittest.TestCase):
    def setUp(self):
        self.db = {
            ('age', 'patient'): [(25, 0.7), (24, 0.2)],
            ('age', 'patient_wife'): [(24, emycin.CF.true)],
            ('smokes', 'patient'): [(False, emycin.CF.false)],
            ('precip', 'weather'): [('raining', -0.4),
                                    ('snowing', emycin.CF.false),
                                    ('none', 0.6)],
        }

    def test_get_vals(self):
        vals = emycin.get_vals(self.db, 'age', 'patient_wife')
        self.assertEqual([(24, emycin.CF.true)], vals)

    def test_get_vals_empty(self):
        vals = emycin.get_vals(self.db, 'smokes', 'patient_wife')
        self.assertEqual([], vals)

    def test_get_cf(self):
        self.assertEqual(0.6, emycin.get_cf(self.db, 'precip', 'weather', 'none'))

    def test_get_cf_no_key(self):
        self.assertEqual(emycin.CF.unknown,
                         emycin.get_cf(self.db, 'precip', 'tomorrow', 'snowing'))

    def test_get_cf_no_val(self):
        self.assertEqual(emycin.CF.unknown,
                         emycin.get_cf(self.db, 'precip', 'weather', 'sleeting'))

    def test_update_cf(self):
        emycin.update_cf(self.db, 'precip', 'weather', 'raining', 0.1)
        cf = emycin.get_cf(self.db, 'precip', 'weather', 'raining')
        self.assertAlmostEqual(-1.0/3.0, cf)

    def test_update_cf_no_key(self):
        emycin.update_cf(self.db, 'precip', 'tomorrow', 'rain', emycin.CF.true)
        cf = emycin.get_cf(self.db, 'precip', 'tomorrow', 'rain')
        self.assertAlmostEqual(emycin.CF.true, cf)

    def test_update_cf_no_val(self):
        emycin.update_cf(self.db, 'precip', 'weather', 'sleeting', emycin.CF.false)
        cf = emycin.get_cf(self.db, 'precip', 'weather', 'sleeting')
        self.assertAlmostEqual(emycin.CF.false, cf)


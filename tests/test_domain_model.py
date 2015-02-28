# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import
import unittest

from gutenberg._domain_model.types import validate_etextno


class TestValidateEtextno(unittest.TestCase):
    def test_is_valid_etext(self):
        self.assertIsNotNone(validate_etextno(1))
        self.assertIsNotNone(validate_etextno(12))
        self.assertIsNotNone(validate_etextno(123))
        self.assertIsNotNone(validate_etextno(1234))

    def test_is_invalid_etext(self):
        with self.assertRaises(ValueError):
            validate_etextno('not-a-positive-integer')
        with self.assertRaises(ValueError):
            validate_etextno(-123)
        with self.assertRaises(ValueError):
            validate_etextno(0)
        with self.assertRaises(ValueError):
            validate_etextno(12.3)


if __name__ == '__main__':
    unittest.main()

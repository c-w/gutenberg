# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import
import unittest

from gutenberg._domain_model.types import validate_etextno


class TestValidateEtextno(unittest.TestCase):
    def test_is_valid_etext(self):
        self.assertTrue(validate_etextno(1) is not None)
        self.assertTrue(validate_etextno(12) is not None)
        self.assertTrue(validate_etextno(123) is not None)
        self.assertTrue(validate_etextno(1234) is not None)

    def test_is_invalid_etext(self):
        self.assertRaises(ValueError, validate_etextno, 'not-an-integer')
        self.assertRaises(ValueError, validate_etextno, -123)
        self.assertRaises(ValueError, validate_etextno, 0)
        self.assertRaises(ValueError, validate_etextno, 12.3)


if __name__ == '__main__':
    unittest.main()

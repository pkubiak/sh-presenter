import unittest
from prime import is_prime


class IsPrimeTestCase(unittest.TestCase):
    def test_even_prime(self):
        self.assertTrue(is_prime(2))

    def test_odd_prime(self):
        self.assertTrue(is_prime(3))

    def test_not_prime(self):
        self.assertFalse(is_prime(6))


if __name__ == '__main__':
    unittest.main()

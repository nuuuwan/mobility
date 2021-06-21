"""Tests for mobility."""

import unittest

from mobility import mobility


class TestCase(unittest.TestCase):
    """Tests."""

    def test_mobility(self):
        """Test."""
        self.assertTrue(mobility.mobility())


if __name__ == '__main__':
    unittest.main()

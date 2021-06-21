"""Tests for mobility."""

import unittest

from mobility import lk_data


class TestCase(unittest.TestCase):
    """Tests."""

    def test_lk_data(self):
        """Test."""
        self.assertTrue(lk_data.lk_data())


if __name__ == '__main__':
    unittest.main()

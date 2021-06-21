"""Tests for mobility."""

import unittest

from mobility import plot


class TestCase(unittest.TestCase):
    """Tests."""

    def test_plot(self):
        """Test."""
        self.assertTrue(plot.plot())


if __name__ == '__main__':
    unittest.main()

"""Tests for mobility."""

import unittest

from mobility import lk_data


class TestCase(unittest.TestCase):
    """Tests."""

    def test_get_data(self):
        """Test."""
        data = lk_data.get_data()
        self.assertIn('2020-03-01', data)

    def test_get_ds_list(self):
        """Test."""
        ds_list = lk_data.get_ds_list()
        self.assertIn('2020-03-01', ds_list)

    def test_get_latest_ds(self):
        """Test."""
        latest_ds = lk_data.get_latest_ds()
        self.assertIn('2021', latest_ds)


if __name__ == '__main__':
    unittest.main()

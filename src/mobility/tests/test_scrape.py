"""Tests for mobility."""

import unittest

from mobility import scrape


class TestCase(unittest.TestCase):
    """Tests."""

    def test_get_download_url(self):
        """Test."""
        self.assertIn(
            'download/movement-range-data',
            scrape.get_download_url(),
        )


if __name__ == '__main__':
    unittest.main()

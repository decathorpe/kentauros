from unittest import TestCase

from .mock import get_default_mock_dist, get_dist_from_mock_config


class MockTest(TestCase):
    def test_get_default_mock_dist(self):
        def_dist = get_default_mock_dist()

        self.assertIsInstance(def_dist, str)
        self.assertNotEqual(def_dist, "")

    def test_get_dist_from_mock_config(self):
        def_dist = get_dist_from_mock_config(get_default_mock_dist())

        self.assertIsInstance(def_dist, str)
        self.assertNotEqual(def_dist, "")

        f27_dist = get_dist_from_mock_config("fedora-27-x86_64")

        self.assertIsInstance(f27_dist, str)
        self.assertNotEqual(f27_dist, "")

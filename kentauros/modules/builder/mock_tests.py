import os
import unittest

from .mock import get_default_mock_dist, get_dist_from_mock_config

MOCK_CONFIGS_FOUND = os.path.exists("/etc/mock/")
MOCK_F27_CONFIG_FOUND = os.path.exists("/etc/mock/fedora-27-x86_64.cfg")


class MockTest(unittest.TestCase):
    @unittest.skipUnless(MOCK_CONFIGS_FOUND, "No installed mock configurations were found.")
    def test_get_default_mock_dist(self):
        def_dist = get_default_mock_dist()

        self.assertIsInstance(def_dist, str)
        self.assertNotEqual(def_dist, "")

    @unittest.skipUnless(MOCK_F27_CONFIG_FOUND, "No configuration file for fedora 27 x86_64 found.")
    def test_get_dist_from_mock_config(self):
        def_dist = get_dist_from_mock_config(get_default_mock_dist())

        self.assertIsInstance(def_dist, str)
        self.assertNotEqual(def_dist, "")

        f27_dist = get_dist_from_mock_config("fedora-27-x86_64")

        self.assertIsInstance(f27_dist, str)
        self.assertNotEqual(f27_dist, "")

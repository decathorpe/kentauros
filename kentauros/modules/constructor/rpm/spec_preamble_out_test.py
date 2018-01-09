import unittest
from collections import OrderedDict

from data.test_packages import TEST_PACKAGE_GIT_SOURCE
from data.test_packages import TEST_PACKAGE_LOCAL_SOURCE
from data.test_packages import TEST_PACKAGE_URL_SOURCE
from .spec_preamble_out import get_spec_preamble


class SpecPreambleOutTest(unittest.TestCase):
    def test_get_git_spec_preamble(self):
        preamble = get_spec_preamble("git", TEST_PACKAGE_GIT_SOURCE)

        self.assertTrue("commit" in preamble.keys())
        self.assertTrue("shortcommit" in preamble.keys())
        self.assertTrue("date" in preamble.keys())
        self.assertTrue("time" in preamble.keys())

    def test_get_url_spec_preamble(self):
        preamble = get_spec_preamble("url", TEST_PACKAGE_URL_SOURCE)

        self.assertEqual(preamble, OrderedDict())

    def test_get_local_spec_preamble(self):
        preamble = get_spec_preamble("url", TEST_PACKAGE_LOCAL_SOURCE)

        self.assertEqual(preamble, OrderedDict())

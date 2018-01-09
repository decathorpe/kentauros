import unittest

from data.test_packages import TEST_PACKAGE_GIT_SOURCE
from data.test_packages import TEST_PACKAGE_LOCAL_SOURCE
from data.test_packages import TEST_PACKAGE_URL_SOURCE
from .spec_version_out import get_spec_version


class SpecSourceOutTest(unittest.TestCase):
    def test_get_git_spec_version(self):
        version = get_spec_version("git", TEST_PACKAGE_GIT_SOURCE)

        self.assertEqual(version, "1.0~%{date}.%{time}.git%{shortcommit}")

    def test_get_url_spec_version(self):
        version = get_spec_version("url", TEST_PACKAGE_URL_SOURCE)

        self.assertEqual(version, "1.0")

    def test_get_local_spec_version(self):
        version = get_spec_version("local", TEST_PACKAGE_LOCAL_SOURCE)

        self.assertEqual(version, "1.0")

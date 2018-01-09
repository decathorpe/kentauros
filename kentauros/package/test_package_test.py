import unittest

from data.test_packages import TEST_PACKAGE_GIT_SOURCE
from data.test_packages import TEST_PACKAGE_URL_SOURCE
from data.test_packages import TEST_PACKAGE_LOCAL_SOURCE
from kentauros.package import ReleaseType


class TestPackageTest(unittest.TestCase):
    def test_verify_git(self):
        package = TEST_PACKAGE_GIT_SOURCE
        verified = package.verify()
        self.assertTrue(verified.success)

    def test_verify_url(self):
        package = TEST_PACKAGE_URL_SOURCE
        verified = package.verify()
        self.assertTrue(verified.success)

    def test_verify_local(self):
        package = TEST_PACKAGE_LOCAL_SOURCE
        verified = package.verify()
        self.assertTrue(verified.success)

    def test_get_version_git(self):
        package = TEST_PACKAGE_GIT_SOURCE
        version = package.get_version()

        self.assertEqual(version, "1.0")

    def test_get_version_url(self):
        package = TEST_PACKAGE_URL_SOURCE
        version = package.get_version()

        self.assertEqual(version, "1.0")

    def test_get_version_local(self):
        package = TEST_PACKAGE_LOCAL_SOURCE
        version = package.get_version()

        self.assertEqual(version, "1.0")

    def test_get_release_type_git(self):
        package = TEST_PACKAGE_GIT_SOURCE
        release = package.get_release_type()

        self.assertEqual(release, ReleaseType.PRE)

    def test_get_release_type_url(self):
        package = TEST_PACKAGE_URL_SOURCE
        release = package.get_release_type()

        self.assertEqual(release, ReleaseType.STABLE)

    def test_get_release_type_local(self):
        package = TEST_PACKAGE_LOCAL_SOURCE
        release = package.get_release_type()

        self.assertEqual(release, ReleaseType.STABLE)

    def test_get_version_separator_git(self):
        package = TEST_PACKAGE_GIT_SOURCE

        separator = package.get_version_separator()
        expected = package.context.conf.get("main", "version_separator_pre")

        self.assertEqual(separator, expected)

    def test_get_version_separator_url(self):
        package = TEST_PACKAGE_URL_SOURCE

        separator = package.get_version_separator()
        expected = ""

        self.assertEqual(separator, expected)

    def test_get_version_separator_local(self):
        package = TEST_PACKAGE_LOCAL_SOURCE

        separator = package.get_version_separator()
        expected = ""

        self.assertEqual(separator, expected)

    def test_replace_vars_git(self):
        package = TEST_PACKAGE_GIT_SOURCE

        template = "%{name} %{version}"
        output = package.replace_vars(template)
        expected = "testpackage 1.0"

        self.assertEqual(output, expected)

    def test_replace_vars_url(self):
        package = TEST_PACKAGE_URL_SOURCE

        template = "%{name} %{version}"
        output = package.replace_vars(template)
        expected = "testpackage 1.0"

        self.assertEqual(output, expected)

    def test_replace_vars_local(self):
        package = TEST_PACKAGE_LOCAL_SOURCE

        template = "%{name} %{version}"
        output = package.replace_vars(template)
        expected = "testpackage 1.0"

        self.assertEqual(output, expected)

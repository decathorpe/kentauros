import unittest

from data.test_packages import TEST_PACKAGE_GIT_SOURCE
from data.test_packages import TEST_PACKAGE_LOCAL_SOURCE
from data.test_packages import TEST_PACKAGE_URL_SOURCE
from .spec_common import format_tag_line
from .spec_source_out import get_spec_source


class SpecSourceOutTest(unittest.TestCase):
    def test_get_git_spec_source(self):
        source = get_spec_source("git", TEST_PACKAGE_GIT_SOURCE)

        self.assertEqual(source, format_tag_line("Source0", "%{name}-%{version}.tar.gz"))

    def test_get_url_spec_source(self):
        source = get_spec_source("url", TEST_PACKAGE_URL_SOURCE)

        self.assertEqual(
            source,
            format_tag_line("Source0",
                            "https://decathorpe.com/testpackage/1.0/testpackage-1.0.tar.gz"))

    def test_get_local_spec_source(self):
        source = get_spec_source("local", TEST_PACKAGE_LOCAL_SOURCE)

        self.assertEqual(source, format_tag_line("Source0", "testpackage-1.0.tar.gz"))

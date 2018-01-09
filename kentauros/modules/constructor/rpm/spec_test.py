import os
import tempfile
import unittest

from data.test_packages import TEST_PACKAGE_GIT_SOURCE
from data.test_packages import TEST_PACKAGE_LOCAL_SOURCE
from data.test_packages import TEST_PACKAGE_URL_SOURCE
from data.test_specs import TEST_SPEC_GIT_SOURCE
from data.test_specs import TEST_SPEC_URL_SOURCE
from data.test_specs import TEST_SPEC_LOCAL_SOURCE
from .spec import RPMSpec, parse_release
from .spec_common import format_tag_line


class TestParseRelease(unittest.TestCase):
    def test_parse_release_too_simple(self):
        string = "1"

        num, text = parse_release(string)

        self.assertEqual(num, "1")
        self.assertEqual(text, "")

    def test_parse_release_simple(self):
        string = "12%{?dist}"

        num, text = parse_release(string)

        self.assertEqual(num, "12")
        self.assertEqual(text, "%{?dist}")

    def test_parse_release_stupid(self):
        string = "12.git%{shortcommit}%{?dist}"

        num, text = parse_release(string)

        self.assertEqual(num, "12")
        self.assertEqual(text, ".git%{shortcommit}%{?dist}")

    @unittest.expectedFailure
    def test_parse_release_fedorastupid(self):
        string = "0.6.%{commitdate}.git%{shortcommit}.1"

        num, text = parse_release(string)

        self.assertEqual(num, "0.6")
        self.assertEqual(text, ".%{commitdate}.git%{shortcommit}.1")


class TestSpecGit(unittest.TestCase):
    def setUp(self):
        self.file, self.path = tempfile.mkstemp()
        os.close(self.file)

        with open(self.path, "w") as file:
            file.write(TEST_SPEC_GIT_SOURCE)

    def tearDown(self):
        os.remove(self.path)
        self.file = None
        self.path = None

    def test_set_get_version_git(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_GIT_SOURCE)

        spec.set_version()
        self.assertEqual(spec.get_version(), spec.build_version_string())

    def test_bump_release_git(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_GIT_SOURCE)

        old = int(parse_release(spec.get_release())[0])
        spec.do_release_bump("Test")
        new = int(parse_release(spec.get_release())[0])

        self.assertEqual(old + 1, new)

    def test_reset_release_git(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_GIT_SOURCE)

        spec.do_release_reset()
        new = int(parse_release(spec.get_release())[0])

        self.assertEqual(new, 0)

    @unittest.expectedFailure
    def test_set_source_git(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_GIT_SOURCE)

        spec.set_source()

        source = spec.get_source()
        sources = spec.get_sources()

        self.assertTrue("Source0" in sources.keys())
        self.assertEqual(format_tag_line("Source0", sources["Source0"]), source)

    @unittest.skip
    def test_set_variables_git(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_GIT_SOURCE)

        spec.set_variables()

        # TODO


class TestSpecURL(unittest.TestCase):
    def setUp(self):
        self.file, self.path = tempfile.mkstemp()
        os.close(self.file)

        with open(self.path, "w") as file:
            file.write(TEST_SPEC_URL_SOURCE)

    def tearDown(self):
        os.remove(self.path)
        self.file = None
        self.path = None

    def test_set_get_version_url(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_URL_SOURCE)

        spec.set_version()
        self.assertEqual(spec.get_version(), spec.build_version_string())

    def test_bump_release_url(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_URL_SOURCE)

        old = int(parse_release(spec.get_release())[0])
        spec.do_release_bump("Test")
        new = int(parse_release(spec.get_release())[0])

        self.assertEqual(old + 1, new)

    def test_reset_release_url(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_URL_SOURCE)

        spec.do_release_reset()
        new = int(parse_release(spec.get_release())[0])

        self.assertEqual(new, 0)

    def test_set_source_url(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_URL_SOURCE)

        spec.set_source()

        source = spec.get_source()
        sources = spec.get_sources()

        self.assertTrue("Source0" in sources.keys())
        self.assertEqual(format_tag_line("Source0", sources["Source0"]), source)

    @unittest.skip
    def test_set_variables_url(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_URL_SOURCE)

        spec.set_variables()

        # TODO


class TestSpecLocal(unittest.TestCase):
    def setUp(self):
        self.file, self.path = tempfile.mkstemp()
        os.close(self.file)

        with open(self.path, "w") as file:
            file.write(TEST_SPEC_LOCAL_SOURCE)

    def tearDown(self):
        os.remove(self.path)
        self.file = None
        self.path = None

    def test_set_get_version_local(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_LOCAL_SOURCE)

        spec.set_version()
        self.assertEqual(spec.get_version(), spec.build_version_string())

    def test_bump_release_local(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_LOCAL_SOURCE)

        old = int(parse_release(spec.get_release())[0])
        spec.do_release_bump("Test")
        new = int(parse_release(spec.get_release())[0])

        self.assertEqual(old + 1, new)

    def test_reset_release_local(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_LOCAL_SOURCE)

        spec.do_release_reset()
        new = int(parse_release(spec.get_release())[0])

        self.assertEqual(new, 0)

    def test_set_source_local(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_LOCAL_SOURCE)

        spec.set_source()

        source = spec.get_source()
        sources = spec.get_sources()

        self.assertTrue("Source0" in sources.keys())
        self.assertEqual(format_tag_line("Source0", sources["Source0"]), source)

    @unittest.skip
    def test_set_variables_local(self):
        spec = RPMSpec(self.path, TEST_PACKAGE_LOCAL_SOURCE)

        spec.set_variables()

        # TODO

import unittest

from .spec_common import format_tag_line


class RPMSpecCommonTest(unittest.TestCase):
    def test_format_tagline_version(self):
        tag = "Version"
        value = "1.0.7"

        expected = "{}:        {}\n".format(tag, value)
        self.assertEqual(format_tag_line(tag, value), expected)

    def test_format_tagline_source(self):
        tag = "Source"
        value = "https://github.com/decathorpe/kentauros/archive/1.0.7/kentauros-1.0.7.tar.gz"

        expected = "{}:         {}\n".format(tag, value)
        self.assertEqual(format_tag_line(tag, value), expected)

    def test_format_tagline_release(self):
        tag = "Release"
        value = "1%{?dist}"

        expected = "{}:        {}\n".format(tag, value)
        self.assertEqual(format_tag_line(tag, value), expected)

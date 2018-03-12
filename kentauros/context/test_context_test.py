import os
import unittest

from .test_context import KtrTestContext


class KtrTestContextTest(unittest.TestCase):
    def test_init_and_del(self):
        context = KtrTestContext()
        basedir = context.basedir

        del context
        self.assertFalse(os.path.exists(basedir))

    def test_init_force_true(self):
        context = KtrTestContext(force=True)
        self.assertTrue(context.get_force())

    def test_init_force_false(self):
        context = KtrTestContext()
        self.assertFalse(context.get_force())

    def test_init_logfile_empty(self):
        context = KtrTestContext()
        self.assertEqual(context.get_logfile(), "")

    def test_init_logfile_nonempty(self):
        context = KtrTestContext(logfile="kentauros.log")
        self.assertEqual(context.get_logfile(), "kentauros.log")

    def test_init_message_empty(self):
        context = KtrTestContext()
        self.assertEqual(context.get_message(), "")

    def test_init_message_nonempty(self):
        context = KtrTestContext(message="NONEMPTY")
        self.assertEqual(context.get_message(), "NONEMPTY")

    def test_init_debug_true(self):
        context = KtrTestContext(debug=True)
        self.assertTrue(context.debug())

    def test_init_debug_false(self):
        context = KtrTestContext()
        self.assertFalse(context.debug())

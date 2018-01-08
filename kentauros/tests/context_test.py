import os
import unittest

from .testcontext import KtrTestContext


class KtrTestContextTest(unittest.TestCase):
    def test_init_and_del(self):
        context = KtrTestContext()
        test_dir = context.test_dir

        del context
        self.assertFalse(os.path.exists(test_dir))

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

    def test_init_warnings_true(self):
        context = KtrTestContext(warnings=True)
        self.assertTrue(context.warnings())

    def test_init_warnings_false(self):
        context = KtrTestContext()
        self.assertFalse(context.warnings())

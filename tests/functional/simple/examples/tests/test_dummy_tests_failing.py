import unittest


class FailingTestCases(unittest.TestCase):
    def test_assert_false(self):
        self.assertFalse(
            True, "This test is expected to fail because True is not False."
        )

    def test_assert_true(self):
        self.assertTrue(
            False, "This test is expected to fail because False is not True."
        )

    def test_assert_equal(self):
        self.assertEqual(
            2 + 2, 5, "This test is expected to fail because 2 + 2 is not equal to 5."
        )

    def test_assert_not_equal(self):
        self.assertNotEqual(
            3 * 4, 12, "This test is expected to fail because 3 * 4 is equal to 12."
        )

    def test_assert_raises_exception(self):
        with self.assertRaises(ValueError):
            # This test is expected to fail because no ValueError is raised here.
            pass

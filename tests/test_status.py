import unittest

from app.status import Status


class TestStatus(unittest.TestCase):
    def test_code(self):
        self.assertEqual(Status.OK.code, 200)
        self.assertEqual(Status.NOT_FOUND.code, 404)

    def test_text(self):
        self.assertEqual(Status.OK.text, "OK")
        self.assertEqual(Status.NOT_FOUND.text, "Not Found")

    def test_str_is_the_status_line_tail(self):
        self.assertEqual(str(Status.OK), "200 OK")
        self.assertEqual(str(Status.NOT_FOUND), "404 Not Found")

    def test_members_are_distinct(self):
        self.assertNotEqual(Status.OK, Status.NOT_FOUND)


if __name__ == "__main__":
    unittest.main()

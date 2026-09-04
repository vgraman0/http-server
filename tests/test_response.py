import dataclasses
import unittest

from app.response import Response
from app.status import Status


class TestResponse(unittest.TestCase):
    def test_body_defaults_to_empty(self):
        self.assertEqual(Response(Status.OK).body, "")

    def test_an_empty_body_omits_the_content_headers(self):
        self.assertEqual(Response(Status.OK).to_bytes(), b"HTTP/1.1 200 OK\r\n\r\n")

    def test_not_found(self):
        self.assertEqual(
            Response(Status.NOT_FOUND).to_bytes(), b"HTTP/1.1 404 Not Found\r\n\r\n"
        )

    def test_a_body_adds_the_content_headers(self):
        self.assertEqual(
            Response(Status.OK, "banana").to_bytes(),
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 6\r\n"
            b"\r\n"
            b"banana",
        )

    def test_content_length_matches_the_body(self):
        for body in ("a", "banana", "a longer body with spaces"):
            with self.subTest(body=body):
                head, _, sent = Response(Status.OK, body).to_bytes().partition(b"\r\n\r\n")
                self.assertIn(f"Content-Length: {len(sent)}".encode(), head)

    def test_is_frozen(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            Response(Status.OK).status = Status.NOT_FOUND

    def test_equality_is_by_value(self):
        self.assertEqual(Response(Status.OK, "banana"), Response(Status.OK, "banana"))
        self.assertNotEqual(Response(Status.OK, "banana"), Response(Status.OK, "apple"))

    @unittest.expectedFailure
    def test_content_length_counts_bytes_not_characters(self):
        # Known bug: to_bytes() uses len(body), which is characters, but encodes
        # as UTF-8. A multi-byte body advertises a Content-Length that is too
        # short. Remove this decorator once to_bytes() measures the encoded body.
        head, _, sent = Response(Status.OK, "café").to_bytes().partition(b"\r\n\r\n")
        self.assertIn(f"Content-Length: {len(sent)}".encode(), head)


if __name__ == "__main__":
    unittest.main()

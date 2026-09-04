import unittest

from app.request import Request


class TestRequestLine(unittest.TestCase):
    def test_parses_method_path_and_version(self):
        request = Request(b"GET /echo/banana HTTP/1.1\r\n\r\n")
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.path, "/echo/banana")
        self.assertEqual(request.version, "HTTP/1.1")

    def test_parses_other_methods(self):
        self.assertEqual(Request(b"POST / HTTP/1.1\r\n\r\n").method, "POST")

    def test_rejects_a_malformed_request_line(self):
        with self.assertRaises(ValueError):
            Request(b"GET /\r\n\r\n")


class TestRequestHeaders(unittest.TestCase):
    def test_no_headers(self):
        self.assertEqual(dict(Request(b"GET / HTTP/1.1\r\n\r\n").headers), {})

    def test_parses_several_headers(self):
        request = Request(
            b"GET / HTTP/1.1\r\n"
            b"Host: localhost:4221\r\n"
            b"User-Agent: curl/8.7.1\r\n"
            b"Accept: */*\r\n\r\n"
        )
        self.assertEqual(
            dict(request.headers),
            {
                "host": "localhost:4221",
                "user-agent": "curl/8.7.1",
                "accept": "*/*",
            },
        )

    def test_lowercases_names(self):
        request = Request(b"GET / HTTP/1.1\r\nUSER-AGENT: curl/8.7.1\r\n\r\n")
        self.assertEqual(request.headers["user-agent"], "curl/8.7.1")

    def test_strips_surrounding_whitespace_from_values(self):
        request = Request(b"GET / HTTP/1.1\r\nHost:   localhost   \r\n\r\n")
        self.assertEqual(request.headers["host"], "localhost")

    def test_keeps_colons_inside_a_value(self):
        request = Request(b"GET / HTTP/1.1\r\nHost: localhost:4221\r\n\r\n")
        self.assertEqual(request.headers["host"], "localhost:4221")

    def test_last_duplicate_wins(self):
        request = Request(b"GET / HTTP/1.1\r\nAccept: text/html\r\nAccept: */*\r\n\r\n")
        self.assertEqual(request.headers["accept"], "*/*")

    def test_a_line_without_a_colon_has_an_empty_value(self):
        request = Request(b"GET / HTTP/1.1\r\nBogus\r\n\r\n")
        self.assertEqual(request.headers["bogus"], "")

    def test_missing_header_raises(self):
        with self.assertRaises(KeyError):
            Request(b"GET / HTTP/1.1\r\n\r\n").headers["user-agent"]

    def test_headers_are_read_only(self):
        headers = Request(b"GET / HTTP/1.1\r\n\r\n").headers
        with self.assertRaises(TypeError):
            headers["host"] = "localhost"


class TestRequestBody(unittest.TestCase):
    def test_the_body_is_not_parsed_as_headers(self):
        request = Request(
            b"POST / HTTP/1.1\r\nHost: localhost\r\n\r\nAccept: not-a-header"
        )
        self.assertEqual(dict(request.headers), {"host": "localhost"})

    def test_a_blank_line_in_the_body_does_not_confuse_the_parser(self):
        request = Request(b"POST / HTTP/1.1\r\nHost: localhost\r\n\r\nfirst\r\n\r\nlast")
        self.assertEqual(request.path, "/")
        self.assertEqual(dict(request.headers), {"host": "localhost"})


if __name__ == "__main__":
    unittest.main()

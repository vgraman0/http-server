import unittest

from app.handler import EchoRoute, RootRoute, UserAgentRoute
from app.router import Router
from tests.support import exchange, start_server


class TestDocumentedRoutes(unittest.TestCase):
    """The four behaviours the README promises, over a real TCP socket."""

    @classmethod
    def setUpClass(cls):
        cls.address = start_server(Router(RootRoute(), EchoRoute(), UserAgentRoute()))

    def get(self, path: str, headers: str = "") -> bytes:
        return exchange(
            self.address, f"GET {path} HTTP/1.1\r\nHost: localhost\r\n{headers}\r\n".encode()
        )

    def test_root_is_ok_with_no_body(self):
        self.assertEqual(self.get("/"), b"HTTP/1.1 200 OK\r\n\r\n")

    def test_echo_returns_the_path_suffix(self):
        self.assertEqual(
            self.get("/echo/banana"),
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 6\r\n"
            b"\r\n"
            b"banana",
        )

    def test_user_agent_returns_the_header(self):
        self.assertTrue(
            self.get("/user-agent", "User-Agent: curl/8.7.1\r\n").endswith(
                b"\r\n\r\ncurl/8.7.1"
            )
        )

    def test_an_unknown_path_is_not_found(self):
        self.assertEqual(self.get("/nope"), b"HTTP/1.1 404 Not Found\r\n\r\n")

    def test_user_agent_without_the_header_is_not_answered(self):
        self.assertEqual(self.get("/user-agent"), b"")


if __name__ == "__main__":
    unittest.main()

import unittest

from app.handler import EchoRoute, Handler, Route, RootRoute, UserAgentRoute
from app.request import Request
from app.response import Response
from app.status import Status


def get(path: str, headers: str = "") -> Request:
    return Request(f"GET {path} HTTP/1.1\r\n{headers}\r\n".encode())


class TestContracts(unittest.TestCase):
    def test_handler_is_abstract(self):
        with self.assertRaises(TypeError):
            Handler()

    def test_route_is_abstract(self):
        with self.assertRaises(TypeError):
            Route()

    def test_every_route_is_a_handler(self):
        for route in (RootRoute(), EchoRoute(), UserAgentRoute()):
            with self.subTest(route=type(route).__name__):
                self.assertIsInstance(route, Handler)


class TestRootRoute(unittest.TestCase):
    def setUp(self):
        self.route = RootRoute()

    def test_matches_the_root(self):
        self.assertTrue(self.route.matches(get("/")))

    def test_does_not_match_anything_else(self):
        for path in ("/index.html", "/echo/banana", "//"):
            with self.subTest(path=path):
                self.assertFalse(self.route.matches(get(path)))

    def test_responds_ok_with_no_body(self):
        self.assertEqual(self.route.handle(get("/")), Response(Status.OK))


class TestEchoRoute(unittest.TestCase):
    def setUp(self):
        self.route = EchoRoute()

    def test_matches_the_echo_prefix(self):
        self.assertTrue(self.route.matches(get("/echo/banana")))

    def test_matches_an_empty_echo(self):
        self.assertTrue(self.route.matches(get("/echo/")))

    def test_does_not_match_without_the_trailing_slash(self):
        self.assertFalse(self.route.matches(get("/echo")))

    def test_does_not_match_a_different_path(self):
        for path in ("/", "/user-agent", "/echoes/banana"):
            with self.subTest(path=path):
                self.assertFalse(self.route.matches(get(path)))

    def test_echoes_the_rest_of_the_path(self):
        self.assertEqual(
            self.route.handle(get("/echo/banana")), Response(Status.OK, "banana")
        )

    def test_echoes_remaining_slashes_verbatim(self):
        self.assertEqual(
            self.route.handle(get("/echo/a/b/c")), Response(Status.OK, "a/b/c")
        )

    def test_echoes_an_empty_string(self):
        self.assertEqual(self.route.handle(get("/echo/")), Response(Status.OK, ""))

    def test_strips_only_the_leading_prefix(self):
        self.assertEqual(
            self.route.handle(get("/echo/echo/banana")),
            Response(Status.OK, "echo/banana"),
        )


class TestUserAgentRoute(unittest.TestCase):
    def setUp(self):
        self.route = UserAgentRoute()

    def test_matches_the_exact_path(self):
        self.assertTrue(self.route.matches(get("/user-agent")))

    def test_does_not_match_a_longer_path(self):
        for path in ("/user-agent/", "/user-agent/extra", "/user"):
            with self.subTest(path=path):
                self.assertFalse(self.route.matches(get(path)))

    def test_returns_the_user_agent_header(self):
        request = get("/user-agent", "User-Agent: curl/8.7.1\r\n")
        self.assertEqual(self.route.handle(request), Response(Status.OK, "curl/8.7.1"))

    def test_looks_the_header_up_case_insensitively(self):
        request = get("/user-agent", "USER-AGENT: curl/8.7.1\r\n")
        self.assertEqual(self.route.handle(request), Response(Status.OK, "curl/8.7.1"))

    def test_raises_when_the_header_is_absent(self):
        with self.assertRaises(KeyError):
            self.route.handle(get("/user-agent"))


if __name__ == "__main__":
    unittest.main()

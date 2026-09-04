import unittest

from app.handler import Handler, Route
from app.request import Request
from app.response import Response
from app.router import Router
from app.status import Status


class StubRoute(Route):
    def __init__(self, matching: bool, body: str = ""):
        self.matching = matching
        self.body = body
        self.handled: list[Request] = []

    def matches(self, request: Request) -> bool:
        return self.matching

    def handle(self, request: Request) -> Response:
        self.handled.append(request)
        return Response(Status.OK, self.body)


def get(path: str = "/") -> Request:
    return Request(f"GET {path} HTTP/1.1\r\n\r\n".encode())


class TestRouter(unittest.TestCase):
    def test_dispatches_to_the_matching_route(self):
        miss, hit = StubRoute(False), StubRoute(True, "hit")
        self.assertEqual(Router(miss, hit).handle(get()), Response(Status.OK, "hit"))
        self.assertEqual(miss.handled, [])
        self.assertEqual(len(hit.handled), 1)

    def test_the_first_match_wins(self):
        first, second = StubRoute(True, "first"), StubRoute(True, "second")
        self.assertEqual(
            Router(first, second).handle(get()), Response(Status.OK, "first")
        )
        self.assertEqual(second.handled, [])

    def test_passes_the_request_through_untouched(self):
        route = StubRoute(True)
        request = get("/echo/banana")
        Router(route).handle(request)
        self.assertIs(route.handled[0], request)

    def test_no_match_is_not_found(self):
        self.assertEqual(
            Router(StubRoute(False)).handle(get()), Response(Status.NOT_FOUND)
        )

    def test_an_empty_router_is_not_found(self):
        self.assertEqual(Router().handle(get()), Response(Status.NOT_FOUND))

    def test_is_itself_a_handler_so_the_server_accepts_it(self):
        self.assertIsInstance(Router(), Handler)


if __name__ == "__main__":
    unittest.main()

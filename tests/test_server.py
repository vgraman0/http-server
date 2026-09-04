import socket
import unittest

from app.response import Response
from app.server import Server
from app.status import Status
from tests.support import RaisingHandler, RecordingHandler, exchange, start_server

GET_ROOT = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"


class TestHandleConnection(unittest.TestCase):
    def setUp(self):
        self.client, self.conn = socket.socketpair()
        self.addCleanup(self.client.close)
        self.addCleanup(self.conn.close)

    def serve_once(self, handler):
        Server("localhost", 0, handler)._handle(self.conn, ("localhost", 0))

    def test_writes_the_handler_response_to_the_socket(self):
        self.client.sendall(GET_ROOT)
        self.serve_once(RecordingHandler(Response(Status.OK, "banana")))
        self.assertEqual(
            self.client.recv(1024),
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 6\r\n"
            b"\r\n"
            b"banana",
        )

    def test_hands_the_parsed_request_to_the_handler(self):
        handler = RecordingHandler(Response(Status.OK))
        self.client.sendall(b"GET /echo/banana HTTP/1.1\r\nHost: localhost\r\n\r\n")
        self.serve_once(handler)
        self.assertEqual([r.path for r in handler.requests], ["/echo/banana"])

    def test_closes_the_connection_after_responding(self):
        self.client.sendall(GET_ROOT)
        self.serve_once(RecordingHandler(Response(Status.OK)))
        self.client.recv(1024)
        self.assertEqual(self.client.recv(1024), b"")

    def test_ignores_a_connection_that_sends_nothing(self):
        handler = RecordingHandler(Response(Status.OK))
        self.client.shutdown(socket.SHUT_WR)
        self.serve_once(handler)
        self.assertEqual(handler.requests, [])


class TestAcceptLoop(unittest.TestCase):
    def test_serves_requests_over_a_real_socket(self):
        address = start_server(RecordingHandler(Response(Status.OK, "banana")))
        self.assertTrue(exchange(address, GET_ROOT).endswith(b"\r\n\r\nbanana"))

    def test_keeps_serving_after_each_connection_closes(self):
        address = start_server(RecordingHandler(Response(Status.OK, "banana")))
        for _ in range(3):
            self.assertTrue(exchange(address, GET_ROOT).endswith(b"banana"))

    def test_survives_a_handler_that_raises(self):
        handler = RecordingHandler(Response(Status.OK, "banana"))
        address = start_server(_FlakyHandler(handler))
        self.assertEqual(exchange(address, GET_ROOT), b"")
        self.assertTrue(exchange(address, GET_ROOT).endswith(b"banana"))

    def test_survives_an_unparsable_request(self):
        address = start_server(RecordingHandler(Response(Status.OK, "banana")))
        self.assertEqual(exchange(address, b"not http\r\n\r\n"), b"")
        self.assertTrue(exchange(address, GET_ROOT).endswith(b"banana"))


class _FlakyHandler(RaisingHandler):
    def __init__(self, fallback):
        self.fallback = fallback
        self.calls = 0

    def handle(self, request):
        self.calls += 1
        if self.calls == 1:
            return super().handle(request)
        return self.fallback.handle(request)


if __name__ == "__main__":
    unittest.main()

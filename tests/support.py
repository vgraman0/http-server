import socket
import threading
import time

from app.handler import Handler
from app.request import Request
from app.response import Response

Address = tuple[str, int]

TIMEOUT = 2.0


class RecordingHandler(Handler):
    def __init__(self, response: Response):
        self.response = response
        self.requests: list[Request] = []

    def handle(self, request: Request) -> Response:
        self.requests.append(request)
        return self.response


class RaisingHandler(Handler):
    def handle(self, request: Request) -> Response:
        raise RuntimeError("boom")


def start_server(handler: Handler) -> Address:
    # Server has no shutdown, so the thread is a daemon and dies with the process.
    from app.server import Server

    address = ("localhost", _free_port())
    thread = threading.Thread(
        target=Server(*address, handler).serve_forever, daemon=True
    )
    thread.start()
    _wait_until_listening(address)
    return address


def exchange(address: Address, raw: bytes) -> bytes:
    with socket.create_connection(address, timeout=TIMEOUT) as sock:
        sock.sendall(raw)
        chunks = []
        while chunk := sock.recv(1024):
            chunks.append(chunk)
        return b"".join(chunks)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]


def _wait_until_listening(address: Address) -> None:
    deadline = time.monotonic() + TIMEOUT
    while time.monotonic() < deadline:
        try:
            socket.create_connection(address, timeout=0.1).close()
            return
        except OSError:
            time.sleep(0.01)
    raise TimeoutError(f"server never started listening on {address}")

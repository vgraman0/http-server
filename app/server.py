import socket

from app.handler import Handler
from app.request import Request


class Server:
    def __init__(self, host: str, port: int, handler: Handler):
        self.host = host
        self.port = port
        self.handler = handler

    def serve_forever(self):
        with socket.create_server((self.host, self.port), reuse_port=True) as sock:
            while True:
                conn, addr = sock.accept()
                try:
                    self._handle(conn, addr)
                except Exception as e:
                    print(f"error handler {addr}: {e}")

    def _handle(self, conn, addr):
        with conn:
            data = conn.recv(1024)
            if not data:
                return
            conn.sendall(self.handler.handle(Request(data)).to_bytes())

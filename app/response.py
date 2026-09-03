from dataclasses import dataclass

from app.status import Status


@dataclass(frozen=True)
class Response:
    status: Status
    body: str = ""

    def to_bytes(self) -> bytes:
        lines = [f"HTTP/1.1 {self.status}"]
        if self.body:
            lines += ["Content-Type: text/plain", f"Content-Length: {len(self.body)}"]
        return ("\r\n".join(lines) + "\r\n\r\n" + self.body).encode()

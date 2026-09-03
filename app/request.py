from types import MappingProxyType
from typing import Mapping


class Request:
    def __init__(self, data: bytes):
        head = data.decode().split("\r\n\r\n", 1)[0]
        request_line, *header_lines = head.split("\r\n")
        self._method, self._path, self._version = request_line.split(" ")
        self._headers = MappingProxyType(
            {
                key.lower(): value.strip()
                for key, _, value in (line.partition(":") for line in header_lines)
            }
        )

    @property
    def method(self) -> str:
        return self._method

    @property
    def path(self) -> str:
        return self._path

    @property
    def version(self) -> str:
        return self._version

    @property
    def headers(self) -> Mapping[str, str]:
        return self._headers

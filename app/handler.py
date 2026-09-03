from abc import ABC, abstractmethod

from app.request import Request
from app.response import Response


class Handler(ABC):
    @abstractmethod
    def handle(self, request: Request) -> Response:
        pass


class Route(Handler):
    @abstractmethod
    def matches(self, request: Request) -> bool:
        pass

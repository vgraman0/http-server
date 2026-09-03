from abc import ABC, abstractmethod

from app.request import Request
from app.response import Response
from app.status import Status


class Handler(ABC):
    @abstractmethod
    def handle(self, request: Request) -> Response:
        pass


class Route(Handler):
    @abstractmethod
    def matches(self, request: Request) -> bool:
        pass


class RootRoute(Route):
    def matches(self, request: Request) -> bool:
        return request.path == "/"

    def handle(self, request: Request) -> Response:
        return Response(Status.OK)


class EchoRoute(Route):
    PREFIX = "/echo/"

    def matches(self, request: Request) -> bool:
        return request.path.startswith(self.PREFIX)

    def handle(self, request: Request) -> Response:
        return Response(Status.OK, request.path.removeprefix(self.PREFIX))


class UserAgentRoute(Route):
    USER_AGENT = "user-agent"
    PATH = f"/{USER_AGENT}"

    def matches(self, request: Request) -> bool:
        return request.path == self.PATH

    def handle(self, request: Request) -> Response:
        body = request.headers[self.USER_AGENT]
        return Response(Status.OK, body)

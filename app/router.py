from app.handler import Handler, Route
from app.request import Request
from app.response import Response
from app.status import Status


class Router(Handler):
    def __init__(self, *routes: Route):
        self._routes = routes

    def handle(self, request: Request) -> Response:
        for route in self._routes:
            if route.matches(request):
                return route.handle(request)
        return Response(Status.NOT_FOUND)

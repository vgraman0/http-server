from app.handler import EchoRoute, RootRoute, UserAgentRoute
from app.router import Router
from app.server import Server

HOST = "localhost"
PORT = 4221


def main():
    router = Router(RootRoute(), EchoRoute(), UserAgentRoute())
    Server(HOST, PORT, router).serve_forever()


if __name__ == "__main__":
    main()

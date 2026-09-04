# HTTP Server

An HTTP/1.1 server written from scratch on the Python standard library.
No frameworks, no third-party dependencies.

## Running

```sh
uv run -m app.main
```

The server listens on `localhost:4221`.

```sh
curl -i localhost:4221/echo/banana
```

## Tests

```sh
uv run -m unittest discover
```

Standard library `unittest`, no test dependencies. `tests/test_server.py` and
`tests/test_routes_end_to_end.py` exercise a real server over a real TCP socket.

## Routes

| Path          | Response                                    |
| ------------- | ------------------------------------------- |
| `/`           | `200 OK`, empty body                        |
| `/echo/<str>` | `200 OK`, `<str>` as the body               |
| `/user-agent` | `200 OK`, the request's `User-Agent` header |
| anything else | `404 Not Found`                             |

## Layout

| Module        | Responsibility                                       |
| ------------- | ---------------------------------------------------- |
| `status.py`   | Status codes paired with their reason phrases        |
| `request.py`  | Parses raw bytes into method, path, version, headers |
| `response.py` | Serializes a status and body to the wire format      |
| `handler.py`  | The `Handler` and `Route` contracts, and the routes  |
| `router.py`   | Dispatches to the first route that matches           |
| `server.py`   | Accept loop over a TCP socket                        |
| `main.py`     | Composition root: builds the router, starts serving  |

`Server` takes any `Handler`, and `Router` is itself a `Handler`, so
routing is swappable without touching the socket code.

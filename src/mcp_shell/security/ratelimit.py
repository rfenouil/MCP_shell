import time
from collections import defaultdict

from starlette.types import ASGIApp, Receive, Scope, Send


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp, limit_per_minute: int = 120) -> None:
        self.app = app
        self.limit = limit_per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        client = scope.get("client")
        ip = client[0] if client else "unknown"
        now = time.monotonic()
        hits = [t for t in self._hits[ip] if now - t < 60]
        if len(hits) >= self.limit:
            self._hits[ip] = hits
            body = b'{"error": "rate limit exceeded"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode()),
                        (b"retry-after", b"60"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return
        hits.append(now)
        self._hits[ip] = hits
        await self.app(scope, receive, send)

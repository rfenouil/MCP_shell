from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from mcp_shell.security.ratelimit import RateLimitMiddleware


def make_client(limit: int) -> TestClient:
    async def ok(request):
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/mcp", ok, methods=["POST"])])
    return TestClient(RateLimitMiddleware(app, limit_per_minute=limit))


def test_under_limit_accepted() -> None:
    client = make_client(limit=3)
    for _ in range(3):
        assert client.post("/mcp", json={}).status_code == 200


def test_over_limit_rejected_with_429() -> None:
    client = make_client(limit=2)
    assert client.post("/mcp", json={}).status_code == 200
    assert client.post("/mcp", json={}).status_code == 200
    response = client.post("/mcp", json={})
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"

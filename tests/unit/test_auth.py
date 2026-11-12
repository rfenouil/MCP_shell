from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from mcp_shell.security.auth import BearerAuthMiddleware


def make_client(token: str = "secret-token") -> TestClient:
    async def ok(request):
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/mcp", ok, methods=["POST"])])
    return TestClient(BearerAuthMiddleware(app, token))


def test_missing_token_rejected() -> None:
    client = make_client()
    response = client.post("/mcp", json={})
    assert response.status_code == 401


def test_wrong_token_rejected() -> None:
    client = make_client()
    response = client.post("/mcp", json={}, headers={"authorization": "Bearer wrong"})
    assert response.status_code == 401


def test_valid_token_accepted() -> None:
    client = make_client()
    response = client.post("/mcp", json={}, headers={"authorization": "Bearer secret-token"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}

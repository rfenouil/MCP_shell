# Technical specifications — mcp-shell

## 1. Stack

| Layer | Technology |
|---|---|
| Language | Python ≥ 3.11 (target 3.12) |
| MCP SDK | `mcp` (MCPServer), `stdio` and `streamable-http` transports |
| CLI | typer (click wrapper) |
| Configuration | pydantic-settings (env vars + CLI) |
| Logs | structlog, **stderr only** (stdout reserved for JSON-RPC in stdio) |
| Execution | `asyncio.create_subprocess_shell`, `start_new_session=True`, process-group kill on timeout |
| Packaging | pyproject.toml + hatchling, entry point `mcp-shell = mcp_shell.server:main` |
| Env / deps | uv (venv, lock, build) |
| Lint / format | ruff |
| Tests | pytest + pytest-asyncio; integration via MCP SDK client (`ClientSession`, stdio) |

## 2. Layered architecture

```
Chat agent (MCP client)
        │  stdio or Streamable HTTP (via nginx HTTPS)
        ▼
┌─────────────────────────────┐
│  server.py                  │  typer CLI, MCPServer wiring, transport choice
│  tools/ (1 module = 1 tool) │  pydantic validation + delegation
├─────────────────────────────┤
│  core/                      │  executor.py (subprocess, timeout, truncation)
│                             │  paths.py (root confinement)
├─────────────────────────────┤
│  security/                  │  policy.py (filtered env, allowlist, limits)
│                             │  auth.py (bearer middleware, HTTP mode)
│                             │  audit.py (structlog command journal)
└─────────────────────────────┘
        │
        ▼
   Shell / FS (confined to settings.root_dir)
```

Rules: dependencies only downward (`tools` → `core`/`security` → `config`); injected configuration (no globals); thin tools.

## 3. Configuration model (`config.py`, pydantic-settings)

- `root_dir`: confinement root (default: current directory).
- `command_timeout`: default per-command timeout, seconds (default 120).
- `max_output_bytes`: output truncation (default 100,000).
- `allowed_commands` / `denied_commands`: optional control lists.
- `mcp_shell_token`: bearer token required in HTTP mode (POC).
- `host`, `port`: loopback bind by default (`127.0.0.1:8000`).

Env prefix: `MCP_SHELL_`. E.g.: `MCP_SHELL_ROOT_DIR`, `MCP_SHELL_TOKEN`.

## 4. Transport

- **stdio**: default, for local dev and automated tests. Logs strictly on stderr.
- **streamable-http**: `mcp.streamable_http_app()` wrapped in the bearer auth middleware, served by uvicorn on `host:port` (loopback by default; nginx bridges public HTTPS). `stateless_http` option considered to simplify proxying.

## 5. Security (remote deployment)

- TLS terminated by nginx (Let's Encrypt); MCP server binds 127.0.0.1 only.
- Application auth: bearer token (POC) → OAuth2/OIDC (target); mTLS via nginx (`ssl_verify_client on`) as defense in depth.
- Headers: no wildcard CORS; request size limits; rate limiting.
- structlog audit: command, cwd, return code, client identity.
- In test sandboxes: servers launched on loopback only, ephemeral ports, never publicly exposed.

## 6. Development phases

0. Foundation (structure, pyproject, uv, ruff, pytest) — delivered with the POC.
1. Core POC: 5 tools + confinement + safe execution, stdio transport + `--transport http` flag.
2. Security: bearer HTTP auth, hardened policy, audit, bypass tests.
3. Robustness: structured errors, cancellation, (optional) persistent shell session.
4. Packaging: hatchling build, `uvx`, README, client config examples.
5. CI: automated unit/integration/security tests.

# Strategic decisions (ADRs) — mcp-shell

Each decision lists the options considered during discussion, the chosen decision and its justification. Goal: another agent understands the "why" without rereading the whole conversation.

## ADR-1 — Generic shell rather than granular tools

- **Options**: (a) one MCP tool per action (`create_file`, `run_tests`, `git_commit`…); (b) a generic `run_command` shell tool + dedicated file read/write tools.
- **Decision**: (b), functional equivalent of the *bash tool* in Claude Code / Codex.
- **Justification**: the target agent supports MCP but has no TUI; the shell covers git, tests, builds, etc. without enumerating every action. Dedicated file tools remain more reliable than `cat`/`echo >`.

## ADR-2 — Python + official MCP SDK (v2)

- **Options**: Python, TypeScript, other.
- **Decision**: Python ≥ 3.11 (tested on 3.12), SDK `mcp>=2.3,<3`.
- **Justification**: mature official SDK, native asyncio for non-blocking execution. **Important note**: in SDK v2, `FastMCP` is renamed `MCPServer` (`from mcp.server.mcpserver import MCPServer`) — do not write v1 code.

## ADR-3 — CLI with typer (click wrapper)

- **Options**: plain click, typer, argparse.
- **Decision**: typer.
- **Justification**: less boilerplate than click, same ecosystem; click remains acceptable if full control is needed.

## ADR-4 — structlog logs, strictly on stderr

- **Options**: stdlib logging, structlog.
- **Decision**: structlog, JSON format, ISO timestamps, **stderr only**.
- **Justification**: structured audit of executed commands; in stdio transport, stdout is reserved for JSON-RPC, any print to stdout would break the protocol.

## ADR-5 — Two transports: stdio (default) + Streamable HTTP

- **Options**: stdio only (initial position); stdio + HTTP.
- **Decision**: both, via `--transport stdio|http`. stdio for dev/tests, Streamable HTTP (`mcp.streamable_http_app()` + uvicorn) for remote deployment.
- **Justification**: the client agent runs on a remote machine. The CLI flag keeps a single codebase.

## ADR-6 — Remote deployment: TLS by nginx, application auth, loopback bind

- **Options**: nginx terminates HTTPS but does no auth; auth left to the MCP server.
- **Decision**: MCP server binds `127.0.0.1` only; nginx alone is publicly exposed (443, Let's Encrypt); **mandatory server-side auth in HTTP mode**: static bearer token (POC, `MCP_SHELL_TOKEN`, constant-time comparison via `hmac.compare_digest`), OAuth2/OIDC as target; mTLS via nginx (`ssl_verify_client on`) as defense in depth. Never plain HTTP outside loopback, no wildcard CORS.
- **Justification**: the agent is on a remote machine, so the server must never be directly exposed.

## ADR-7 — pip-installable packaging from Phase 0

- **Options**: packaging deferred to the end of the project; packaging from the start.
- **Decision**: `pyproject.toml` + hatchling + entry point `mcp-shell = mcp_shell.server:main` from the start; installable via `pip`/`uvx`.
- **Justification**: avoids a big packaging refactor at the end; the POC is already a real package.

## ADR-8 — Layered architecture, injected configuration

- **Options**: monolithic code; strict layers.
- **Decision**: `tools/` → `core/` + `security/` → `config.py` (pydantic-settings, env prefix `MCP_SHELL_`). Downward-only dependencies, injected `Settings`, thin tools (pydantic validation then delegation).
- **Justification**: each layer testable on its own; security does not depend on the MCP layer.

## ADR-9 — Shell security: confinement + filtered environment + control lists

- **Options**: free execution; strict confinement.
- **Decision**: all paths resolved against a root (`resolve_confined`, rejection of `..` and absolute paths outside the root); per-command timeout with process-group kill (`start_new_session=True` + `os.killpg`); output truncation (`max_output_bytes`); filtered env (`SAFE_ENV_KEYS`, no secrets passed); optional `allowed_commands`/`denied_commands`.
- **Justification**: minimal attack surface even in the POC.

## ADR-10 — Work persistence outside the sandbox: GitHub + Mistral library snapshot

- **Options**: sandbox only (destroyed at session end); GitHub repository.
- **Decision**: deliver to **`rfenouil/MCP_shell`** (`main` branch, commit `38f7279`). Constraint encountered: in a session where the GitHub MCP connector was not injected at startup, `gh auth login` can be blocked; the device flow `gh auth login --web --scopes repo` worked, and the push is done via `git -c credential.helper='!gh auth git-credential' push <explicit-url>` (the token never transits through the chat). A full snapshot (code + docs) is also stored in the Mistral library "mcp-shell".
- **Justification**: the sandbox is ephemeral; GitHub is the only reliable durable storage. Never push to a repository belonging to another project.

## ADR-11 — Tests: stdio for integration, loopback for HTTP

- **Options**: test everything over HTTP; test everything over stdio.
- **Decision**: MCP integration via `ClientSession` over **stdio** (fast, local); the auth middleware unit-tested via `TestClient` (no real network server). In sandboxes, never a public listener.
- **Justification**: reproducible, fast, no network exposure.

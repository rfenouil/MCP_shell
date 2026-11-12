# mcp-shell

MCP server giving a chat agent (no TUI) structured, confined and auditable shell access — the functional equivalent of the *bash tool* in Claude Code / Codex.

See [docs/01-cahier-des-charges-fonctionnel.md](docs/01-cahier-des-charges-fonctionnel.md) and [docs/02-specifications-techniques.md](docs/02-specifications-techniques.md).

## Taking over the project from another agent

Read in this order: `docs/04-plan-de-developpement.md` (status + resume commands) → `docs/03-decisions-strategiques.md` (ADRs, the "why" behind the choices) → `docs/01` (functional) → `docs/02` (technical).

## Installation (dev)

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Running

```bash
mcp-shell                          # stdio transport (default)
mcp-shell --transport http         # Streamable HTTP on 127.0.0.1:8000 (behind nginx in prod)
```

Configuration via `MCP_SHELL_`-prefixed environment variables (e.g. `MCP_SHELL_ROOT_DIR`, `MCP_SHELL_TOKEN`).

## Tests

```bash
pytest
```

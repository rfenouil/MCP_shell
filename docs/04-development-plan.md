# Development plan — mcp-shell

## Current state (commit `94ba591` on `rfenouil/MCP_shell`)

Phases 0 and 1 delivered: functional POC, tests passing, ruff clean, wheel build OK. Phase 2 in progress.

## Phases

| Phase | Content | Status | Next concrete action |
|---|---|---|---|
| 0. Foundation | structure, pyproject (hatchling), uv, ruff, pytest | ✅ | — |
| 1. Core POC | 5 MCP tools, confinement, safe execution, stdio + `--transport http` | ✅ | — |
| 2. Security | bearer HTTP ✅, policy, audit ✅, glob pattern validation ✅, rate limiting ✅, bypass tests (symlink, `..` patterns) ✅, nginx deployment doc ✅ (`05-deployment-nginx.md`) | 🔶 | OAuth2/OIDC target, mTLS, load testing |
| 3. Robustness | structured errors, cancellation | ⬜ | handle signals cleanly, structured MCP errors, optional persistent shell session |
| 4. Packaging | hatchling ✅, wheel ✅ | 🔶 | client config examples (`.mcp.json` for Claude Code, `config.toml` for Codex), test `uvx mcp-shell` |
| 5. CI | GitHub Actions | ⬜ | pytest + ruff workflow on `rfenouil/MCP_shell` |

## Resume commands

```bash
git clone https://github.com/rfenouil/MCP_shell.git && cd MCP_shell
uv venv && uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest -q          # 20 tests
.venv/bin/python -m ruff check src tests
.venv/bin/mcp-shell --help              # CLI
.venv/bin/mcp-shell                      # MCP server over stdio
```

## Recommended order going forward

1. **Phase 2** (security) before any external demo — bypass tests first.
2. Phase 4 (client config) to plug in a real agent.
3. Phases 3 and 5 iteratively.

## Points of attention for a new agent

- MCP SDK **v2**: `MCPServer`, not `FastMCP` (see ADR-2).
- Logs **stderr only** (ADR-4).
- In HTTP mode, token required (`--token` / `MCP_SHELL_TOKEN`), loopback bind (ADR-6).
- Never push anywhere but `rfenouil/MCP_shell` (ADR-10).
- Reference docs: `01-functional-requirements.md`, `02-technical-specifications.md`, `03-strategic-decisions.md`.

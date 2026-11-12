# mcp-shell

Serveur MCP donnant à un agent de chat (sans TUI) un accès shell structuré, confiné et auditable — équivalent du *bash tool* de Claude Code / Codex.

Voir [docs/01-cahier-des-charges-fonctionnel.md](docs/01-cahier-des-charges-fonctionnel.md) et [docs/02-specifications-techniques.md](docs/02-specifications-techniques.md).

## Installation (dev)

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Lancement

```bash
mcp-shell                          # transport stdio (défaut)
mcp-shell --transport http         # Streamable HTTP sur 127.0.0.1:8000 (derrière nginx en prod)
```

Configuration par variables d'environnement préfixées `MCP_SHELL_` (ex. `MCP_SHELL_ROOT_DIR`, `MCP_SHELL_TOKEN`).

## Tests

```bash
pytest
```

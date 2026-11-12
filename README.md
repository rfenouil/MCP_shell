# mcp-shell

Serveur MCP donnant à un agent de chat (sans TUI) un accès shell structuré, confiné et auditable — équivalent du *bash tool* de Claude Code / Codex.

Voir [docs/01-cahier-des-charges-fonctionnel.md](docs/01-cahier-des-charges-fonctionnel.md) et [docs/02-specifications-techniques.md](docs/02-specifications-techniques.md).

## Reprise du projet par un autre agent

Lire dans l'ordre : `docs/04-plan-de-developpement.md` (etat + commandes de reprise) → `docs/03-decisions-strategiques.md` (ADR, le « pourquoi » des choix) → `docs/01` (fonctionnel) → `docs/02` (technique).

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

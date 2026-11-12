# Plan de développement — mcp-shell

## État actuel (commit `38f7279` sur `rfenouil/MCP_shell`)

Phases 0 et 1 livrées : POC fonctionnel, 20 tests OK, ruff clean, wheel build OK.

## Phases

| Phase | Contenu | État | Prochaine action concrète |
|---|---|---|---|
| 0. Fondation | structure, pyproject (hatchling), uv, ruff, pytest | ✅ | — |
| 1. POC core | 5 tools MCP, confinement, exécution sûre, stdio + `--transport http` | ✅ | — |
| 2. Sécurité | bearer HTTP ✅, policy, audit ✅ | 🔶 | tests de contournement du confinement (symlinks, encodages, chemins absolus), config nginx type (TLS + proxy_pass 127.0.0.1:8000), doc mTLS, rate limiting |
| 3. Robustesse | erreurs structurées, annulation | ⬜ | gérer proprement les signaux, reporter les erreurs MCP structurées, option session shell persistante |
| 4. Packaging | hatchling ✅, wheel ✅ | 🔶 | exemples de config client (`.mcp.json` pour Claude Code, `config.toml` pour Codex), test `uvx mcp-shell` |
| 5. CI | GitHub Actions | ⬜ | workflow pytest + ruff sur `rfenouil/MCP_shell` |

## Commandes de reprise

```bash
git clone https://github.com/rfenouil/MCP_shell.git && cd MCP_shell
uv venv && uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest -q          # 20 tests
.venv/bin/python -m ruff check src tests
.venv/bin/mcp-shell --help              # CLI
.venv/bin/mcp-shell                      # serveur MCP en stdio
```

## Ordre conseillé pour la suite

1. **Phase 2** (sécurité) avant toute démo externe — tests de contournement prioritaires.
2. Phase 4 (config client) pour brancher un vrai agent.
3. Phases 3 et 5 par itérations.

## Points d'attention pour un nouvel agent

- SDK MCP **v2** : `MCPServer`, pas `FastMCP` (voir ADR-2).
- Logs **stderr uniquement** (ADR-4).
- En mode HTTP, token obligatoire (`--token` / `MCP_SHELL_TOKEN`), bind loopback (ADR-6).
- Ne jamais pousser ailleurs que `rfenouil/MCP_shell` (ADR-10).
- Docs de référence : `01-cahier-des-charges-fonctionnel.md`, `02-specifications-techniques.md`, `03-decisions-strategiques.md`.

# Spécifications techniques — mcp-shell

## 1. Stack

| Couche | Technologie |
|---|---|
| Langage | Python ≥ 3.11 (cible 3.12) |
| SDK MCP | `mcp` (FastMCP), transports `stdio` et `streamable-http` |
| CLI | typer (surcouche click) |
| Configuration | pydantic-settings (env vars + CLI) |
| Logs | structlog, sortie **stderr uniquement** (stdout réservé au JSON-RPC en stdio) |
| Exécution | `asyncio.create_subprocess_shell`, `start_new_session=True`, kill du process group au timeout |
| Packaging | pyproject.toml + hatchling, entry point `mcp-shell = mcp_shell.server:main` |
| Env / deps | uv (venv, lock, build) |
| Lint / format | ruff |
| Tests | pytest + pytest-asyncio ; intégration via client MCP SDK (`ClientSession`, stdio) |

## 2. Architecture en couches

```
Agent de chat (client MCP)
        │  stdio ou Streamable HTTP (via nginx HTTPS)
        ▼
┌─────────────────────────────┐
│  server.py                  │  CLI typer, wiring FastMCP, choix du transport
│  tools/ (1 module = 1 tool) │  validation pydantic + délégation
├─────────────────────────────┤
│  core/                      │  executor.py (subprocess, timeout, troncature)
│                             │  paths.py (confinement racine)
├─────────────────────────────┤
│  security/                  │  policy.py (env filtré, allowlist, limites)
│                             │  auth.py (middleware bearer, mode HTTP)
│                             │  audit.py (journal structlog des commandes)
└─────────────────────────────┘
        │
        ▼
   Shell / FS (confiné à settings.root_dir)
```

Règles : dépendances uniquement vers le bas (`tools` → `core`/`security` → `config`) ; configuration injectée (pas de globales) ; tools minces.

## 3. Modèle de configuration (`config.py`, pydantic-settings)

- `root_dir` : racine de confinement (défaut : répertoire courant).
- `command_timeout` : timeout par défaut des commandes, secondes (défaut 120).
- `max_output_bytes` : troncature des sorties (défaut 100 000).
- `allowed_commands` / `denied_commands` : listes optionnelles de contrôle.
- `mcp_shell_token` : bearer token requis en mode HTTP (POC).
- `host`, `port` : bind loopback par défaut (`127.0.0.1:8000`).

Préfixe d'env : `MCP_SHELL_`. Ex. : `MCP_SHELL_ROOT_DIR`, `MCP_SHELL_TOKEN`.

## 4. Transport

- **stdio** : défaut, pour dev local et tests automatisés. Logs impérativement sur stderr.
- **streamable-http** : `mcp.streamable_http_app()` enveloppé dans le middleware d'auth bearer, servi par uvicorn sur `host:port` (loopback par défaut ; nginx fait le pont HTTPS public). Option `stateless_http` envisagée pour simplifier le proxying.

## 5. Sécurité (déploiement distant)

- TLS terminé par nginx (Let's Encrypt) ; le serveur MCP bind 127.0.0.1 uniquement.
- Auth applicative : bearer token (POC) → OAuth2/OIDC (cible) ; mTLS via nginx (`ssl_verify_client on`) en défense en profondeur.
- En-têtes : pas de CORS wildcard ; limites de taille de requête ; rate limiting.
- Audit structlog : commande, cwd, code retour, identité client.
- En environnement sandbox de test : serveurs lancés en loopback uniquement, ports éphémères, jamais d'exposition publique.

## 6. Phases de développement

0. Fondation (structure, pyproject, uv, ruff, pytest) — livrée avec le POC.
1. POC core : 5 tools + confinement + exécution sûre, transport stdio + flag `--transport http`.
2. Sécurité : auth bearer HTTP, policy renforcée, audit, tests de contournement.
3. Robustesse : erreurs structurées, annulation, (option) session persistante.
4. Packaging : build hatchling, `uvx`, README, exemples de config client.
5. CI : tests unitaires/intégration/sécurité automatisés.

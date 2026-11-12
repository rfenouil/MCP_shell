# Décisions stratégiques (ADR) — mcp-shell

Chaque décision liste les options envisagées pendant la discussion, la décision retenue et sa justification. Objectif : qu'un autre agent comprenne le "pourquoi" sans relire toute la conversation.

## ADR-1 — Shell générique plutôt que outils granulaires

- **Options** : (a) un tool MCP par action (`create_file`, `run_tests`, `git_commit`…) ; (b) un tool shell générique `run_command` + lecture/écriture de fichiers dédiées.
- **Décision** : (b), équivalent fonctionnel du *bash tool* de Claude Code / Codex.
- **Justification** : l'agent cible supporte MCP mais n'a pas de TUI ; le shell couvre git, tests, builds, etc. sans énumérer chaque action. Les tools fichiers dédiés restent plus fiables que `cat`/`echo >`.

## ADR-2 — Python + SDK MCP officiel (v2)

- **Options** : Python, TypeScript, autre.
- **Décision** : Python ≥ 3.11 (testé sur 3.12), SDK `mcp>=2.3,<3`.
- **Justification** : SDK officiel mature, asyncio natif pour l'exécution non bloquante. **Note importante** : en v2 du SDK, `FastMCP` est renommé `MCPServer` (`from mcp.server.mcpserver import MCPServer`) — ne pas écrire de code v1.

## ADR-3 — CLI avec typer (surcouche de click)

- **Options** : click pur, typer, argparse.
- **Décision** : typer.
- **Justification** : moins de boilerplate que click, même écosystème ; click reste acceptable si besoin de contrôle total.

## ADR-4 — Logs structlog, impérativement sur stderr

- **Options** : logging stdlib, structlog.
- **Décision** : structlog, format JSON, timestamps ISO, **stderr uniquement**.
- **Justification** : audit structuré des commandes exécutées ; en transport stdio, stdout est réservé au JSON-RPC, toute impression sur stdout casserait le protocole.

## ADR-5 — Deux transports : stdio (défaut) + Streamable HTTP

- **Options** : stdio uniquement (position initiale) ; stdio + HTTP.
- **Décision** : les deux, via `--transport stdio|http`. stdio pour dev/tests, Streamable HTTP (`mcp.streamable_http_app()` + uvicorn) pour le déploiement distant.
- **Justification** : l'agent client tourne sur une machine distante. Le flag CLI garde une seule codebase.

## ADR-6 — Déploiement distant : TLS par nginx, auth applicative, bind loopback

- **Options** : nginx termine HTTPS mais ne fait pas l'auth ; auth laissée au serveur MCP.
- **Décision** : serveur MCP bind `127.0.0.1` uniquement ; nginx seul exposé publiquement (443, Let's Encrypt) ; **auth obligatoire côté serveur en mode HTTP** : bearer token statique (POC, `MCP_SHELL_TOKEN`, comparaison temps constant via `hmac.compare_digest`), OAuth2/OIDC en cible ; mTLS via nginx (`ssl_verify_client on`) en défense en profondeur. Jamais de HTTP en clair hors loopback, pas de CORS wildcard.
- **Justification** : l'agent est sur une machine distante, donc le serveur ne doit jamais être directement exposé.

## ADR-7 — Packaging pip-installable dès la Phase 0

- **Options** : packaging différé en fin de projet ; packaging dès le début.
- **Décision** : `pyproject.toml` + hatchling + entry point `mcp-shell = mcp_shell.server:main` dès le départ ; installable `pip`/`uvx`.
- **Justification** : évite un gros refactor de packaging en fin de projet ; le POC est déjà un vrai package.

## ADR-8 — Architecture en couches, configuration injectée

- **Options** : code monolithique ; couches strictes.
- **Décision** : `tools/` → `core/` + `security/` → `config.py` (pydantic-settings, préfixe env `MCP_SHELL_`). Dépendances uniquement vers le bas, `Settings` injecté, tools minces (validation pydantic puis délégation).
- **Justification** : chaque couche testable seule ; la sécurité ne dépend pas de la couche MCP.

## ADR-9 — Sécurité du shell : confinement + environnement filtré + listes de contrôle

- **Options** : exécution libre ; confinement strict.
- **Décision** : tous les chemins résolus contre une racine (`resolve_confined`, rejet des `..` et absolus hors racine) ; timeout par commande avec kill du process group (`start_new_session=True` + `os.killpg`) ; troncature des sorties (`max_output_bytes`) ; env filtré (`SAFE_ENV_KEYS`, aucun secret transmis) ; `allowed_commands`/`denied_commands` optionnels.
- **Justification** : surface d'attaque minimale même en POC.

## ADR-10 — Persistance du travail hors sandbox : GitHub + snapshot bibliothèque Mistral

- **Options** : sandbox seul (détruit à la fin de session) ; dépôt GitHub.
- **Décision** : livrer sur **`rfenouil/MCP_shell`** (branche `main`, commit `38f7279`). Contrainte rencontrée : dans une session où le connecteur GitHub MCP n'a pas été injecté au démarrage, `gh auth login` peut être bloqué ; le device flow `gh auth login --web --scopes repo` a fonctionné, le push se fait via `git -c credential.helper='!gh auth git-credential' push <url-explicite>` (le token ne transite jamais par le chat). Un snapshot complet (code + docs) est aussi déposé dans la bibliothèque Mistral « mcp-shell ».
- **Justification** : le sandbox est éphémère ; GitHub est le seul stockage durable fiable. Ne jamais pousser dans un dépôt appartenant à un autre projet.

## ADR-11 — Tests : stdio pour l'intégration, loopback pour le HTTP

- **Options** : tout tester en HTTP ; tout en stdio.
- **Décision** : intégration MCP via `ClientSession` sur **stdio** (rapide, local) ; le middleware d'auth testé unitairement via `TestClient` (pas de vrai serveur réseau). En sandbox, jamais d'écoute publique.
- **Justification** : reproductible, rapide, aucune exposition réseau.

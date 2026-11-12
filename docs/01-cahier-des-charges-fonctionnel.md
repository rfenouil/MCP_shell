# Cahier des charges fonctionnel — mcp-shell

## 1. Contexte et objectif

Fournir à un agent de chat compatible MCP (mais sans interface TUI type Claude Code / Codex) un accès shell structuré, sûr et auditable, équivalent fonctionnel du *bash tool* de ces outils.

## 2. Utilisateurs et déploiement

- **Client** : agent de chat MCP tournant sur une machine distante du serveur.
- **Déploiement cible** : serveur MCP derrière un reverse proxy nginx qui termine le HTTPS. Le serveur MCP lui-même n'écoute que sur loopback.
- **Transports supportés** : stdio (dev local, tests) et Streamable HTTP (déploiement distant).

## 3. Fonctions attendues (tools MCP)

| Tool | Description | Entrées principales |
|---|---|---|
| `run_command` | Exécute une commande shell dans la racine confinée, retourne stdout/stderr/code retour | `command`, `cwd` (optionnel), `timeout` (optionnel) |
| `read_file` | Lit un fichier texte sous la racine | `path`, `offset`/`limit` optionnels |
| `write_file` | Écrit/écrase un fichier sous la racine | `path`, `content` |
| `glob` | Recherche de fichiers par motif | `pattern` |
| `grep` | Recherche de texte dans les fichiers sous la racine | `pattern`, `path` optionnel |

## 4. Exigences non fonctionnelles

### 4.1 Sécurité
- Confinement strict de tous les chemins à une racine configurée (rejet des sorties via `..`, chemins absolus hors racine).
- Timeout obligatoire sur chaque commande (défaut 120 s), kill du groupe de processus.
- Troncature des sorties au-delà d'une taille max configurable.
- Environnement d'exécution filtré (pas de secrets transmis au shell).
- En mode HTTP : authentification obligatoire (bearer token en POC, OAuth2/OIDC en cible), aucune écoute publique directe.
- Audit : chaque commande exécutée est journalisée avec l'identité du client.

### 4.2 Disponibilité / robustesse
- Erreurs structurées retournées au client MCP (jamais de crash du serveur sur une commande invalide).
- Gestion propre des signaux d'annulation.

### 4.3 Packaging
- Installable via `pip` / `uvx`, commande console `mcp-shell`.
- Configuration par variables d'environnement et options CLI.

## 5. Hors périmètre (v1)

- Sessions shell persistantes interactives (PTY).
- Streaming progressif de la sortie des commandes.
- Authentification OAuth2/OIDC complète (POC : bearer token statique).

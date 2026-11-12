# Functional requirements — mcp-shell

## 1. Context and objective

Give an MCP-compatible chat agent (but without a TUI like Claude Code / Codex) structured, safe and auditable shell access, functionally equivalent to the *bash tool* of those tools.

## 2. Users and deployment

- **Client**: MCP chat agent running on a machine remote from the server.
- **Target deployment**: MCP server behind an nginx reverse proxy terminating HTTPS. The MCP server itself only listens on loopback.
- **Supported transports**: stdio (local dev, tests) and Streamable HTTP (remote deployment).

## 3. Expected functions (MCP tools)

| Tool | Description | Main inputs |
|---|---|---|
| `run_command` | Run a shell command in the confined root, returns stdout/stderr/return code | `command`, `cwd` (optional), `timeout` (optional) |
| `read_file` | Read a text file under the root | `path`, optional `offset`/`limit` |
| `write_file` | Write/overwrite a file under the root | `path`, `content` |
| `glob` | Find files by pattern | `pattern` |
| `grep` | Search text in files under the root | `pattern`, optional `path` |

## 4. Non-functional requirements

### 4.1 Security
- Strict confinement of all paths to a configured root (rejection of escapes via `..`, absolute paths outside the root).
- Mandatory timeout on every command (default 120 s), kill of the process group.
- Output truncation beyond a configurable max size.
- Filtered execution environment (no secrets passed to the shell).
- In HTTP mode: mandatory authentication (bearer token in POC, OAuth2/OIDC as target), no direct public listener.
- Audit: every executed command is logged with the client identity.

### 4.2 Availability / robustness
- Structured errors returned to the MCP client (server never crashes on an invalid command).
- Clean handling of cancellation signals.

### 4.3 Packaging
- Installable via `pip` / `uvx`, console command `mcp-shell`.
- Configuration via environment variables and CLI options.

## 5. Out of scope (v1)

- Persistent interactive shell sessions (PTY).
- Progressive streaming of command output.
- Full OAuth2/OIDC authentication (POC: static bearer token).

# Deployment behind nginx (remote agent setup)

The MCP server must never be publicly reachable by itself: it binds loopback only. nginx is the single public listener and terminates TLS.

## Topology

```
chat agent (remote machine)
        │  HTTPS :443
        ▼
nginx (public, Let's Encrypt cert)
        │  HTTP, proxy_pass → 127.0.0.1:8000
        ▼
mcp-shell --transport http --host 127.0.0.1 --port 8000   (bearer token required)
```

## nginx server block (template)

```nginx
server {
    listen 443 ssl;
    server_name mcp-shell.example.com;

    ssl_certificate     /etc/letsencrypt/live/mcp-shell.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp-shell.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Optional defense-in-depth: mTLS (ADR-6)
    # ssl_client_certificate /etc/nginx/ca.pem;
    # ssl_verify_client on;

    location /mcp {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        client_max_body_size 4m;
    }
}
```

## Application-side requirements (already implemented)

- `MCP_SHELL_TOKEN` (or `--token`) is **mandatory** in HTTP mode; bearer auth middleware returns 401 otherwise (constant-time comparison).
- Rate limiting: `MCP_SHELL_RATE_LIMIT_PER_MINUTE` (default 120 req/min/IP, 429 + `Retry-After`).
- `MCP_SHELL_ROOT_DIR` sets the confinement root for all tools and commands.
- Audit logs (JSON, structlog) go to stderr — collect them with journald or a log shipper.

## Client config example (agent side)

```json
{
  "mcpServers": {
    "mcp-shell": {
      "type": "http",
      "url": "https://mcp-shell.example.com/mcp",
      "headers": { "Authorization": "Bearer <token>" }
    }
  }
}
```

## Roadmap

- POC: static bearer token (done).
- Target: OAuth2/OIDC via the MCP SDK auth support; mTLS at nginx as an additional transport-level layer.

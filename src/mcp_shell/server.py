import logging
import sys

import structlog
import typer

from mcp_shell.config import Settings
from mcp_shell.security.auth import BearerAuthMiddleware
from mcp_shell.tools import command, files, search

cli = typer.Typer(help="mcp-shell: MCP server giving an agent confined shell access.")


def configure_logging() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


def build_server(settings: Settings):
    from mcp.server.mcpserver import MCPServer

    mcp = MCPServer("mcp-shell", version="0.1.0")
    command.register(mcp, settings)
    files.register(mcp, settings)
    search.register(mcp, settings)
    return mcp


@cli.command()
def serve(
    transport: str = typer.Option("stdio", "--transport", help="stdio | http"),
    root_dir: str | None = typer.Option(None, "--root-dir"),
    host: str | None = typer.Option(None, "--host"),
    port: int | None = typer.Option(None, "--port"),
    token: str | None = typer.Option(None, "--token"),
) -> None:
    overrides = {
        k: v
        for k, v in {
            "root_dir": root_dir,
            "host": host,
            "port": port,
            "token": token,
        }.items()
        if v is not None
    }
    settings = Settings(**overrides)
    configure_logging()
    mcp = build_server(settings)
    if transport == "stdio":
        mcp.run(transport="stdio")
        return
    if transport != "http":
        raise typer.BadParameter(f"unknown transport: {transport}")
    if not settings.token:
        raise typer.BadParameter("--token / MCP_SHELL_TOKEN is required for http transport")
    import uvicorn

    asgi_app = mcp.streamable_http_app()
    asgi_app = BearerAuthMiddleware(asgi_app, settings.token)
    uvicorn.run(asgi_app, host=settings.host, port=settings.port, log_level="info")


def main() -> None:
    cli()

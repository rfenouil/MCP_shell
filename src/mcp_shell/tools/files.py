from mcp.server.mcpserver import MCPServer

from mcp_shell.config import Settings
from mcp_shell.core.paths import resolve_confined
from mcp_shell.security import audit


def register(mcp: MCPServer, settings: Settings, client: str = "local") -> None:
    @mcp.tool(
        name="read_file",
        description="Read a text file confined to the configured root directory.",
    )
    async def read_file(path: str, offset: int = 0, limit: int | None = None) -> dict:
        root = settings.resolved_root()
        try:
            target = resolve_confined(root, path)
        except Exception as exc:
            return {"error": str(exc)}
        audit.log_access(client=client, tool="read_file", path=str(target))
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"error": str(exc)}
        lines = text.splitlines()
        selected = lines[offset:] if limit is None else lines[offset : offset + limit]
        return {
            "path": str(target.relative_to(root)),
            "content": "\n".join(selected),
            "total_lines": len(lines),
        }

    @mcp.tool(
        name="write_file",
        description="Write a text file confined to the configured root directory.",
    )
    async def write_file(path: str, content: str) -> dict:
        root = settings.resolved_root()
        try:
            target = resolve_confined(root, path)
        except Exception as exc:
            return {"error": str(exc)}
        audit.log_access(client=client, tool="write_file", path=str(target))
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except OSError as exc:
            return {"error": str(exc)}
        return {"path": str(target.relative_to(root)), "bytes_written": len(content.encode())}

import re

from mcp.server.mcpserver import MCPServer

from mcp_shell.config import Settings
from mcp_shell.core.paths import resolve_confined, validate_glob_pattern
from mcp_shell.security import audit


def register(mcp: MCPServer, settings: Settings, client: str = "local") -> None:
    @mcp.tool(
        name="glob",
        description="List files under the root matching a glob pattern.",
    )
    async def glob(pattern: str) -> dict:
        root = settings.resolved_root()
        try:
            validate_glob_pattern(pattern)
            base = resolve_confined(root, ".")
            matches = sorted(str(p.relative_to(root)) for p in base.glob(pattern) if p.is_file())
        except Exception as exc:
            return {"error": str(exc)}
        audit.log_access(client=client, tool="glob", path=pattern)
        return {"matches": matches[:1000]}

    @mcp.tool(
        name="grep",
        description="Search for a regex pattern in files under the root.",
    )
    async def grep(pattern: str, path: str = ".") -> dict:
        root = settings.resolved_root()
        try:
            regex = re.compile(pattern)
            base = resolve_confined(root, path)
        except Exception as exc:
            return {"error": str(exc)}
        audit.log_access(client=client, tool="grep", path=path)
        results = []
        files = sorted(base.rglob("*")) if base.is_dir() else [base]
        for file in files:
            if not file.is_file():
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                if regex.search(line):
                    results.append(
                        {
                            "path": str(file.relative_to(root)),
                            "line_number": lineno,
                            "line": line[:500],
                        }
                    )
                    if len(results) >= settings.max_grep_matches:
                        return {"matches": results, "truncated": True}
        return {"matches": results, "truncated": False}

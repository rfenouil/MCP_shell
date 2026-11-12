from mcp.server.mcpserver import MCPServer

from mcp_shell.config import Settings
from mcp_shell.core.executor import execute
from mcp_shell.core.paths import resolve_confined
from mcp_shell.security import audit
from mcp_shell.security.policy import build_safe_env, ensure_allowed


def register(mcp: MCPServer, settings: Settings, client: str = "local") -> None:
    @mcp.tool(
        name="run_command",
        description="Execute a shell command confined to the configured root directory.",
    )
    async def run_command(command: str, cwd: str = ".", timeout: int | None = None) -> dict:
        root = settings.resolved_root()
        try:
            workdir = resolve_confined(root, cwd)
            ensure_allowed(command, settings.allowed_commands, settings.denied_commands)
        except Exception as exc:
            audit.log_command(
                client=client, command=command, cwd=cwd, returncode=-1, timed_out=False
            )
            return {"error": str(exc), "returncode": -1}
        effective_timeout = timeout if timeout is not None else settings.command_timeout
        result = await execute(
            command,
            cwd=str(workdir),
            timeout=effective_timeout,
            max_output_bytes=settings.max_output_bytes,
            env=build_safe_env(),
        )
        audit.log_command(
            client=client,
            command=command,
            cwd=str(workdir),
            returncode=result.returncode,
            timed_out=result.timed_out,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timed_out": result.timed_out,
            "truncated": result.truncated,
        }

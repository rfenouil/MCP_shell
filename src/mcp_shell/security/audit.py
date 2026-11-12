import structlog

logger = structlog.get_logger("mcp_shell.audit")


def log_command(*, client: str, command: str, cwd: str, returncode: int, timed_out: bool) -> None:
    logger.info(
        "command_executed",
        client=client,
        command=command,
        cwd=cwd,
        returncode=returncode,
        timed_out=timed_out,
    )


def log_access(*, client: str, tool: str, path: str) -> None:
    logger.info("tool_called", client=client, tool=tool, path=path)

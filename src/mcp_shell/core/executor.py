import asyncio
import os
import signal
from dataclasses import dataclass


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool
    truncated: bool


def _truncate(data: bytes, limit: int) -> tuple[str, bool]:
    truncated = len(data) > limit
    if truncated:
        data = data[:limit]
    return data.decode("utf-8", errors="replace"), truncated


async def execute(
    command: str,
    *,
    cwd: str,
    timeout: float,
    max_output_bytes: int,
    env: dict[str, str],
) -> CommandResult:
    proc = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True,
    )
    timed_out = False
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        timed_out = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = await proc.communicate()
    except asyncio.CancelledError:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        await proc.communicate()
        raise
    stdout, out_truncated = _truncate(out, max_output_bytes)
    stderr, err_truncated = _truncate(err, max_output_bytes)
    return CommandResult(
        stdout=stdout,
        stderr=stderr,
        returncode=proc.returncode if proc.returncode is not None else -1,
        timed_out=timed_out,
        truncated=out_truncated or err_truncated,
    )

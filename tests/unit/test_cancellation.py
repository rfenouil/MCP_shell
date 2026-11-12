import asyncio
import subprocess

import pytest

from mcp_shell.core.executor import execute


def sleep_processes_running() -> int:
    result = subprocess.run(["pgrep", "-fc", "sleep 4242"], capture_output=True, text=True)
    return int(result.stdout.strip() or 0)


async def test_cancellation_kills_process_group(tmp_path) -> None:
    assert sleep_processes_running() == 0
    task = asyncio.create_task(
        execute(
            "sleep 4242",
            cwd=str(tmp_path),
            timeout=60,
            max_output_bytes=1000,
            env={"PATH": "/usr/bin:/bin"},
        )
    )
    await asyncio.sleep(0.5)
    assert sleep_processes_running() >= 1
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await asyncio.sleep(0.5)
    assert sleep_processes_running() == 0

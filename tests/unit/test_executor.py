from mcp_shell.core.executor import execute


async def test_simple_command(tmp_path) -> None:
    result = await execute(
        "echo hello",
        cwd=str(tmp_path),
        timeout=10,
        max_output_bytes=1000,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "hello"
    assert result.timed_out is False


async def test_timeout_kills_process_group(tmp_path) -> None:
    result = await execute(
        "sleep 30",
        cwd=str(tmp_path),
        timeout=1,
        max_output_bytes=1000,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.timed_out is True
    assert result.returncode != 0


async def test_output_truncated(tmp_path) -> None:
    result = await execute(
        "head -c 5000 /dev/zero | tr '\\0' 'a'",
        cwd=str(tmp_path),
        timeout=10,
        max_output_bytes=100,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.truncated is True
    assert len(result.stdout) == 100


async def test_returncode_propagated(tmp_path) -> None:
    result = await execute(
        "exit 3",
        cwd=str(tmp_path),
        timeout=10,
        max_output_bytes=1000,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 3

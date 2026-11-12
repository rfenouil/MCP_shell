import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[2]


async def make_session(tmp_path: Path):
    env = dict(os.environ)
    env["MCP_SHELL_ROOT_DIR"] = str(tmp_path)
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_shell"],
        env=env,
        cwd=str(PROJECT_ROOT),
    )
    return stdio_client(params)


def parse_result(result) -> dict:
    return json.loads(result.content[0].text)


async def test_tools_listed(tmp_path: Path) -> None:
    async with await make_session(tmp_path) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert {"run_command", "read_file", "write_file", "glob", "grep"} <= names


async def test_run_command_confined(tmp_path: Path) -> None:
    async with await make_session(tmp_path) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("run_command", {"command": "pwd"})
            data = parse_result(result)
            assert data["returncode"] == 0
            assert data["stdout"].strip() == str(tmp_path.resolve())


async def test_run_command_escape_rejected(tmp_path: Path) -> None:
    async with await make_session(tmp_path) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "run_command", {"command": "cat /etc/hostname", "cwd": "../.."}
            )
            data = parse_result(result)
            assert "error" in data


async def test_write_then_read_then_grep(tmp_path: Path) -> None:
    async with await make_session(tmp_path) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await session.call_tool(
                "write_file", {"path": "notes/todo.txt", "content": "acheter du lait\n"}
            )
            read_result = await session.call_tool("read_file", {"path": "notes/todo.txt"})
            assert "acheter du lait" in parse_result(read_result)["content"]
            glob_result = await session.call_tool("glob", {"pattern": "**/*.txt"})
            assert parse_result(glob_result)["matches"] == ["notes/todo.txt"]
            grep_result = await session.call_tool("grep", {"pattern": "lait"})
            matches = parse_result(grep_result)["matches"]
            assert matches and matches[0]["path"] == "notes/todo.txt"


async def test_structured_errors(tmp_path: Path) -> None:
    async with await make_session(tmp_path) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            bad_glob = parse_result(await session.call_tool("glob", {"pattern": "../*"}))
            assert "error" in bad_glob
            bad_regex = parse_result(await session.call_tool("grep", {"pattern": "["}))
            assert "error" in bad_regex
            missing = parse_result(await session.call_tool("read_file", {"path": "nope.txt"}))
            assert "error" in missing
            escape = parse_result(
                await session.call_tool("write_file", {"path": "../x", "content": "x"})
            )
            assert "error" in escape

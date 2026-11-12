import os

import pytest

from mcp_shell.security.policy import PolicyError, build_safe_env, ensure_allowed


def test_safe_env_filters_secrets() -> None:
    old = os.environ.get("MCP_SHELL_TOKEN")
    os.environ["MCP_SHELL_TOKEN"] = "secret-value"
    os.environ["PATH"] = "/usr/bin:/bin"
    try:
        env = build_safe_env()
    finally:
        if old is None:
            del os.environ["MCP_SHELL_TOKEN"]
        else:
            os.environ["MCP_SHELL_TOKEN"] = old
    assert "MCP_SHELL_TOKEN" not in env
    assert env["PATH"] == "/usr/bin:/bin"


def test_denied_command_rejected() -> None:
    with pytest.raises(PolicyError):
        ensure_allowed("rm -rf /", allowed=None, denied=["rm"])


def test_allowlist_enforced() -> None:
    ensure_allowed("git status", allowed=["git"], denied=[])
    with pytest.raises(PolicyError):
        ensure_allowed("curl example.com", allowed=["git"], denied=[])


def test_empty_command_rejected() -> None:
    with pytest.raises(PolicyError):
        ensure_allowed("   ", allowed=None, denied=[])

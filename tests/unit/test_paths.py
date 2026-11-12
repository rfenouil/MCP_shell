from pathlib import Path

import pytest

from mcp_shell.core.paths import PathEscapeError, resolve_confined


def test_relative_path_inside_root(tmp_path: Path) -> None:
    result = resolve_confined(tmp_path, "sub/file.txt")
    assert result == (tmp_path / "sub/file.txt").resolve()


def test_dotdot_escape_rejected(tmp_path: Path) -> None:
    with pytest.raises(PathEscapeError):
        resolve_confined(tmp_path, "../outside.txt")


def test_absolute_path_outside_root_rejected(tmp_path: Path) -> None:
    with pytest.raises(PathEscapeError):
        resolve_confined(tmp_path, "/etc/passwd")


def test_absolute_path_inside_root_allowed(tmp_path: Path) -> None:
    inside = tmp_path / "ok.txt"
    assert resolve_confined(tmp_path, str(inside)) == inside.resolve()


def test_root_itself_allowed(tmp_path: Path) -> None:
    assert resolve_confined(tmp_path, ".") == tmp_path.resolve()

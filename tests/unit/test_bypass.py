import os
from pathlib import Path

import pytest

from mcp_shell.core.paths import PathEscapeError, resolve_confined, validate_glob_pattern


def test_symlink_inside_root_pointing_outside_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-secret.txt"
    outside.write_text("secret")
    link = tmp_path / "link.txt"
    os.symlink(outside, link)
    with pytest.raises(PathEscapeError):
        resolve_confined(tmp_path, "link.txt")


def test_dotdot_staying_inside_root_allowed(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    result = resolve_confined(tmp_path, "sub/../file.txt")
    assert result == (tmp_path / "file.txt").resolve()


@pytest.mark.parametrize(
    "pattern",
    ["../*", "..", "a/../../etc/*", "/etc/*", ""],
)
def test_glob_escape_patterns_rejected(pattern: str) -> None:
    with pytest.raises(PathEscapeError):
        validate_glob_pattern(pattern)


@pytest.mark.parametrize("pattern", ["**/*.py", "src/**/*.py", "*.md", "docs/0*"])
def test_glob_safe_patterns_allowed(pattern: str) -> None:
    validate_glob_pattern(pattern)

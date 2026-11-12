from pathlib import Path


class PathEscapeError(Exception):
    pass


def resolve_confined(root: Path, raw: str) -> Path:
    root = root.resolve()
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    if candidate != root and root not in candidate.parents:
        raise PathEscapeError(f"path escapes root: {raw!r}")
    return candidate


def validate_glob_pattern(pattern: str) -> None:
    if not pattern or Path(pattern).is_absolute():
        raise PathEscapeError(f"invalid glob pattern: {pattern!r}")
    if ".." in pattern.split("/"):
        raise PathEscapeError(f"glob pattern escapes root: {pattern!r}")

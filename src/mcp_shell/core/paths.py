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

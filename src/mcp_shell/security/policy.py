import os
import shlex

SAFE_ENV_KEYS = frozenset(
    {"PATH", "HOME", "LANG", "LC_ALL", "TERM", "USER", "LOGNAME", "SHELL", "TMPDIR"}
)


class PolicyError(Exception):
    pass


def build_safe_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k in SAFE_ENV_KEYS}


def ensure_allowed(command: str, allowed: list[str] | None, denied: list[str]) -> None:
    try:
        argv0 = shlex.split(command)[0]
    except (ValueError, IndexError):
        raise PolicyError("empty or unparsable command")
    base = os.path.basename(argv0)
    if base in denied:
        raise PolicyError(f"command denied: {base}")
    if allowed is not None and base not in allowed:
        raise PolicyError(f"command not in allowlist: {base}")

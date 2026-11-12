from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_SHELL_")

    root_dir: Path = Field(default_factory=lambda: Path.cwd())
    command_timeout: int = 120
    max_output_bytes: int = 100_000
    max_grep_matches: int = 100
    allowed_commands: list[str] | None = None
    denied_commands: list[str] = Field(default_factory=list)
    token: str | None = None
    host: str = "127.0.0.1"
    port: int = 8000
    rate_limit_per_minute: int = 120

    def resolved_root(self) -> Path:
        return self.root_dir.expanduser().resolve()

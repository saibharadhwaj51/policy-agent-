"""
config.py
=========
Central configuration for the AI Policy Advisor.

WHY THIS FILE EXISTS
---------------------
Every other module in this project (agents, rag pipeline, api, ui) needs
things like API keys, file paths, and model names. Instead of each module
calling `os.getenv(...)` directly (error-prone, no validation, easy to typo
a variable name and get `None` silently), we read the environment ONCE here,
validate it with pydantic, and export a single `settings` object.

If a required variable is missing or malformed, the app fails LOUDLY at
startup instead of failing silently three modules deep at 2am in production.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Typed, validated application settings.

    Pydantic reads these from environment variables / the .env file.
    The attribute name (lowercase) maps to the env var name (uppercase)
    automatically, e.g. `google_api_key` <- GOOGLE_API_KEY.
    """

    # ---- LLM ----
    google_api_key: str = "REPLACE_ME"
    gemini_model: str = "gemini-1.5-pro"

    # ---- Embeddings ----
    embedding_model: str = "all-MiniLM-L6-v2"

    # ---- Vector DB ----
    chroma_db_path: Path = Path("./vector_db")

    # ---- App paths ----
    upload_dir: Path = Path("./uploads")
    reports_dir: Path = Path("./reports")
    auto_ingest_dir: Path = Path("./uploads/auto_ingest")
    processed_dir: Path = Path("./uploads/processed")
    failed_dir: Path = Path("./uploads/failed")

    # ---- Logging ----
    log_level: str = "INFO"
    log_file: Path = Path("./logs/app.log")

    # ---- API ----
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ---- Automation ----
    start_watcher: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def ensure_directories(self) -> None:
        """Create every directory this app depends on, if it doesn't exist yet."""
        paths_to_create = [
            self.chroma_db_path,
            self.upload_dir,
            self.reports_dir,
            self.auto_ingest_dir,
            self.processed_dir,
            self.failed_dir,
            self.log_file.parent
        ]
        for path in paths_to_create:
            path.mkdir(parents=True, exist_ok=True)


# A single, importable instance every other module will use:
#   from config import settings
settings = Settings()
settings.ensure_directories()

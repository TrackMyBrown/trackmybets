"""Application configuration helpers."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "development")
    api_host: str = os.getenv("API_HOST", "127.0.0.1")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/trackmybets.db")
    raw_data_dir: Path = Path(os.getenv("RAW_DATA_DIR", "./data/raw"))
    rejects_dir: Path = Path(os.getenv("REJECTS_DIR", "./data/rejects"))
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

    class Config:
        arbitrary_types_allowed = True

    def ensure_data_dirs(self) -> None:
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.rejects_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_data_dirs()
    return settings


settings = get_settings()

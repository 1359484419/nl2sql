"""
配置管理 — 从 .env 文件加载 Learning Tracker 相关配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class TrackerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DB_HOST: str = "/tmp"
    DB_PORT: int = 5432
    DB_NAME: str = "learning_tracker"
    DB_USER: str = "liuzhuoran"
    DB_PASSWORD: str = ""

    GIT_PROJECT_PATH: str = "/Users/liuzhuoran/cursor/nl2sql-bi-agent"

    @property
    def async_db_url(self) -> str:
        if self.DB_HOST.startswith("/"):
            return f"postgresql+asyncpg://{self.DB_USER}@/{self.DB_NAME}?host={self.DB_HOST}"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


tracker_settings = TrackerSettings()

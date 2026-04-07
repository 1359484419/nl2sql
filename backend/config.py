"""
全局配置管理 — 从 .env 文件加载所有配置项
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ─── LLM 配置 ───────────────────────────────────────────────
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.deepseek.com"
    openai_model: str = "gpt-4o-mini"
    openai_embed_model: str = "text-embedding-3-small"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_embed_model: str = "nomic-embed-text"

    use_ollama: bool = True  # True = Ollama 本地模型，False = OpenAI

    # ─── Milvus 向量数据库配置 ─────────────────────────────────
    milvus_collection_schema: str = "saas_bi_schema"
    milvus_collection_metrics: str = "saas_bi_metrics"
    milvus_collection_examples: str = "saas_bi_sql_examples"
    milvus_data_dir: str = "./data/milvus"

    # ─── 业务数据库配置（PostgreSQL） ───────────────────────────
    db_host: str = "/tmp"
    db_port: int = 5432
    db_name: str = "saas_bi"
    db_user: str = "liuzhuoran"
    db_password: str = ""

    # ─── FastAPI 服务配置 ──────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # ─── RAG 配置 ───────────────────────────────────────────────
    top_k_schema: int = 10
    top_k_metrics: int = 5
    top_k_examples: int = 5

    # ─── SQL 生成配置 ───────────────────────────────────────────
    max_sql_retries: int = 3

    @property
    def db_url(self) -> str:
        if self.db_host.startswith("/"):
            # Unix socket 模式（macOS 上 postgres 通过 /tmp 连接）
            pw = f":{self.db_password}" if self.db_password else ""
            return f"postgresql://{self.db_user}{pw}@/saas_bi?host={self.db_host}"
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def resolve_llm_config(self) -> dict:
        if self.use_ollama:
            return {
                "provider": "ollama",
                "model": self.ollama_model,
                "base_url": self.ollama_base_url,
                "embed_model": self.ollama_embed_model,
            }
        return {
            "provider": "openai",
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "embed_model": self.openai_embed_model,
            "base_url": self.openai_base_url,
        }


settings = Settings()

"""
嵌入模型管理 — 统一管理 Embedding 模型，支持 Ollama / OpenAI / HuggingFace
"""

from typing import Optional
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer
from backend.config import settings


class EmbeddingModel:
    """
    统一的嵌入模型封装类。

    支持三种模式：
    1. Ollama 本地模型（nomic-embed-text 等，REST API）
    2. OpenAI 云端模型（text-embedding-3-small 等）
    3. HuggingFace SentenceTransformer（纯本地，无需 GPU）
    """

    _instance: Optional["EmbeddingModel"] = None

    def __init__(self):
        self._provider = "huggingface"  # 默认用 HuggingFace，零配置即可运行
        self._embedding_model = None
        self._embed_dimension = 768
        self._init_embedding()

    def _init_embedding(self):
        """初始化嵌入模型"""
        llm_config = settings.resolve_llm_config()
        provider = llm_config["provider"]

        # Ollama 有自己的 embedding 服务
        if provider == "ollama":
            try:
                self._provider = "ollama"
                self._embedding_model = OllamaEmbeddings(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_embed_model,
                )
                self._embed_dimension = 768
                print(f"[EmbeddingModel] 使用 Ollama {settings.ollama_embed_model}")
                return
            except Exception as e:
                print(f"[EmbeddingModel] Ollama 连接失败，fallback 到 HuggingFace: {e}")

        # 非 Ollama（DeepSeek / OpenAI 等）统一用 HuggingFace 本地 embedding
        # DeepSeek / OpenAI 的 Chat 模型不提供 embedding 接口
        self._provider = "huggingface"
        self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self._embed_dimension = 384
        print("[EmbeddingModel] 使用 HuggingFace all-MiniLM-L6-v2（CPU，本地向量化）")

    def embed_query(self, text: str) -> list[float]:
        """将单条文本向量化"""
        if self._provider == "ollama":
            return self._embedding_model.embed_query(text)
        elif self._provider == "openai":
            return self._embedding_model.embed_query(text)
        else:
            return self._embedding_model.encode(text).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量向量化"""
        if self._provider == "ollama":
            return self._embedding_model.embed_documents(texts)
        elif self._provider == "openai":
            return self._embedding_model.embed_documents(texts)
        else:
            return self._embedding_model.encode(texts).tolist()

    @property
    def dimension(self) -> int:
        return self._embed_dimension

    @property
    def provider(self) -> str:
        return self._provider

    @classmethod
    def get_instance(cls) -> "EmbeddingModel":
        """单例模式"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# 全局单例
embedding_model = EmbeddingModel.get_instance()

"""
统一的 RAG 检索器 — 从 Milvus 中检索 Schema / 指标 / SQL 示例
对外提供统一的检索接口，为 NL2SQL Agent 提供上下文
"""

import json
from typing import Any, Dict, List, Optional
from pymilvus import MilvusClient, DataType

from backend.rag.embedding import embedding_model
from backend.rag.metrics_library import BUSINESS_METRICS
from backend.rag.sql_examples import SQL_EXAMPLES
from backend.config import settings
from pathlib import Path


class MetricsIndexer:
    """业务指标库索引器 — 将 BUSINESS_METRICS 向量化存入 Milvus"""

    def __init__(self):
        self._client: Optional[MilvusClient] = None
        self._collection_name = settings.milvus_collection_metrics
        self._dim = embedding_model.dimension
        self._connect()

    def _connect(self):
        db_path = Path(settings.milvus_data_dir)
        db_path.mkdir(parents=True, exist_ok=True)
        db_file = db_path / "milvus_saas_bi.db"
        self._client = MilvusClient(uri=str(db_file))

    def _ensure_collection(self, drop_existing: bool = False):
        if self._client.has_collection(self._collection_name):
            if drop_existing:
                self._client.drop_collection(self._collection_name)
            else:
                return
        schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self._dim)
        schema.add_field(field_name="metric_id", datatype=DataType.VARCHAR, max_length=50)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2000)
        schema.add_field(field_name="metadata", datatype=DataType.VARCHAR, max_length=2000)
        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type="COSINE")
        self._client.create_collection(collection_name=self._collection_name, schema=schema, index_params=index_params)

    def build_index(self, drop_existing: bool = False):
        self._ensure_collection(drop_existing=drop_existing)
        chunks = []
        for metric in BUSINESS_METRICS:
            aliases_text = "，".join(metric.get("aliases", []))
            text = (
                f"指标名称：{metric['metric_name']}\n"
                f"常见问法：{aliases_text}\n"
                f"指标定义：{metric['definition_desc']}\n"
                f"使用表：{', '.join(metric.get('table_used', []))}\n"
                f"适用场景：{', '.join(metric.get('applicable_scenes', []))}"
            )
            chunks.append({
                "metric_id": metric["metric_id"],
                "text": text,
                "metadata": json.dumps(metric, ensure_ascii=False),
            })
        print(f"[MetricsIndexer] 共生成 {len(chunks)} 个指标块，开始向量化...")
        vectors = embedding_model.embed_documents([c["text"] for c in chunks])
        entities = [
            {"metric_id": c["metric_id"], "text": c["text"], "metadata": c["metadata"], "vector": vec}
            for c, vec in zip(chunks, vectors)
        ]
        self._client.insert(collection_name=self._collection_name, data=entities)
        print(f"[MetricsIndexer] ✅ 索引构建完成，共插入 {len(entities)} 条")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = embedding_model.embed_query(query)
        results = self._client.search(
            collection_name=self._collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["metric_id", "text", "metadata"],
            search_params={"metric_type": "COSINE", "params": {}},
        )
        return [
            {
                "metric_id": hit["entity"]["metric_id"],
                "text": hit["entity"]["text"],
                "metadata": json.loads(hit["entity"]["metadata"]),
                "score": hit.get("distance", 0),
            }
            for hit in results[0]
        ]


class ExamplesIndexer:
    """SQL 示例库索引器 — 将 SQL_EXAMPLES 向量化存入 Milvus"""

    def __init__(self):
        self._client: Optional[MilvusClient] = None
        self._collection_name = settings.milvus_collection_examples
        self._dim = embedding_model.dimension
        self._connect()

    def _connect(self):
        db_path = Path(settings.milvus_data_dir)
        db_path.mkdir(parents=True, exist_ok=True)
        db_file = db_path / "milvus_saas_bi.db"
        self._client = MilvusClient(uri=str(db_file))

    def _ensure_collection(self, drop_existing: bool = False):
        if self._client.has_collection(self._collection_name):
            if drop_existing:
                self._client.drop_collection(self._collection_name)
            else:
                return
        schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=True)
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self._dim)
        schema.add_field(field_name="example_id", datatype=DataType.VARCHAR, max_length=50)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=3000)
        schema.add_field(field_name="metadata", datatype=DataType.VARCHAR, max_length=2000)
        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type="COSINE")
        self._client.create_collection(collection_name=self._collection_name, schema=schema, index_params=index_params)

    def build_index(self, drop_existing: bool = False):
        self._ensure_collection(drop_existing=drop_existing)
        chunks = []
        for ex in SQL_EXAMPLES:
            tags_text = "，".join(ex.get("tags", []))
            text = (
                f"问题模式：{ex['question_pattern']}\n"
                f"SQL 示例：{ex['sql']}\n"
                f"说明：{ex['description']}\n"
                f"适用图表：{', '.join(ex.get('applicable_charts', []))}\n"
                f"标签：{tags_text}"
            )
            chunks.append({
                "example_id": ex["example_id"],
                "text": text,
                "metadata": json.dumps(ex, ensure_ascii=False),
            })
        print(f"[ExamplesIndexer] 共生成 {len(chunks)} 个示例块，开始向量化...")
        vectors = embedding_model.embed_documents([c["text"] for c in chunks])
        entities = [
            {"example_id": c["example_id"], "text": c["text"], "metadata": c["metadata"], "vector": vec}
            for c, vec in zip(chunks, vectors)
        ]
        self._client.insert(collection_name=self._collection_name, data=entities)
        print(f"[ExamplesIndexer] ✅ 索引构建完成，共插入 {len(entities)} 条")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = embedding_model.embed_query(query)
        results = self._client.search(
            collection_name=self._collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["example_id", "text", "metadata"],
            search_params={"metric_type": "COSINE", "params": {}},
        )
        return [
            {
                "example_id": hit["entity"]["example_id"],
                "text": hit["entity"]["text"],
                "metadata": json.loads(hit["entity"]["metadata"]),
                "score": hit.get("distance", 0),
            }
            for hit in results[0]
        ]


class UnifiedRetriever:
    """
    统一检索器 — 同时检索 Schema + 指标 + SQL 示例
    为 NL2SQL Agent 提供完整的上下文信息
    """

    def __init__(self):
        from backend.rag.schema_indexer import SchemaIndexer
        self._schema_indexer = SchemaIndexer()
        self._metrics_indexer = MetricsIndexer()
        self._examples_indexer = ExamplesIndexer()

    def retrieve(self, question: str) -> Dict[str, List[Dict[str, Any]]]:
        """执行多路检索，返回各类上下文"""
        schema_chunks = self._schema_indexer.search(question, top_k=settings.top_k_schema)
        metrics = self._metrics_indexer.search(question, top_k=settings.top_k_metrics)
        sql_examples = self._examples_indexer.search(question, top_k=settings.top_k_examples)
        return {
            "schema_chunks": schema_chunks,
            "metrics": metrics,
            "sql_examples": sql_examples,
        }

    def build_all_indexes(self, drop_existing: bool = False):
        """构建所有向量索引"""
        self._schema_indexer.build_index(drop_existing=drop_existing)
        self._metrics_indexer.build_index(drop_existing=drop_existing)
        self._examples_indexer.build_index(drop_existing=drop_existing)

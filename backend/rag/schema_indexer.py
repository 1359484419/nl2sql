"""
RAG Schema 索引器 — 将数据库 Schema 向量化存入 Milvus
支持表级 chunk + 字段级 chunk 两种粒度
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pymilvus import MilvusClient, DataType

from backend.rag.embedding import embedding_model
from backend.config import settings
from backend.schemas.saas_bi_schema import SAAS_BI_SCHEMA


def _build_column_description(col: Dict[str, Any]) -> str:
    nullable_str = "（必填）" if not col.get("nullable", True) else "（可空）"
    pk_str = "【主键】" if col.get("primary_key") else ""
    return (
        f"字段名：{col['name']}，类型：{col['type']}，含义：{col['comment']}"
        f"{pk_str}{nullable_str}"
    )


def _build_table_chunk(table: Dict[str, Any], chunk_id: str) -> Dict[str, Any]:
    columns_desc = "\n".join(
        _build_column_description(col) for col in table["columns"]
    )
    text = (
        f"【数据库表】{table['table_name']}\n"
        f"【表说明】{table['table_comment']}\n"
        f"【字段列表】\n{columns_desc}\n"
        f"【常见查询场景】\n"
        f"  - 统计 {table['table_name']} 的记录数\n"
        f"  - 按各维度聚合 {table['table_name']} 的关键指标\n"
        f"  - 关联查询 {table['table_name']} 与其他表的数据\n"
    )
    return {
        "chunk_id": chunk_id,
        "table_name": table["table_name"],
        "table_comment": table["table_comment"],
        "text": text,
        "column_count": len(table["columns"]),
        "primary_key": next((c["name"] for c in table["columns"] if c.get("primary_key")), ""),
    }


def _build_column_chunk(table: Dict[str, Any], col: Dict[str, Any], chunk_id: str) -> Dict[str, Any]:
    text = (
        f"【字段】{table['table_name']}.{col['name']}\n"
        f"【类型】{col['type']}\n"
        f"【业务含义】{col['comment']}\n"
        f"【所属表】{table['table_name']}（{table['table_comment']}）\n"
        f"【使用场景】\n"
        f"  - 用于 SELECT 列表：SELECT {col['name']}\n"
        f"  - 用于 WHERE 条件过滤\n"
        f"  - 用于 GROUP BY 分组聚合\n"
    )
    return {
        "chunk_id": chunk_id,
        "table_name": table["table_name"],
        "column_name": col["name"],
        "column_comment": col["comment"],
        "text": text,
    }


class SchemaIndexer:
    """Schema 向量索引器，使用 Milvus 存储"""

    def __init__(self):
        self._client: Optional[MilvusClient] = None
        self._collection_name = settings.milvus_collection_schema
        self._dim = embedding_model.dimension
        self._connect()

    def _connect(self):
        """连接 Milvus Lite（本地文件模式，无需 Docker）"""
        db_path = Path(settings.milvus_data_dir)
        db_path.mkdir(parents=True, exist_ok=True)
        db_file = db_path / "milvus_saas_bi.db"
        self._client = MilvusClient(uri=str(db_file))
        print(f"[SchemaIndexer] Milvus Lite 已连接: {db_file}")

    def _ensure_collection(self, drop_existing: bool = False):
        """确保 Milvus Collection 存在"""
        if self._client.has_collection(self._collection_name):
            if drop_existing:
                self._client.drop_collection(self._collection_name)
                print(f"[SchemaIndexer] 已删除旧 Collection: {self._collection_name}")
            else:
                print(f"[SchemaIndexer] Collection 已存在: {self._collection_name}")
                return

        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=True,
            description="SaaS BI 系统数据库 Schema 向量索引",
        )
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self._dim)
        schema.add_field(field_name="chunk_id", datatype=DataType.VARCHAR, max_length=200)
        schema.add_field(field_name="chunk_type", datatype=DataType.VARCHAR, max_length=20)
        schema.add_field(field_name="table_name", datatype=DataType.VARCHAR, max_length=100)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=4000)
        schema.add_field(field_name="metadata", datatype=DataType.VARCHAR, max_length=1000)

        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )
        index_params.add_index(field_name="chunk_id")

        self._client.create_collection(
            collection_name=self._collection_name,
            schema=schema,
            index_params=index_params,
        )
        print(f"[SchemaIndexer] 创建 Collection: {self._collection_name}，维度={self._dim}")

    def build_index(self, drop_existing: bool = False):
        """构建 Schema 向量索引"""
        self._ensure_collection(drop_existing=drop_existing)

        all_chunks: List[Dict[str, Any]] = []
        for table in SAAS_BI_SCHEMA["tables"]:
            all_chunks.append(_build_table_chunk(table, f"table_{table['table_name']}"))
            for col in table["columns"]:
                all_chunks.append(_build_column_chunk(table, col, f"col_{table['table_name']}_{col['name']}"))

        print(f"[SchemaIndexer] 共生成 {len(all_chunks)} 个文本块，开始向量化...")

        texts = [c["text"] for c in all_chunks]
        vectors = embedding_model.embed_documents(texts)

        entities = [
            {
                "chunk_id": c["chunk_id"],
                "chunk_type": "table" if c["chunk_id"].startswith("table_") else "column",
                "table_name": c["table_name"],
                "text": c["text"],
                "metadata": json.dumps(c, ensure_ascii=False, default=str),
                "vector": vec,
            }
            for c, vec in zip(all_chunks, vectors)
        ]

        self._client.insert(collection_name=self._collection_name, data=entities)
        print(f"[SchemaIndexer] ✅ 索引构建完成，共插入 {len(entities)} 条向量")

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """检索与用户问题最相关的 Schema 片段"""
        query_vector = embedding_model.embed_query(query)

        results = self._client.search(
            collection_name=self._collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["chunk_id", "chunk_type", "table_name", "text", "metadata"],
            search_params={"metric_type": "COSINE", "params": {}},
        )

        hits = []
        for hit in results[0]:
            metadata = json.loads(hit.get("metadata", "{}"))
            hits.append({
                "chunk_id": hit["entity"]["chunk_id"],
                "chunk_type": hit["entity"]["chunk_type"],
                "table_name": hit["entity"]["table_name"],
                "text": hit["entity"]["text"],
                "score": hit.get("distance", 0),
                "metadata": metadata,
            })

        return hits

"""
Day 13 — 练习 13-1：Milvus 基础操作
"""

from pymilvus import MilvusClient, DataType
from pathlib import Path

db_file = Path(__file__).parent / "milvus_demo.db"
client = MilvusClient(uri=str(db_file))
COLLECTION = "demo_nl2sql"

# 删除旧 collection
if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)

# 定义 Schema
schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=True)
schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=4)
schema.add_field(field_name="description", datatype=DataType.VARCHAR, max_length=200)
schema.add_field(field_name="table_name", datatype=DataType.VARCHAR, max_length=50)

# 创建 Collection
client.create_collection(collection_name=COLLECTION, schema=schema)

# 插入数据
vectors = [
    [0.1, 0.2, 0.3, 0.4],   # 活跃用户时长
    [0.9, 0.8, 0.7, 0.6],   # 天气查询
    [0.5, 0.5, 0.5, 0.5],   # 部门统计
    [0.15, 0.25, 0.35, 0.42],  # 接近活跃用户时长
]
descs = [
    "fact_workspace: 用户活跃时长、活跃时间",
    "天气查询、气温、降水概率",
    "fact_department: 部门人数、部门统计",
    "用户使用时长、日活跃用户数",
]
tables = ["fact_workspace", "weather", "fact_department", "fact_workspace"]

entities = [
    {"vector": v, "description": d, "table_name": t}
    for v, d, t in zip(vectors, descs, tables)
]
client.insert(collection_name=COLLECTION, data=entities)

print("=" * 50)
print("  Milvus 基础操作测试")
print("=" * 50)

# 检索
test_queries = [
    "各部门用户平均使用时长",
    "今天天气怎么样",
]
for q in test_queries:
    # 模拟向量（用随机向量代替）
    import numpy as np
    np.random.seed(hash(q) % 100)
    query_vec = [np.random.rand(4).tolist()]
    results = client.search(
        collection_name=COLLECTION,
        data=query_vec,
        limit=2,
        output_fields=["description", "table_name"]
    )
    print(f"\n查询: {q}")
    for r in results[0]:
        print(f"  → {r['entity']['table_name']}: {r['entity']['description']} (距离: {r['distance']:.4f})")

print("\n✅ Milvus 操作完成！")

"""
Day 23 — 练习 23-2：BM25 混合检索实现

此脚本展示 BM25 + 向量检索的融合逻辑
运行此脚本查看效果
"""

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print("请先安装 rank-bm25: pip install rank-bm25")
    import sys; sys.exit(1)

documents = [
    "fact_workspace: org_id, user_id, record_date, total_active_time_seconds",
    "fact_meeting: org_id, meeting_id, duration_minutes, start_time",
    "fact_calling: org_id, caller_id, call_duration_seconds, call_date",
    "fact_messaging: org_id, sender_id, message_count, send_date",
]

# 模拟向量检索结果（按顺序）
vector_results = [0, 1, 2, 3]  # 假设向量检索按文档顺序返回

# BM25 检索
tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

test_queries = [
    "各部门用户平均使用时长",
    "会议总时长",
    "通话记录查询",
]

print("=" * 55)
print("  BM25 + RRF 混合检索")
print("=" * 55)

for query in test_queries:
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_ranking = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)

    # RRF 融合（k=60）
    k = 60
    rrf_scores = {}
    for rank, idx in enumerate(vector_results):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank)
    for rank, idx in enumerate(bm25_ranking):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank)

    final_ranking = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    print(f"\n问题: {query}")
    print(f"  向量检索: {documents[vector_results[0]][:50]}...")
    print(f"  BM25 排序: {[documents[i][:30] for i in bm25_ranking[:2]]}")
    print(f"  RRF 最终: {[documents[i][:30] for i, _ in final_ranking[:2]]}")

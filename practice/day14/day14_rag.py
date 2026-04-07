"""
Day 14 — 练习 14-1：简化版 RAG
"""

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

documents = [
    {"text": "fact_workspace: org_id(租户ID), user_id(用户ID), record_date(日期), total_active_time_seconds(用户活跃时长)",
     "table": "fact_workspace", "desc": "用户活跃数据"},
    {"text": "fact_meeting: org_id, meeting_id, duration_minutes, start_time, host_user_id",
     "table": "fact_meeting", "desc": "会议数据"},
    {"text": "fact_calling: org_id, caller_id, call_duration_seconds, call_date",
     "table": "fact_calling", "desc": "通话数据"},
    {"text": "fact_messaging: org_id, sender_id, message_count, send_date",
     "table": "fact_messaging", "desc": "消息数据"},
]

# 模拟用户问题
questions = [
    "各部门用户平均使用时长",
    "过去7天开了多少会议",
    "通话时长最长的10个人",
]

print("=" * 50)
print("  简化版 NL2SQL RAG")
print("=" * 50)

vectorizer = TfidfVectorizer()
docs_texts = [d["text"] for d in documents]
vectors = vectorizer.fit_transform(docs_texts).toarray()

for question in questions:
    q_vec = vectorizer.transform([question]).toarray()[0]
    similarities = [np.dot(q_vec, v) / (np.linalg.norm(q_vec) * np.linalg.norm(v) + 1e-9) for v in vectors]
    best_idx = int(np.argmax(similarities))
    best_doc = documents[best_idx]
    print(f"\n问题: {question}")
    print(f"  → 找到表: {best_doc['table']} ({best_doc['desc']})")
    print(f"  → 相似度: {similarities[best_idx]:.4f}")
    print(f"  → 可用字段: {best_doc['text'][:60]}...")

"""
Day 12 — 练习 12-1：用 TF-IDF 计算语义相似度
"""

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

texts = [
    "各部门用户平均使用时长",
    "每个部门员工的活跃时间",
    "今天天气怎么样",
    "明天的会议安排",
]

vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(texts).toarray()

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)

print("=" * 50)
print("  TF-IDF 语义相似度计算")
print("=" * 50)
print("\n文本：")
for i, t in enumerate(texts):
    print(f"  {i+1}. {t}")

print("\n相似度矩阵：")
pairs = [
    ("使用时长", "活跃时间", 0, 1),
    ("使用时长", "天气", 0, 2),
    ("活跃时间", "天气", 1, 2),
    ("会议安排", "天气", 3, 2),
]
for label1, label2, i, j in pairs:
    sim = cosine_sim(vectors[i], vectors[j])
    bar = "█" * int(sim * 20) + "░" * (20 - int(sim * 20))
    flag = "✅（相关）" if sim > 0.1 else "❌（不相关）"
    print(f"  {label1} vs {label2}: {sim:.4f} {bar} {flag}")

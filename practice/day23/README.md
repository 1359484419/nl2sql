# Day 23 — BM25 混合检索

## 今日目标

给 NL2SQL 的 RAG 加一路 BM25 关键词检索，用 RRF 融合向量和关键词两路结果。

## 练习 23-1：安装 BM25（必做）

```bash
pip install rank-bm25
```

---

## 练习 23-2：实现 BM25 检索（必做）

修改 `backend/rag/retriever.py`，在 `UnifiedRetriever` 类里：

1. `__init__` 里加 `_bm25: Optional[BM25Okapi] = None`
2. 新增 `_ensure_bm25()` 方法，构建 BM25 索引
3. `search()` 方法里加一路 BM25 检索
4. 用 RRF 融合两路结果

---

## 练习 23-3：对比测试（必做）

修改后重启服务，对比改进前后的检索质量。

新建 `day23_test.py` 记录测试结果。

# Day 17 — NL2SQL LangGraph 状态图

```mermaid
flowchart TD
    START([开始]) --> A[classify_intent\n意图分类]
    A --> B[retrieve\nRAG 检索]
    B --> C{generate\n生成 SQL}
    C --> D{validate\n校验 SQL}
    D -->|通过| E[execute\n执行 SQL]
    D -->|失败| C
    C -->|重试≥3次| F([失败])
    E --> G[chart\n图表推荐]
    G --> END([结束])
    F --> END

    style START fill:#1a2e1a,stroke:#4ade80,color:#4ade80
    style END fill:#2e1a3a,stroke:#7c6af7,color:#7c6af7
    style F fill:#3a1e2e,stroke:#fb7185,color:#fb7185
    style D fill:#3a2e1a,stroke:#fb923c,color:#fb923c
```

## 节点说明

| 节点 | 作用 | 输入 | 输出 |
|------|------|------|------|
| classify_intent | 判断用户意图 | question | intent |
| retrieve | RAG 检索 | question | schema_context |
| generate | LLM 生成 SQL | question + schema | generated_sql |
| validate | EXPLAIN 校验 | generated_sql | sql_valid |
| execute | 执行 SQL | sql_valid=True | sql_result_data |
| chart | 图表推荐 | sql_result_data | chart_config |

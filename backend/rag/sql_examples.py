"""
RAG SQL 示例库 — 存储标准查询示例，供 LLM 参考生成更准确的 SQL
这些示例涵盖常见 BI 场景：趋势分析、部门对比、TOP N、环比同比等
"""

SQL_EXAMPLES = [
    # ─── 会议趋势分析 ───────────────────────────────────────────
    {
        "example_id": "meeting_trend_daily",
        "question_pattern": "每天会议数量趋势",
        "sql": """
SELECT DATE(start_time) AS date,
       COUNT(*) AS meeting_count,
       AVG(actual_duration_seconds) / 60.0 AS avg_duration_minutes,
       SUM(participant_count) AS total_participants,
       AVG(participant_count) AS avg_participants
FROM fact_meeting
WHERE org_id = '{org_id}'
  AND meeting_status = 'ended'
  AND start_time >= '{start_date}'
  AND start_time < '{end_date}'
GROUP BY DATE(start_time)
ORDER BY date;
""",
        "description": "按天统计会议数量、平均时长和参会人数趋势",
        "applicable_charts": ["line", "bar"],
        "tags": ["趋势", "日", "会议"],
    },
    {
        "example_id": "meeting_by_department",
        "question_pattern": "各部门会议数量对比",
        "sql": """
SELECT host_department AS department,
       COUNT(*) AS meeting_count,
       SUM(actual_duration_seconds) / 3600.0 AS total_hours,
       AVG(actual_duration_seconds) / 60.0 AS avg_duration_minutes
FROM fact_meeting
WHERE org_id = '{org_id}'
  AND meeting_status = 'ended'
  AND start_time >= '{start_date}'
  AND start_time < '{end_date}'
GROUP BY host_department
ORDER BY meeting_count DESC;
""",
        "description": "按主持人部门统计会议数量和总时长",
        "applicable_charts": ["bar", "pie"],
        "tags": ["部门", "对比", "会议"],
    },
    {
        "example_id": "meeting_quality_by_dept",
        "question_pattern": "各部门会议质量评分",
        "sql": """
SELECT department,
       AVG(quality_score) AS avg_quality_score,
       SUM(CASE WHEN connection_quality = 'excellent' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS excellent_rate,
       SUM(CASE WHEN connection_quality = 'poor' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS poor_rate
FROM fact_meeting fm
JOIN fact_quality fq ON fm.meeting_id = fq.meeting_id AND fm.org_id = fq.org_id
WHERE fm.org_id = '{org_id}'
  AND fm.meeting_status = 'ended'
  AND fm.start_time >= '{start_date}'
  AND fm.start_time < '{end_date}'
GROUP BY department
ORDER BY avg_quality_score DESC;
""",
        "description": "按部门统计会议质量评分和连接质量分布",
        "applicable_charts": ["bar", "radar"],
        "tags": ["质量", "部门", "连接"],
    },
    {
        "example_id": "top_users_meeting_hours",
        "question_pattern": "开会时长最多的用户 TOP 10",
        "sql": """
SELECT u.display_name AS user_name,
       u.department,
       COUNT(DISTINCT fm.meeting_id) AS meeting_count,
       SUM(fm.actual_duration_seconds) / 3600.0 AS total_hours,
       AVG(fm.actual_duration_seconds) / 60.0 AS avg_duration_minutes
FROM fact_meeting fm
JOIN dim_user u ON fm.host_user_id = u.user_id AND fm.org_id = u.org_id
WHERE fm.org_id = '{org_id}'
  AND fm.meeting_status = 'ended'
  AND fm.start_time >= '{start_date}'
  AND fm.start_time < '{end_date}'
GROUP BY u.display_name, u.department
ORDER BY total_hours DESC
LIMIT 10;
""",
        "description": "按主持人统计总会议时长 TOP 10 用户",
        "applicable_charts": ["bar", "table"],
        "tags": ["TOP N", "用户", "会议时长"],
    },

    # ─── 通话分析 ──────────────────────────────────────────────
    {
        "example_id": "call_trend_daily",
        "question_pattern": "每天通话数量和时长趋势",
        "sql": """
SELECT DATE(start_time) AS date,
       COUNT(*) AS call_count,
       SUM(CASE WHEN call_status = 'completed' THEN 1 ELSE 0 END) AS answered_calls,
       AVG(talk_duration_seconds) / 60.0 AS avg_talk_minutes,
       SUM(talk_duration_seconds) / 3600.0 AS total_talk_hours
FROM fact_calling
WHERE org_id = '{org_id}'
  AND start_time >= '{start_date}'
  AND start_time < '{end_date}'
GROUP BY DATE(start_time)
ORDER BY date;
""",
        "description": "按天统计通话数量、接通数和平均通话时长",
        "applicable_charts": ["line", "bar"],
        "tags": ["趋势", "日", "通话"],
    },
    {
        "example_id": "call_answer_rate_by_dept",
        "question_pattern": "各部门通话接通率",
        "sql": """
SELECT caller_department AS department,
       COUNT(*) AS total_calls,
       SUM(CASE WHEN call_status = 'completed' THEN 1 ELSE 0 END) AS answered,
       SUM(CASE WHEN call_status = 'missed' THEN 1 ELSE 0 END) AS missed,
       ROUND(SUM(CASE WHEN call_status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS answer_rate,
       AVG(talk_duration_seconds) / 60.0 AS avg_duration_minutes
FROM fact_calling
WHERE org_id = '{org_id}'
  AND start_time >= '{start_date}'
  AND start_time < '{end_date}'
GROUP BY caller_department
ORDER BY answer_rate DESC;
""",
        "description": "按主叫部门统计通话接通率和漏接数",
        "applicable_charts": ["bar", "pie"],
        "tags": ["接通率", "部门", "通话"],
    },
    {
        "example_id": "call_type_distribution",
        "question_pattern": "通话类型分布（内部/外部/呼入/呼出）",
        "sql": """
SELECT call_type,
       call_direction,
       COUNT(*) AS call_count,
       AVG(talk_duration_seconds) / 60.0 AS avg_duration_minutes,
       SUM(CASE WHEN call_status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS answer_rate
FROM fact_calling
WHERE org_id = '{org_id}'
  AND start_time >= '{start_date}'
  AND start_time < '{end_date}'
GROUP BY call_type, call_direction
ORDER BY call_count DESC;
""",
        "description": "按通话类型和方向统计分布",
        "applicable_charts": ["pie", "bar"],
        "tags": ["分布", "类型", "通话"],
    },

    # ─── 工作空间分析 ──────────────────────────────────────────
    {
        "example_id": "workspace_daily_trend",
        "question_pattern": "每日用户活跃时长趋势",
        "sql": """
SELECT record_date,
       COUNT(DISTINCT user_id) AS active_users,
       SUM(total_active_time_seconds) / 3600.0 AS total_active_hours,
       AVG(total_active_time_seconds) / 3600.0 AS avg_active_hours_per_user,
       SUM(login_count) AS total_logins,
       SUM(file_created_count) AS files_created,
       SUM(task_completed_count) AS tasks_completed
FROM fact_workspace
WHERE org_id = '{org_id}'
  AND record_date >= '{start_date}'
  AND record_date < '{end_date}'
GROUP BY record_date
ORDER BY record_date;
""",
        "description": "按天统计活跃用户数、总活跃时长和人均时长",
        "applicable_charts": ["line", "area"],
        "tags": ["趋势", "日", "活跃度", "工作空间"],
    },
    {
        "example_id": "workspace_by_department",
        "question_pattern": "各部门用户使用时间对比",
        "sql": """
SELECT department,
       COUNT(DISTINCT user_id) AS user_count,
       SUM(total_active_time_seconds) / 3600.0 AS total_hours,
       AVG(total_active_time_seconds) / 3600.0 AS avg_hours_per_user,
       SUM(file_created_count + file_edited_count) AS total_file_ops,
       SUM(task_completed_count) AS tasks_completed
FROM fact_workspace
WHERE org_id = '{org_id}'
  AND record_date >= '{start_date}'
  AND record_date < '{end_date}'
GROUP BY department
ORDER BY total_hours DESC;
""",
        "description": "按部门统计用户数、总使用时长和人均时长",
        "applicable_charts": ["bar", "pie"],
        "tags": ["部门", "对比", "使用时长"],
    },
    {
        "example_id": "feature_usage",
        "question_pattern": "功能使用排行",
        "sql": """
SELECT u.department,
       COUNT(DISTINCT fw.user_id) AS active_users,
       SUM(fw.file_created_count) AS file_created,
       SUM(fw.file_edited_count) AS file_edited,
       SUM(fw.comment_count) AS comments,
       SUM(fw.task_created_count) AS tasks_created,
       SUM(fw.task_completed_count) AS tasks_completed
FROM fact_workspace fw
JOIN dim_user u ON fw.user_id = u.user_id AND fw.org_id = u.org_id
WHERE fw.org_id = '{org_id}'
  AND fw.record_date >= '{start_date}'
  AND fw.record_date < '{end_date}'
GROUP BY u.department
ORDER BY active_users DESC;
""",
        "description": "按部门统计各功能模块的使用次数",
        "applicable_charts": ["bar", "radar"],
        "tags": ["功能", "部门", "使用分析"],
    },

    # ─── 消息分析 ──────────────────────────────────────────────
    {
        "example_id": "messaging_trend_hourly",
        "question_pattern": "每小时消息发送量（活跃时段分析）",
        "sql": """
SELECT EXTRACT(HOUR FROM sent_time) AS hour,
       COUNT(*) AS message_count,
       COUNT(DISTINCT sender_user_id) AS active_senders,
       SUM(reaction_count) AS total_reactions,
       SUM(CASE WHEN is_reply = TRUE THEN 1 ELSE 0 END) AS reply_count
FROM fact_messaging
WHERE org_id = '{org_id}'
  AND is_deleted = FALSE
  AND sent_time >= '{start_date}'
  AND sent_time < '{end_date}'
GROUP BY EXTRACT(HOUR FROM sent_time)
ORDER BY hour;
""",
        "description": "按小时统计消息发送量，分析活跃时段",
        "applicable_charts": ["line", "bar"],
        "tags": ["时段", "小时", "消息", "趋势"],
    },
    {
        "example_id": "messaging_by_department",
        "question_pattern": "各部门消息发送量",
        "sql": """
SELECT sender_department AS department,
       COUNT(*) AS message_count,
       COUNT(DISTINCT sender_user_id) AS active_users,
       COUNT(DISTINCT channel_id) AS active_channels,
       AVG(reaction_count) AS avg_reactions_per_message
FROM fact_messaging
WHERE org_id = '{org_id}'
  AND is_deleted = FALSE
  AND sent_time >= '{start_date}'
  AND sent_time < '{end_date}'
GROUP BY sender_department
ORDER BY message_count DESC;
""",
        "description": "按发送者部门统计消息数量和互动情况",
        "applicable_charts": ["bar", "pie"],
        "tags": ["部门", "消息", "对比"],
    },

    # ─── 设备使用分析 ───────────────────────────────────────────
    {
        "example_id": "device_usage_distribution",
        "question_pattern": "设备使用分布（桌面端/移动端占比）",
        "sql": """
SELECT device_type,
       os_platform,
       COUNT(DISTINCT user_id) AS user_count,
       SUM(total_active_time_seconds) / 3600.0 AS total_hours,
       ROUND(COUNT(DISTINCT user_id) * 100.0 / NULLIF(SUM(COUNT(DISTINCT user_id)) OVER (), 0), 2) AS user_pct
FROM fact_device_usage
WHERE org_id = '{org_id}'
  AND record_date >= '{start_date}'
  AND record_date < '{end_date}'
GROUP BY device_type, os_platform
ORDER BY total_hours DESC;
""",
        "description": "按设备和操作系统统计用户数和使用时长分布",
        "applicable_charts": ["pie", "bar"],
        "tags": ["设备", "分布", "操作系统"],
    },

    # ─── 综合质量分析 ───────────────────────────────────────────
    {
        "example_id": "quality_trend",
        "question_pattern": "每日质量评分趋势",
        "sql": """
SELECT record_date,
       AVG(quality_score) AS avg_quality_score,
       AVG(avg_latency_ms) AS avg_latency,
       AVG(avg_packet_loss_rate) * 100 AS avg_packet_loss_pct,
       SUM(connection_failures) AS total_failures,
       SUM(poor_sessions) * 100.0 / NULLIF(SUM(total_sessions), 0) AS poor_rate
FROM fact_quality
WHERE org_id = '{org_id}'
  AND record_date >= '{start_date}'
  AND record_date < '{end_date}'
GROUP BY record_date
ORDER BY record_date;
""",
        "description": "按天统计质量评分、延迟、丢包率和连接失败趋势",
        "applicable_charts": ["line", "area"],
        "tags": ["质量", "趋势", "日"],
    },

    # ─── 同比环比 ──────────────────────────────────────────────
    {
        "example_id": "meeting_mom_comparison",
        "question_pattern": "本月与上月会议数量环比",
        "sql": """
WITH this_month AS (
    SELECT COUNT(*) AS this_month_count,
           AVG(actual_duration_seconds) / 60.0 AS this_avg_duration
    FROM fact_meeting
    WHERE org_id = '{org_id}'
      AND meeting_status = 'ended'
      AND start_time >= DATE_TRUNC('month', CURRENT_DATE)
),
last_month AS (
    SELECT COUNT(*) AS last_month_count,
           AVG(actual_duration_seconds) / 60.0 AS last_avg_duration
    FROM fact_meeting
    WHERE org_id = '{org_id}'
      AND meeting_status = 'ended'
      AND start_time >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
      AND start_time < DATE_TRUNC('month', CURRENT_DATE)
)
SELECT lm.last_month_count AS last_month_meetings,
       tm.this_month_count AS this_month_meetings,
       tm.this_month_count - lm.last_month_count AS change,
       ROUND((tm.this_month_count - lm.last_month_count) * 100.0 / NULLIF(lm.last_month_count, 0), 2) AS mom_change_pct,
       lm.last_avg_duration AS last_avg_duration,
       tm.this_avg_duration AS this_avg_duration
FROM last_month lm, this_month tm;
""",
        "description": "本月与上月会议数量和平均时长环比",
        "applicable_charts": ["bar", "table"],
        "tags": ["环比", "同比", "会议"],
    },
]

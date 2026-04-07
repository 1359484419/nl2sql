"""
PostgreSQL 数据库 Schema — 企业协作 SaaS 平台
支持模块：Meeting（会议）、Calling（通话）、Workspace（工作空间）、Messaging（消息）
多租户架构：org_id 隔离不同公司数据
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 维度表（Dimensions）
# ═══════════════════════════════════════════════════════════════════════════════

DIM_TENANT = {
    "table_name": "dim_tenant",
    "table_comment": "租户（公司）维度表",
    "columns": [
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "租户唯一标识（UUID）"},
        {"name": "tenant_name", "type": "VARCHAR(200)", "nullable": False, "comment": "公司名称"},
        {"name": "industry", "type": "VARCHAR(100)", "nullable": True, "comment": "所属行业"},
        {"name": "plan_type", "type": "VARCHAR(30)", "nullable": True, "comment": "套餐类型：free/starter/pro/enterprise"},
        {"name": "seats_total", "type": "INT", "nullable": True, "comment": "总席位数"},
        {"name": "seats_used", "type": "INT", "nullable": True, "comment": "已使用席位数"},
        {"name": "timezone", "type": "VARCHAR(50)", "nullable": True, "comment": "公司时区"},
        {"name": "country", "type": "VARCHAR(50)", "nullable": True, "comment": "国家"},
        {"name": "registered_at", "type": "TIMESTAMP", "nullable": True, "comment": "注册时间"},
        {"name": "trial_expires_at", "type": "TIMESTAMP", "nullable": True, "comment": "试用期截止时间"},
        {"name": "status", "type": "VARCHAR(20)", "nullable": True, "comment": "状态：active/trial/suspended/cancelled"},
    ],
}

DIM_USER = {
    "table_name": "dim_user",
    "table_comment": "用户维度表",
    "columns": [
        {"name": "user_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "用户唯一标识（UUID）"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "所属租户 ID"},
        {"name": "username", "type": "VARCHAR(100)", "nullable": False, "comment": "用户名"},
        {"name": "display_name", "type": "VARCHAR(200)", "nullable": True, "comment": "显示名称"},
        {"name": "email", "type": "VARCHAR(200)", "nullable": True, "comment": "邮箱"},
        {"name": "phone", "type": "VARCHAR(30)", "nullable": True, "comment": "手机号"},
        {"name": "department", "type": "VARCHAR(100)", "nullable": True, "comment": "部门"},
        {"name": "job_title", "type": "VARCHAR(100)", "nullable": True, "comment": "职位"},
        {"name": "role", "type": "VARCHAR(30)", "nullable": True, "comment": "角色：admin/supervisor/member"},
        {"name": "is_supervisor", "type": "BOOLEAN", "nullable": True, "comment": "是否为管理员/主管（可看 Dashboard）"},
        {"name": "status", "type": "VARCHAR(20)", "nullable": True, "comment": "状态：active/inactive/suspended"},
        {"name": "device_type", "type": "VARCHAR(30)", "nullable": True, "comment": "常用设备类型：desktop/mobile/tablet"},
        {"name": "os_platform", "type": "VARCHAR(30)", "nullable": True, "comment": "操作系统：windows/macOS/iOS/Android"},
        {"name": "registered_at", "type": "TIMESTAMP", "nullable": True, "comment": "注册时间"},
        {"name": "last_active_at", "type": "TIMESTAMP", "nullable": True, "comment": "最后活跃时间"},
        {"name": "first_login_at", "type": "TIMESTAMP", "nullable": True, "comment": "首次登录时间"},
    ],
}

DIM_MEETING_ROOM = {
    "table_name": "dim_meeting_room",
    "table_comment": "会议室维度表（虚拟会议室）",
    "columns": [
        {"name": "room_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "会议室 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "所属租户 ID"},
        {"name": "room_name", "type": "VARCHAR(200)", "nullable": False, "comment": "会议室名称"},
        {"name": "room_type", "type": "VARCHAR(30)", "nullable": True, "comment": "会议室类型：instant(即时)/scheduled(预约)/recurring(周期)"},
        {"name": "max_participants", "type": "INT", "nullable": True, "comment": "最大参会人数"},
        {"name": "has_recording", "type": "BOOLEAN", "nullable": True, "comment": "是否开启录制"},
        {"name": "has_screen_share", "type": "BOOLEAN", "nullable": True, "comment": "是否开启屏幕共享"},
        {"name": "created_by", "type": "VARCHAR(36)", "nullable": True, "comment": "创建人 user_id"},
        {"name": "created_at", "type": "TIMESTAMP", "nullable": True, "comment": "创建时间"},
        {"name": "status", "type": "VARCHAR(20)", "nullable": True, "comment": "状态：active/inactive"},
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# 事实表（Facts）
# ═══════════════════════════════════════════════════════════════════════════════

FACT_MEETING = {
    "table_name": "fact_meeting",
    "table_comment": "会议事实表 — 记录每个会议的关键数据",
    "columns": [
        {"name": "meeting_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "会议 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "租户 ID"},
        {"name": "room_id", "type": "VARCHAR(36)", "nullable": True, "comment": "会议室 ID"},
        {"name": "host_user_id", "type": "VARCHAR(36)", "nullable": False, "comment": "主持人 user_id"},
        {"name": "host_department", "type": "VARCHAR(100)", "nullable": True, "comment": "主持人部门"},
        {"name": "meeting_no", "type": "VARCHAR(50)", "nullable": False, "comment": "会议号"},
        {"name": "meeting_type", "type": "VARCHAR(30)", "nullable": True, "comment": "会议类型：instant/scheduled/webinar/recurring"},
        {"name": "start_time", "type": "TIMESTAMP", "nullable": False, "comment": "会议开始时间"},
        {"name": "end_time", "type": "TIMESTAMP", "nullable": True, "comment": "会议结束时间"},
        {"name": "duration_seconds", "type": "INT", "nullable": True, "comment": "会议持续时长（秒）"},
        {"name": "actual_duration_seconds", "type": "INT", "nullable": True, "comment": "实际通话时长（秒，扣除前后缓冲）"},
        {"name": "participant_count", "type": "INT", "nullable": True, "comment": "参会人数（含主持人）"},
        {"name": "peak_participants", "type": "INT", "nullable": True, "comment": "峰值参会人数"},
        {"name": "avg_participants", "type": "DECIMAL(6,2)", "nullable": True, "comment": "平均参会人数"},
        {"name": "total_messages", "type": "INT", "nullable": True, "comment": "会议中聊天消息数"},
        {"name": "screen_share_count", "type": "INT", "nullable": True, "comment": "屏幕共享次数"},
        {"name": "recording_duration_seconds", "type": "INT", "nullable": True, "comment": "录制时长（秒）"},
        {"name": "is_recorded", "type": "BOOLEAN", "nullable": True, "comment": "是否录制"},
        {"name": "is_international", "type": "BOOLEAN", "nullable": True, "comment": "是否含国际参会者"},
        {"name": "connection_quality", "type": "VARCHAR(20)", "nullable": True, "comment": "连接质量：excellent/good/poor"},
        {"name": "video_enabled_count", "type": "INT", "nullable": True, "comment": "开启视频的参会者数"},
        {"name": "audio_enabled_count", "type": "INT", "nullable": True, "comment": "开启音频的参会者数"},
        {"name": "meeting_status", "type": "VARCHAR(20)", "nullable": True, "comment": "会议状态：ended/cancelled/in_progress"},
        {"name": "end_reason", "type": "VARCHAR(30)", "nullable": True, "comment": "结束原因：host_end/timeout/all_left"},
    ],
}

FACT_MEETING_PARTICIPANT = {
    "table_name": "fact_meeting_participant",
    "table_comment": "会议参会者事实表 — 记录每个参会者在每个会议中的详细行为",
    "columns": [
        {"name": "record_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "记录 ID"},
        {"name": "meeting_id", "type": "VARCHAR(36)", "nullable": False, "comment": "会议 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "租户 ID"},
        {"name": "user_id", "type": "VARCHAR(36)", "nullable": False, "comment": "用户 ID"},
        {"name": "department", "type": "VARCHAR(100)", "nullable": True, "comment": "用户部门"},
        {"name": "join_time", "type": "TIMESTAMP", "nullable": True, "comment": "加入时间"},
        {"name": "leave_time", "type": "TIMESTAMP", "nullable": True, "comment": "离开时间"},
        {"name": "join_duration_seconds", "type": "INT", "nullable": True, "comment": "在会议中的总时长（秒）"},
        {"name": "is_host", "type": "BOOLEAN", "nullable": True, "comment": "是否主持人"},
        {"name": "is_co_host", "type": "BOOLEAN", "nullable": True, "comment": "是否联席主持人"},
        {"name": "is_presenter", "type": "BOOLEAN", "nullable": True, "comment": "是否主讲人"},
        {"name": "video_enabled", "type": "BOOLEAN", "nullable": True, "comment": "是否开启视频"},
        {"name": "audio_enabled", "type": "BOOLEAN", "nullable": True, "comment": "是否开启音频"},
        {"name": "screen_shared", "type": "BOOLEAN", "nullable": True, "comment": "是否进行过屏幕共享"},
        {"name": "chat_messages_count", "type": "INT", "nullable": True, "comment": "发送聊天消息数"},
        {"name": "reaction_count", "type": "INT", "nullable": True, "comment": "发送表情反应数"},
        {"name": "hand_raised", "type": "BOOLEAN", "nullable": True, "comment": "是否举手"},
        {"name": "connection_quality", "type": "VARCHAR(20)", "nullable": True, "comment": "个人连接质量：excellent/good/poor"},
        {"name": "join_source", "type": "VARCHAR(30)", "nullable": True, "comment": "入会方式：desktop/mobile/web/phone"},
        {"name": "late_seconds", "type": "INT", "nullable": True, "comment": "迟到秒数（相对会议开始时间）"},
        {"name": "early_leave_seconds", "type": "INT", "nullable": True, "comment": "早退秒数（相对会议结束时间）"},
        {"name": "status", "type": "VARCHAR(20)", "nullable": True, "comment": "参会状态：joined/left/error"},
    ],
}

FACT_CALLING = {
    "table_name": "fact_calling",
    "table_comment": "通话事实表 — 记录每个通话的详细信息",
    "columns": [
        {"name": "call_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "通话 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "租户 ID"},
        {"name": "caller_user_id", "type": "VARCHAR(36)", "nullable": False, "comment": "主叫用户 ID"},
        {"name": "caller_department", "type": "VARCHAR(100)", "nullable": True, "comment": "主叫用户部门"},
        {"name": "callee_user_id", "type": "VARCHAR(36)", "nullable": True, "comment": "被叫用户 ID（外部用户可为空）"},
        {"name": "callee_department", "type": "VARCHAR(100)", "nullable": True, "comment": "被叫用户部门"},
        {"name": "call_type", "type": "VARCHAR(20)", "nullable": True, "comment": "通话类型：internal/external/inbound/outbound"},
        {"name": "call_direction", "type": "VARCHAR(20)", "nullable": True, "comment": "呼叫方向：outgoing/incoming"},
        {"name": "start_time", "type": "TIMESTAMP", "nullable": False, "comment": "通话开始时间"},
        {"name": "answer_time", "type": "TIMESTAMP", "nullable": True, "comment": "接听时间（空则未接通）"},
        {"name": "end_time", "type": "TIMESTAMP", "nullable": True, "comment": "通话结束时间"},
        {"name": "ring_duration_seconds", "type": "INT", "nullable": True, "comment": "响铃时长（秒）"},
        {"name": "talk_duration_seconds", "type": "INT", "nullable": True, "comment": "通话时长（秒，从接听到挂断）"},
        {"name": "total_duration_seconds", "type": "INT", "nullable": True, "comment": "总时长（包含响铃，秒）"},
        {"name": "call_status", "type": "VARCHAR(20)", "nullable": True, "comment": "通话状态：completed/missed/voicemail/rejected/busy/failed"},
        {"name": "has_video", "type": "BOOLEAN", "nullable": True, "comment": "是否视频通话"},
        {"name": "has_screen_share", "type": "BOOLEAN", "nullable": True, "comment": "是否进行屏幕共享"},
        {"name": "recording_enabled", "type": "BOOLEAN", "nullable": True, "comment": "是否开启通话录制"},
        {"name": "connection_quality", "type": "VARCHAR(20)", "nullable": True, "comment": "连接质量：excellent/good/poor"},
        {"name": "device_type", "type": "VARCHAR(30)", "nullable": True, "comment": "主叫设备类型：desktop/mobile/phone"},
        {"name": "is_international", "type": "BOOLEAN", "nullable": True, "comment": "是否国际通话"},
        {"name": "transfer_count", "type": "INT", "nullable": True, "comment": "转接次数"},
        {"name": "hold_duration_seconds", "type": "INT", "nullable": True, "comment": "保持时长（秒）"},
    ],
}

FACT_WORKSPACE = {
    "table_name": "fact_workspace",
    "table_comment": "工作空间事实表 — 记录用户在工作空间中的活动",
    "columns": [
        {"name": "record_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "记录 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "租户 ID"},
        {"name": "user_id", "type": "VARCHAR(36)", "nullable": False, "comment": "用户 ID"},
        {"name": "department", "type": "VARCHAR(100)", "nullable": True, "comment": "用户部门"},
        {"name": "workspace_id", "type": "VARCHAR(36)", "nullable": True, "comment": "工作空间 ID"},
        {"name": "workspace_type", "type": "VARCHAR(30)", "nullable": True, "comment": "工作空间类型：personal/shared/team"},
        {"name": "record_date", "type": "DATE", "nullable": False, "comment": "记录日期（按天聚合）"},
        {"name": "login_count", "type": "INT", "nullable": True, "comment": "登录次数"},
        {"name": "total_active_time_seconds", "type": "INT", "nullable": True, "comment": "当日总活跃时长（秒，含所有操作）"},
        {"name": "total_idle_time_seconds", "type": "INT", "nullable": True, "comment": "当日总空闲时长（秒）"},
        {"name": "total_session_time_seconds", "type": "INT", "nullable": True, "comment": "当日总会话时长（秒）"},
        {"name": "file_created_count", "type": "INT", "nullable": True, "comment": "创建文件数"},
        {"name": "file_edited_count", "type": "INT", "nullable": True, "comment": "编辑文件数"},
        {"name": "file_viewed_count", "type": "INT", "nullable": True, "comment": "浏览文件数"},
        {"name": "file_uploaded_count", "type": "INT", "nullable": True, "comment": "上传文件数"},
        {"name": "file_downloaded_count", "type": "INT", "nullable": True, "comment": "下载文件数"},
        {"name": "comment_count", "type": "INT", "nullable": True, "comment": "发表评论数"},
        {"name": "task_created_count", "type": "INT", "nullable": True, "comment": "创建任务数"},
        {"name": "task_completed_count", "type": "INT", "nullable": True, "comment": "完成任务数"},
        {"name": "storage_used_mb", "type": "DECIMAL(15,2)", "nullable": True, "comment": "已使用存储空间（MB）"},
        {"name": "active_features", "type": "TEXT", "nullable": True, "comment": "当日使用过的功能列表（JSON 数组）"},
    ],
}

FACT_MESSAGING = {
    "table_name": "fact_messaging",
    "table_comment": "消息事实表 — 记录即时消息的发送和交互数据",
    "columns": [
        {"name": "message_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "消息 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "租户 ID"},
        {"name": "sender_user_id", "type": "VARCHAR(36)", "nullable": False, "comment": "发送者用户 ID"},
        {"name": "sender_department", "type": "VARCHAR(100)", "nullable": True, "comment": "发送者部门"},
        {"name": "channel_id", "type": "VARCHAR(36)", "nullable": True, "comment": "频道/群组 ID"},
        {"name": "channel_type", "type": "VARCHAR(30)", "nullable": True, "comment": "频道类型：dm(私聊)/group(群聊)/channel(频道)"},
        {"name": "sent_time", "type": "TIMESTAMP", "nullable": False, "comment": "消息发送时间"},
        {"name": "message_type", "type": "VARCHAR(30)", "nullable": True, "comment": "消息类型：text/image/file/emoji/reaction/poll"},
        {"name": "is_reply", "type": "BOOLEAN", "nullable": True, "comment": "是否为回复消息"},
        {"name": "reply_to_message_id", "type": "VARCHAR(36)", "nullable": True, "comment": "回复的消息 ID"},
        {"name": "reaction_count", "type": "INT", "nullable": True, "comment": "收到表情反应数"},
        {"name": "is_edited", "type": "BOOLEAN", "nullable": True, "comment": "是否被编辑过"},
        {"name": "is_deleted", "type": "BOOLEAN", "nullable": True, "comment": "是否被删除"},
        {"name": "read_receipt_count", "type": "INT", "nullable": True, "comment": "已读回执数"},
        {"name": "forward_count", "type": "INT", "nullable": True, "comment": "被转发次数"},
        {"name": "thread_reply_count", "type": "INT", "nullable": True, "comment": "thread 回复数（嵌套消息数）"},
        {"name": "emoji_mentions", "type": "TEXT", "nullable": True, "comment": "使用的表情符号列表（JSON）"},
    ],
}

FACT_DEVICE_USAGE = {
    "table_name": "fact_device_usage",
    "table_comment": "设备使用事实表 — 记录不同设备的使用分布",
    "columns": [
        {"name": "record_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "记录 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "租户 ID"},
        {"name": "user_id", "type": "VARCHAR(36)", "nullable": False, "comment": "用户 ID"},
        {"name": "department", "type": "VARCHAR(100)", "nullable": True, "comment": "用户部门"},
        {"name": "record_date", "type": "DATE", "nullable": False, "comment": "记录日期"},
        {"name": "os_platform", "type": "VARCHAR(30)", "nullable": True, "comment": "操作系统：windows/macOS/iOS/Android"},
        {"name": "device_type", "type": "VARCHAR(30)", "nullable": True, "comment": "设备类型：desktop/mobile/tablet"},
        {"name": "app_version", "type": "VARCHAR(30)", "nullable": True, "comment": "App 版本号"},
        {"name": "session_count", "type": "INT", "nullable": True, "comment": "登录会话数"},
        {"name": "total_active_time_seconds", "type": "INT", "nullable": True, "comment": "总活跃时长（秒）"},
        {"name": "feature_usage_count", "type": "INT", "nullable": True, "comment": "功能使用次数"},
        {"name": "network_type", "type": "VARCHAR(20)", "nullable": True, "comment": "网络类型：wifi/5g/4g/3g"},
        {"name": "is_primary_device", "type": "BOOLEAN", "nullable": True, "comment": "是否为主要使用设备"},
    ],
}

FACT_QUALITY = {
    "table_name": "fact_quality",
    "table_comment": "服务质量事实表 — 会议质量、连接质量等指标",
    "columns": [
        {"name": "record_id", "type": "VARCHAR(36)", "nullable": False, "primary_key": True, "comment": "记录 ID"},
        {"name": "org_id", "type": "VARCHAR(36)", "nullable": False, "comment": "租户 ID"},
        {"name": "user_id", "type": "VARCHAR(36)", "nullable": True, "comment": "用户 ID（可为 null 表示整体）"},
        {"name": "department", "type": "VARCHAR(100)", "nullable": True, "comment": "部门"},
        {"name": "record_date", "type": "DATE", "nullable": False, "comment": "记录日期"},
        {"name": "meeting_id", "type": "VARCHAR(36)", "nullable": True, "comment": "会议 ID（可为空表示整体统计）"},
        {"name": "session_type", "type": "VARCHAR(30)", "nullable": True, "comment": "会话类型：meeting/calling"},
        {"name": "total_sessions", "type": "INT", "nullable": True, "comment": "总会话数"},
        {"name": "excellent_sessions", "type": "INT", "nullable": True, "comment": "优质会话数（连接质量 excellent）"},
        {"name": "good_sessions", "type": "INT", "nullable": True, "comment": "良好会话数（连接质量 good）"},
        {"name": "poor_sessions", "type": "INT", "nullable": True, "comment": "较差会话数（连接质量 poor）"},
        {"name": "avg_video_bitrate_kbps", "type": "DECIMAL(10,2)", "nullable": True, "comment": "平均视频码率（Kbps）"},
        {"name": "avg_audio_bitrate_kbps", "type": "DECIMAL(10,2)", "nullable": True, "comment": "平均音频码率（Kbps）"},
        {"name": "avg_packet_loss_rate", "type": "DECIMAL(6,4)", "nullable": True, "comment": "平均丢包率（0~1）"},
        {"name": "avg_latency_ms", "type": "DECIMAL(10,2)", "nullable": True, "comment": "平均延迟（毫秒）"},
        {"name": "avg_jitter_ms", "type": "DECIMAL(10,2)", "nullable": True, "comment": "平均抖动（毫秒）"},
        {"name": "connection_failures", "type": "INT", "nullable": True, "comment": "连接失败次数"},
        {"name": "quality_score", "type": "DECIMAL(5,2)", "nullable": True, "comment": "综合质量评分（0-100）"},
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# 导出所有表定义
# ═══════════════════════════════════════════════════════════════════════════════

SAAS_BI_SCHEMA = {
    "tables": [
        DIM_TENANT,
        DIM_USER,
        DIM_MEETING_ROOM,
        FACT_MEETING,
        FACT_MEETING_PARTICIPANT,
        FACT_CALLING,
        FACT_WORKSPACE,
        FACT_MESSAGING,
        FACT_DEVICE_USAGE,
        FACT_QUALITY,
    ]
}

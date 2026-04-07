-- ============================================================
-- 企业协作 SaaS BI 系统 — PostgreSQL 建表脚本
-- 支持模块：Meeting / Calling / Workspace / Messaging / Device
-- ============================================================

-- 1. 租户维度表
CREATE TABLE IF NOT EXISTS dim_tenant (
    org_id VARCHAR(36) PRIMARY KEY,
    tenant_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    plan_type VARCHAR(30) DEFAULT 'starter',
    seats_total INT DEFAULT 10,
    seats_used INT DEFAULT 0,
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    country VARCHAR(50) DEFAULT 'China',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trial_expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- 2. 用户维度表
CREATE TABLE IF NOT EXISTS dim_user (
    user_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    username VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(30),
    department VARCHAR(100),
    job_title VARCHAR(100),
    role VARCHAR(30) DEFAULT 'member',
    is_supervisor BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',
    device_type VARCHAR(30),
    os_platform VARCHAR(30),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP,
    first_login_at TIMESTAMP,
    CONSTRAINT fk_user_tenant FOREIGN KEY (org_id) REFERENCES dim_tenant(org_id)
);

-- 3. 会议室维度表
CREATE TABLE IF NOT EXISTS dim_meeting_room (
    room_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    room_name VARCHAR(200) NOT NULL,
    room_type VARCHAR(30) DEFAULT 'instant',
    max_participants INT DEFAULT 100,
    has_recording BOOLEAN DEFAULT FALSE,
    has_screen_share BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- 4. 会议事实表
CREATE TABLE IF NOT EXISTS fact_meeting (
    meeting_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    room_id VARCHAR(36),
    host_user_id VARCHAR(36) NOT NULL,
    host_department VARCHAR(100),
    meeting_no VARCHAR(50) NOT NULL,
    meeting_type VARCHAR(30) DEFAULT 'instant',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INT,
    actual_duration_seconds INT,
    participant_count INT DEFAULT 0,
    peak_participants INT DEFAULT 0,
    avg_participants DECIMAL(6,2),
    total_messages INT DEFAULT 0,
    screen_share_count INT DEFAULT 0,
    recording_duration_seconds INT DEFAULT 0,
    is_recorded BOOLEAN DEFAULT FALSE,
    is_international BOOLEAN DEFAULT FALSE,
    connection_quality VARCHAR(20) DEFAULT 'good',
    video_enabled_count INT DEFAULT 0,
    audio_enabled_count INT DEFAULT 0,
    meeting_status VARCHAR(20) DEFAULT 'ended',
    end_reason VARCHAR(30)
);

-- 5. 会议参会者事实表
CREATE TABLE IF NOT EXISTS fact_meeting_participant (
    record_id VARCHAR(36) PRIMARY KEY,
    meeting_id VARCHAR(36) NOT NULL,
    org_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    department VARCHAR(100),
    join_time TIMESTAMP,
    leave_time TIMESTAMP,
    join_duration_seconds INT,
    is_host BOOLEAN DEFAULT FALSE,
    is_co_host BOOLEAN DEFAULT FALSE,
    is_presenter BOOLEAN DEFAULT FALSE,
    video_enabled BOOLEAN DEFAULT FALSE,
    audio_enabled BOOLEAN DEFAULT TRUE,
    screen_shared BOOLEAN DEFAULT FALSE,
    chat_messages_count INT DEFAULT 0,
    reaction_count INT DEFAULT 0,
    hand_raised BOOLEAN DEFAULT FALSE,
    connection_quality VARCHAR(20) DEFAULT 'good',
    join_source VARCHAR(30) DEFAULT 'desktop',
    late_seconds INT DEFAULT 0,
    early_leave_seconds INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'joined'
);

-- 6. 通话事实表
CREATE TABLE IF NOT EXISTS fact_calling (
    call_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    caller_user_id VARCHAR(36) NOT NULL,
    caller_department VARCHAR(100),
    callee_user_id VARCHAR(36),
    callee_department VARCHAR(100),
    call_type VARCHAR(20) DEFAULT 'internal',
    call_direction VARCHAR(20) DEFAULT 'outgoing',
    start_time TIMESTAMP NOT NULL,
    answer_time TIMESTAMP,
    end_time TIMESTAMP,
    ring_duration_seconds INT DEFAULT 0,
    talk_duration_seconds INT DEFAULT 0,
    total_duration_seconds INT DEFAULT 0,
    call_status VARCHAR(20) DEFAULT 'completed',
    has_video BOOLEAN DEFAULT FALSE,
    has_screen_share BOOLEAN DEFAULT FALSE,
    recording_enabled BOOLEAN DEFAULT FALSE,
    connection_quality VARCHAR(20) DEFAULT 'good',
    device_type VARCHAR(30) DEFAULT 'desktop',
    is_international BOOLEAN DEFAULT FALSE,
    transfer_count INT DEFAULT 0,
    hold_duration_seconds INT DEFAULT 0
);

-- 7. 工作空间事实表
CREATE TABLE IF NOT EXISTS fact_workspace (
    record_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    department VARCHAR(100),
    workspace_id VARCHAR(36),
    workspace_type VARCHAR(30) DEFAULT 'personal',
    record_date DATE NOT NULL,
    login_count INT DEFAULT 0,
    total_active_time_seconds INT DEFAULT 0,
    total_idle_time_seconds INT DEFAULT 0,
    total_session_time_seconds INT DEFAULT 0,
    file_created_count INT DEFAULT 0,
    file_edited_count INT DEFAULT 0,
    file_viewed_count INT DEFAULT 0,
    file_uploaded_count INT DEFAULT 0,
    file_downloaded_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    task_created_count INT DEFAULT 0,
    task_completed_count INT DEFAULT 0,
    storage_used_mb DECIMAL(15,2) DEFAULT 0,
    active_features TEXT
);

-- 8. 消息事实表
CREATE TABLE IF NOT EXISTS fact_messaging (
    message_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    sender_user_id VARCHAR(36) NOT NULL,
    sender_department VARCHAR(100),
    channel_id VARCHAR(36),
    channel_type VARCHAR(30) DEFAULT 'dm',
    sent_time TIMESTAMP NOT NULL,
    message_type VARCHAR(30) DEFAULT 'text',
    is_reply BOOLEAN DEFAULT FALSE,
    reply_to_message_id VARCHAR(36),
    reaction_count INT DEFAULT 0,
    is_edited BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    read_receipt_count INT DEFAULT 0,
    forward_count INT DEFAULT 0,
    thread_reply_count INT DEFAULT 0,
    emoji_mentions TEXT
);

-- 9. 设备使用事实表
CREATE TABLE IF NOT EXISTS fact_device_usage (
    record_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    department VARCHAR(100),
    record_date DATE NOT NULL,
    os_platform VARCHAR(30),
    device_type VARCHAR(30),
    app_version VARCHAR(30),
    session_count INT DEFAULT 0,
    total_active_time_seconds INT DEFAULT 0,
    feature_usage_count INT DEFAULT 0,
    network_type VARCHAR(20) DEFAULT 'wifi',
    is_primary_device BOOLEAN DEFAULT TRUE
);

-- 10. 服务质量事实表
CREATE TABLE IF NOT EXISTS fact_quality (
    record_id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36),
    department VARCHAR(100),
    record_date DATE NOT NULL,
    meeting_id VARCHAR(36),
    session_type VARCHAR(30) DEFAULT 'meeting',
    total_sessions INT DEFAULT 0,
    excellent_sessions INT DEFAULT 0,
    good_sessions INT DEFAULT 0,
    poor_sessions INT DEFAULT 0,
    avg_video_bitrate_kbps DECIMAL(10,2) DEFAULT 0,
    avg_audio_bitrate_kbps DECIMAL(10,2) DEFAULT 0,
    avg_packet_loss_rate DECIMAL(6,4) DEFAULT 0,
    avg_latency_ms DECIMAL(10,2) DEFAULT 0,
    avg_jitter_ms DECIMAL(10,2) DEFAULT 0,
    connection_failures INT DEFAULT 0,
    quality_score DECIMAL(5,2) DEFAULT 80
);

-- ==================== 索引 ====================
CREATE INDEX IF NOT EXISTS idx_meeting_tenant_date ON fact_meeting(org_id, start_time);
CREATE INDEX IF NOT EXISTS idx_meeting_host ON fact_meeting(host_user_id);
CREATE INDEX IF NOT EXISTS idx_calling_tenant_date ON fact_calling(org_id, start_time);
CREATE INDEX IF NOT EXISTS idx_workspace_tenant_date ON fact_workspace(org_id, record_date);
CREATE INDEX IF NOT EXISTS idx_workspace_user ON fact_workspace(user_id);
CREATE INDEX IF NOT EXISTS idx_messaging_tenant_date ON fact_messaging(org_id, sent_time);
CREATE INDEX IF NOT EXISTS idx_device_tenant_date ON fact_device_usage(org_id, record_date);
CREATE INDEX IF NOT EXISTS idx_quality_tenant_date ON fact_quality(org_id, record_date);
CREATE INDEX IF NOT EXISTS idx_user_tenant ON dim_user(org_id);

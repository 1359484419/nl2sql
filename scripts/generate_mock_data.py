"""
生成丰富模拟数据 — 企业协作 SaaS BI 系统
运行方式: python -m scripts.generate_mock_data
"""

import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from sqlalchemy import create_engine, text


# ─── 常量 ────────────────────────────────────────────────────────────────────

DEPARTMENTS = ["技术部", "产品部", "市场部", "销售部", "运营部", "财务部", "人事部", "客服部"]
PLATFORMS    = ["windows", "macOS", "iOS", "Android"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
MEETING_TYPES  = ["instant", "scheduled", "webinar", "recurring"]
MEETING_STATUS = ["ended", "cancelled"]
CONNECTION_QUALITY = ["excellent", "good", "poor"]
CALL_STATUS    = ["completed", "missed", "voicemail", "rejected", "busy"]
CALL_TYPES     = ["internal", "external"]
CALL_DIRECTIONS= ["outgoing", "incoming"]
CHANNEL_TYPES  = ["dm", "group", "channel"]
MESSAGE_TYPES  = ["text", "image", "file", "emoji"]

# 多租户配置
TENANTS = [
    {"org_id": "demo_org_001", "name": "示例科技有限公司",   "industry": "互联网",     "plan": "pro",        "seats": 200, "used": 87},
    {"org_id": "org_002",     "name": "华创数字科技",         "industry": "软件开发",   "plan": "enterprise","seats": 500, "used": 312},
    {"org_id": "org_003",     "name": "星辰企业服务",         "industry": "企业服务",   "plan": "starter",    "seats": 50,  "used": 28},
    {"org_id": "org_004",     "name": "云智互联科技",         "industry": "云计算",     "plan": "pro",        "seats": 150, "used": 103},
    {"org_id": "org_005",     "name": "未来数字传媒",         "industry": "媒体",       "plan": "starter",    "seats": 80,  "used": 41},
]


def get_engine():
    return create_engine(settings.db_url)


def _dept_of(user_id: str) -> str:
    """从 user_id 哈希出一个稳定的部门（保持 user 和 dept 关系）"""
    return DEPARTMENTS[hash(user_id) % len(DEPARTMENTS)]


def _today():
    return datetime.now()


# ─── 建表 + 清空（重新生成） ────────────────────────────────────────────────

def reset_tables(engine):
    sql_file = Path(__file__).parent / "init_db.sql"
    with engine.connect() as conn:
        with open(sql_file, "r", encoding="utf-8") as f:
            for statement in f.read().split(";"):
                st = statement.strip()
                if st:
                    try:
                        conn.execute(text(st))
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            print(f"  建表警告: {e}")
        conn.commit()
    print("✅ 建表完成")


def truncate_tables(engine):
    tables = [
        "fact_meeting_participant", "fact_meeting", "fact_calling",
        "fact_workspace", "fact_messaging", "fact_device_usage",
        "fact_quality", "dim_user", "dim_meeting_room", "dim_tenant",
    ]
    with engine.connect() as conn:
        for t in tables:
            try:
                conn.execute(text(f"TRUNCATE TABLE {t} CASCADE"))
            except Exception:
                pass
        conn.commit()
    print("✅ 数据表已清空")


# ─── 各表生成 ────────────────────────────────────────────────────────────────

def generate_tenants(engine):
    with engine.connect() as conn:
        for t in TENANTS:
            conn.execute(text("""
                INSERT INTO dim_tenant VALUES (:tid, :name, :ind, :plan, :seats, :used, 'active', NULL, NULL, NULL, NULL)
                ON CONFLICT (org_id) DO UPDATE SET
                    tenant_name=EXCLUDED.tenant_name,
                    industry=EXCLUDED.industry,
                    plan_type=EXCLUDED.plan_type,
                    seats_total=EXCLUDED.seats_total,
                    seats_used=EXCLUDED.seats_used
            """), {
                "tid": t["org_id"], "name": t["name"],
                "ind": t["industry"], "plan": t["plan"],
                "seats": t["seats"], "used": t["used"],
            })
        conn.commit()
    print(f"✅ 生成 {len(TENANTS)} 个租户")


def generate_users(engine, org_id: str, count: int, base_year: int = 2024):
    """
    为每个租户生成指定数量的用户，分布在近 2 年内注册。
    返回 {user_id: dept} 映射。
    """
    user_map = {}  # user_id -> dept
    today = _today()
    with engine.connect() as conn:
        for i in range(count):
            uid  = str(uuid.uuid4())
            dept = DEPARTMENTS[i % len(DEPARTMENTS)]
            user_map[uid] = dept
            registered  = today - timedelta(days=random.randint(30, 730),
                                            hours=random.randint(0, 23))
            last_active = today - timedelta(hours=random.randint(0, 168))
            is_sup      = i < count // 8
            conn.execute(text("""
                INSERT INTO dim_user VALUES (
                    :uid, :tid, :uname, :dname, :email, :phone, :dept, :title,
                    :role, :is_sup, :status, :device, :os,
                    :reg_at, :last_active, :first_login
                )
                ON CONFLICT (user_id) DO UPDATE SET last_active_at=EXCLUDED.last_active_at
            """), {
                "uid": uid, "tid": org_id,
                "uname": f"u_{org_id[-3:]}_{i+1:04d}",
                "dname": f"员工{org_id[-3:]}-{i+1}",
                "email": f"u{org_id[-3:]}{i+1}@{org_id}.com",
                "phone": f"1{random.randint(3,9)}{random.randint(100000000,999999999)}",
                "dept": dept,
                "title": random.choice(["工程师", "高级工程师", "经理", "总监", "主管", "专员", "助理"]),
                "role": "supervisor" if is_sup else "member",
                "is_sup": is_sup,
                "status": random.choices(["active", "inactive"], weights=[0.9, 0.1])[0],
                "device": random.choice(DEVICE_TYPES),
                "os": random.choice(PLATFORMS),
                "reg_at": registered,
                "last_active": last_active,
                "first_login": registered,
            })
        conn.commit()
    return user_map


def generate_meetings(engine, org_id: str, user_map: dict, count: int, days_back: int = 365):
    """
    会议分布在近 days_back 天内，时间段集中在 9:00-18:00。
    """
    today = _today()
    inserted = 0
    with engine.connect() as conn:
        for i in range(count):
            uid = random.choice(list(user_map.keys()))
            mid = str(uuid.uuid4())
            # 会议时间分布：近期密集，历史稀疏
            if random.random() < 0.7:
                days_ago = random.randint(0, 30)
            else:
                days_ago = random.randint(31, days_back)
            hour = random.choices(
                [h for h in range(24)],
                weights=[1]*9 + [5]*9 + [1]*6,
                k=1
            )[0] if True else random.randint(9, 18)
            start = today - timedelta(days=days_ago, hours=hour,
                                      minutes=random.randint(0, 59))
            duration     = random.randint(600, 10800)
            actual_dur   = int(duration * random.uniform(0.6, 1.0))
            end          = start + timedelta(seconds=actual_dur)
            participants = random.randint(2, 50)
            quality      = random.choices(CONNECTION_QUALITY, weights=[0.55, 0.35, 0.10])[0]
            mtype        = random.choices(MEETING_TYPES, weights=[0.3, 0.35, 0.15, 0.2])[0]

            conn.execute(text("""
                INSERT INTO fact_meeting VALUES (
                    :mid, :tid, NULL, :host, :dept, :mno, :mtype,
                    :start, :end, :dur, :actual_dur, :pc, :peak_pc,
                    :avg_pc, :msgs, :ss_count, 0, :is_rec, FALSE,
                    :quality, :video_cnt, :audio_cnt, 'ended', 'host_end'
                )
            """), {
                "mid": mid, "tid": org_id, "host": uid,
                "dept": user_map[uid],
                "mno": f"MEET-{org_id[-3:]}-{10000+i}",
                "mtype": mtype,
                "start": start, "end": end,
                "dur": duration, "actual_dur": actual_dur,
                "pc": participants,
                "peak_pc": int(participants * random.uniform(0.8, 1.2)),
                "avg_pc": round(participants * random.uniform(0.6, 0.9), 2),
                "msgs": random.randint(0, 80),
                "ss_count": random.randint(0, 8),
                "is_rec": random.random() < 0.35,
                "quality": quality,
                "video_cnt": random.randint(0, participants),
                "audio_cnt": random.randint(1, participants),
            })
            inserted += 1
        conn.commit()
    return inserted


def generate_meeting_participants(engine, org_id: str, user_map: dict,
                                   meeting_count: int, days_back: int = 365):
    """
    基于现有会议数，按比例生成参会者记录（每个会议 2~30 人）
    """
    today = _today()
    today_str = today.strftime("%Y-%m-%d")
    start_str = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")

    sql = f"""
        SELECT meeting_id, start_time, end_time, host_user_id
        FROM fact_meeting
        WHERE org_id = :tid
          AND start_time >= '{start_str}'::timestamp
          AND start_time < '{today_str}'::timestamp + interval '1 day'
        ORDER BY meeting_id
        LIMIT :limit
    """
    with engine.connect() as conn:
        meetings = list(conn.execute(text(sql), {"tid": org_id, "limit": meeting_count // 3}).fetchall())

    total = 0
    with engine.connect() as conn:
        for m in meetings:
            mid, m_start, m_end, host = m
            participants_count = random.randint(2, min(30, len(user_map)))
            participants = random.sample(list(user_map.keys()), participants_count)
            for p_uid in participants:
                join_offset  = random.randint(0, 300)   # 最多迟到 5 分钟
                leave_offset = random.randint(0, 300)   # 最多早退 5 分钟
                join  = m_start + timedelta(seconds=join_offset)
                leave = m_end   - timedelta(seconds=leave_offset)
                dur_s = max(0, int((leave - join).total_seconds()))

                conn.execute(text("""
                    INSERT INTO fact_meeting_participant VALUES (
                        :rid, :mid, :tid, :uid, :dept, :join, :leave,
                        :dur, :is_host, FALSE, FALSE,
                        :video, :audio, :ss, :msgs, :reactions,
                        :hand, 'good', 'desktop', :late, :early_leave, 'joined'
                    )
                """), {
                    "rid": str(uuid.uuid4()), "mid": mid, "tid": org_id,
                    "uid": p_uid, "dept": user_map[p_uid],
                    "join": join, "leave": leave,
                    "dur": dur_s,
                    "is_host": (p_uid == host),
                    "video": random.random() < 0.7,
                    "audio": random.random() < 0.9,
                    "ss": random.random() < 0.2,
                    "msgs": random.randint(0, 20),
                    "reactions": random.randint(0, 15),
                    "hand": random.random() < 0.1,
                    "late": join_offset,
                    "early_leave": leave_offset,
                })
                total += 1
        conn.commit()
    return total


def generate_calling(engine, org_id: str, user_map: dict, count: int, days_back: int = 365):
    today = _today()
    with engine.connect() as conn:
        for i in range(count):
            cid     = str(uuid.uuid4())
            caller  = random.choice(list(user_map.keys()))
            callee  = random.choice(list(user_map.keys()))
            ctype   = random.choice(CALL_TYPES)
            direct  = random.choice(CALL_DIRECTIONS)
            if random.random() < 0.65:
                status = "completed"
                talk_dur = random.randint(30, 7200)
                ring_dur = random.randint(5, 45)
            else:
                status = random.choices(["missed", "voicemail", "rejected", "busy"], weights=[0.4, 0.2, 0.2, 0.2])[0]
                talk_dur = 0
                ring_dur = random.randint(5, 120)
            days_ago = random.choices(
                list(range(0, 31)) + list(range(31, days_back)),
                weights=[5]*31 + [1]*(days_back-31), k=1
            )[0]
            start = today - timedelta(days=days_ago, hours=random.randint(8, 21),
                                      minutes=random.randint(0, 59))
            end   = start + timedelta(seconds=ring_dur + talk_dur)
            quality = random.choices(CONNECTION_QUALITY, weights=[0.5, 0.4, 0.1])[0]

            conn.execute(text("""
                INSERT INTO fact_calling VALUES (
                    :cid, :tid, :caller, :c_dept, :callee, :ca_dept,
                    :ctype, :dir, :start, :answer, :end,
                    :ring, :talk, :total, :status, FALSE, FALSE, FALSE,
                    :quality, 'desktop', FALSE, 0, 0
                )
            """), {
                "cid": cid, "tid": org_id,
                "caller": caller, "c_dept": user_map[caller],
                "callee": callee, "ca_dept": user_map[callee],
                "ctype": ctype, "dir": direct,
                "start": start,
                "answer": start + timedelta(seconds=ring_dur) if status == "completed" else None,
                "end": end,
                "ring": ring_dur, "talk": talk_dur,
                "total": ring_dur + talk_dur,
                "status": status,
                "quality": quality,
            })
        conn.commit()
    return count


def generate_workspace(engine, org_id: str, user_map: dict,
                       records_per_user: int = 60, days_back: int = 365):
    """
    每个用户每天一条记录，records_per_user=60 覆盖近 60 天。
    """
    today = _today()
    total = 0
    with engine.connect() as conn:
        for uid, dept in user_map.items():
            # 每个用户在 days_back 天内随机选取 records_per_user 天有记录
            active_days = random.sample(range(days_back), min(records_per_user, days_back))
            for d in active_days:
                rid          = str(uuid.uuid4())
                record_date  = (today - timedelta(days=d)).date()
                active_time  = random.randint(1800, 28800)
                idle_time    = random.randint(0, 7200)
                session_time = active_time + random.randint(0, 3600)
                conn.execute(text("""
                    INSERT INTO fact_workspace VALUES (
                        :rid, :tid, :uid, :dept, NULL, 'personal',
                        :date, :logins, :active, :idle, :session,
                        :created, :edited, :viewed, :uploaded, :downloaded,
                        :comments, :task_c, :task_done, :storage, NULL
                    )
                """), {
                    "rid": rid, "tid": org_id, "uid": uid, "dept": dept,
                    "date": record_date,
                    "logins": random.randint(1, 6),
                    "active": active_time,
                    "idle": idle_time,
                    "session": session_time,
                    "created": random.randint(0, 12),
                    "edited": random.randint(0, 25),
                    "viewed": random.randint(5, 60),
                    "uploaded": random.randint(0, 8),
                    "downloaded": random.randint(0, 15),
                    "comments": random.randint(0, 20),
                    "task_c": random.randint(0, 6),
                    "task_done": random.randint(0, 6),
                    "storage": round(random.uniform(50, 8000), 2),
                })
                total += 1
        conn.commit()
    return total


def generate_messaging(engine, org_id: str, user_map: dict, count: int, days_back: int = 365):
    today = _today()
    total = 0
    with engine.connect() as conn:
        for i in range(count):
            mid   = str(uuid.uuid4())
            sender= random.choice(list(user_map.keys()))
            days_ago = random.choices(
                list(range(0, 31)) + list(range(31, days_back)),
                weights=[5]*31 + [1]*(days_back-31), k=1
            )[0]
            sent  = today - timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )
            conn.execute(text("""
                INSERT INTO fact_messaging VALUES (
                    :mid, :tid, :sender, :dept, NULL, :ctype,
                    :sent, :mtype, FALSE, NULL, :reactions,
                    FALSE, FALSE, :read_receipt, 0, 0, NULL
                )
            """), {
                "mid": mid, "tid": org_id, "sender": sender,
                "dept": user_map[sender],
                "ctype": random.choices(CHANNEL_TYPES, weights=[0.4, 0.35, 0.25])[0],
                "sent": sent,
                "mtype": random.choices(MESSAGE_TYPES, weights=[0.7, 0.1, 0.1, 0.1])[0],
                "reactions": random.randint(0, 20),
                "read_receipt": random.randint(0, 10),
            })
            total += 1
        conn.commit()
    return total


def generate_device_usage(engine, org_id: str, user_map: dict,
                           count: int, days_back: int = 180):
    """
    设备使用情况 — 每用户每天一条，count 控制总量
    """
    today = _today()
    total = 0
    batch = []
    all_users = list(user_map.keys())
    for i in range(count):
        uid   = random.choice(all_users)
        date  = (today - timedelta(days=random.randint(0, days_back))).date()
        device = random.choice(DEVICE_TYPES)
        session_count = random.randint(1, 8)
        active_secs   = random.randint(600, 28800)
        batch.append({
            "rid": str(uuid.uuid4()), "tid": org_id, "uid": uid,
            "dept": user_map[uid], "date": date,
            "device": device, "sessions": session_count,
            "active": active_secs, "idle": random.randint(0, 3600),
        })
        if len(batch) >= 500:
            with engine.connect() as conn:
                for r in batch:
                    conn.execute(text("""
                        INSERT INTO fact_device_usage VALUES (
                            :rid, :tid, :uid, :dept, :date,
                            :device, :sessions, :active, :idle
                        )
                    """), r)
                conn.commit()
            total += len(batch)
            batch = []
    if batch:
        with engine.connect() as conn:
            for r in batch:
                conn.execute(text("""
                    INSERT INTO fact_device_usage VALUES (
                        :rid, :tid, :uid, :dept, :date,
                        :device, :sessions, :active, :idle
                    )
                """), r)
            conn.commit()
        total += len(batch)
    return total


def generate_quality(engine, org_id: str, user_map: dict, count: int, days_back: int = 365):
    today = _today()
    total = 0
    with engine.connect() as conn:
        for i in range(count):
            rid   = str(uuid.uuid4())
            uid   = random.choice(list(user_map.keys()))
            date  = (today - timedelta(days=random.randint(0, days_back))).date()
            total_sessions = random.randint(20, 500)
            excellent = int(total_sessions * random.uniform(0.45, 0.80))
            good      = int((total_sessions - excellent) * random.uniform(0.50, 0.90))
            poor      = max(0, total_sessions - excellent - good)
            score     = round((excellent * 100 + good * 75 + max(poor, 0) * 40) / total_sessions, 2)

            conn.execute(text("""
                INSERT INTO fact_quality VALUES (
                    :rid, :tid, :uid, :dept, :date, NULL, 'meeting',
                    :total, :excellent, :good, :poor,
                    1500, 64, 0.001, 45, 5, 0, :score
                )
            """), {
                "rid": rid, "tid": org_id, "uid": uid,
                "dept": user_map[uid],
                "date": date,
                "total": total_sessions,
                "excellent": excellent, "good": good, "poor": poor,
                "score": score,
            })
            total += 1
        conn.commit()
    return total


# ─── 主流程 ─────────────────────────────────────────────────────────────────

def main():
    print("🚀 开始生成丰富的模拟数据...\n")
    engine = get_engine()

    reset_tables(engine)
    truncate_tables(engine)

    # 总览
    total_users       = 0
    total_meetings    = 0
    total_participants= 0
    total_calls       = 0
    total_workspace  = 0
    total_messages   = 0
    total_device     = 0
    total_quality    = 0

    generate_tenants(engine)
    print()

    for t in TENANTS:
        org   = t["org_id"]
        # 根据租户规模分配用户数
        user_count = t["used"]
        users = generate_users(engine, org, count=user_count)
        total_users += len(users)
        print(f"  ✅ {org} ({t['name']}): {len(users)} 用户")

        # 会议：按用户数比例，分布 365 天
        meet_cnt = max(200, user_count * 8)
        m = generate_meetings(engine, org, users, count=meet_cnt, days_back=365)
        total_meetings += m

        # 参会者记录
        p = generate_meeting_participants(engine, org, users, meeting_count=m, days_back=365)
        total_participants += p

        # 通话
        c = generate_calling(engine, org, users, count=max(300, user_count * 10), days_back=365)
        total_calls += c

        # 工作空间：每用户每天一条，覆盖近 90 天
        w = generate_workspace(engine, org, users, records_per_user=90, days_back=365)
        total_workspace += w

        # 消息
        msg = generate_messaging(engine, org, users, count=max(500, user_count * 30), days_back=365)
        total_messages += msg

        # 设备使用
        d = generate_device_usage(engine, org, users, count=max(200, user_count * 15), days_back=180)
        total_device += d

        # 质量记录
        q = generate_quality(engine, org, users, count=max(50, user_count * 3), days_back=365)
        total_quality += q

        print(f"     会议 {m} 条 | 参会记录 {p} | 通话 {c} | "
              f"工作空间 {w} 条 | 消息 {msg} | 设备 {d} | 质量 {q}")
        print()

    print("=" * 60)
    print("📊 数据生成汇总")
    print(f"   租户数:      {len(TENANTS)}")
    print(f"   用户数:      {total_users}")
    print(f"   会议记录:    {total_meetings}")
    print(f"   参会记录:    {total_participants}")
    print(f"   通话记录:    {total_calls}")
    print(f"   工作空间:    {total_workspace} 条")
    print(f"   消息记录:   {total_messages}")
    print(f"   设备记录:    {total_device}")
    print(f"   质量记录:    {total_quality}")
    print("=" * 60)
    print(f"\n🎉 数据生成完毕！数据库: {settings.effective_db_url}")


if __name__ == "__main__":
    main()

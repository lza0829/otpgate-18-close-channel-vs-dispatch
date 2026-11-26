from __future__ import annotations
from datetime import datetime

from app.db import db, init_db
from app.services.common import audit, now_str


def seed_if_empty() -> None:
    init_db()
    with db() as conn:
        n = conn.execute("SELECT COUNT(*) AS c FROM channels").fetchone()["c"]
        if n:
            return
        now = now_str()
        conn.execute(
            """
            INSERT INTO channels(code, name, role, weight, status, concurrency_limit, fail_threshold)
            VALUES
              ('阿里云短信', '阿里云主通道', '主路', 80, '启用', 30, 3),
              ('腾讯云短信', '腾讯云备通道', '备路', 20, '启用', 20, 3)
            """
        )
        conn.execute(
            "INSERT INTO route_policy(id, mode, updated_at) VALUES (1, '权重', ?)",
            (now,),
        )
        conn.execute(
            """
            INSERT INTO settings(key, value) VALUES
              ('允许双挂硬投', '否'),
              ('熔断后自动探测', '是'),
              ('回执晚到可改写', '是')
            """
        )
        main = conn.execute("SELECT id FROM channels WHERE role='主路'").fetchone()["id"]
        serial = f"验{datetime.now().strftime('%Y%m%d')}0001"
        conn.execute(
            """
            INSERT INTO sends(serial, phone_mask, scene, status, channel_id, note, created_at)
            VALUES (?, '138****8001', '登录', '待投递', ?, '种子可投递单', ?)
            """,
            (serial, main, now),
        )
        audit(conn, "系统", None, "种子初始化", "验码渠")

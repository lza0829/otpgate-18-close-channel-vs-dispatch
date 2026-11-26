from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import db, rows_to_list
from app.services.common import audit, now_str

router = APIRouter(tags=["投递"])


class SendCreate(BaseModel):
    手机掩码: str = Field(min_length=3)
    场景: str = "登录"
    备注: str = ""


def pick_channel(conn):
    policy = conn.execute("SELECT mode FROM route_policy WHERE id=1").fetchone()["mode"]
    if policy == "强制主路":
        row = conn.execute(
            "SELECT * FROM channels WHERE role='主路' AND status='启用' LIMIT 1"
        ).fetchone()
    elif policy == "强制备路":
        row = conn.execute(
            "SELECT * FROM channels WHERE role='备路' AND status='启用' LIMIT 1"
        ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT * FROM channels WHERE status='启用'
            ORDER BY weight DESC, id ASC LIMIT 1
            """
        ).fetchone()
    return row


@router.get("/投递单")
def list_sends():
    with db() as conn:
        rows = rows_to_list(
            conn.execute(
                """
                SELECT s.*, c.name AS channel_name, f.name AS failover_name
                FROM sends s
                LEFT JOIN channels c ON c.id = s.channel_id
                LEFT JOIN channels f ON f.id = s.failover_channel_id
                ORDER BY s.id DESC
                """
            ).fetchall()
        )
    return [
        {
            "编号": r["id"],
            "投递单号": r["serial"],
            "手机掩码": r["phone_mask"],
            "场景": r["scene"],
            "状态": r["status"],
            "通道": r["channel_name"] or "-",
            "切备通道": r["failover_name"] or "-",
            "创建时间": r["created_at"],
            "备注": r["note"],
        }
        for r in rows
    ]


@router.post("/投递单")
def create_send(body: SendCreate):
    with db() as conn:
        ch = pick_channel(conn)
        if not ch:
            raise HTTPException(400, "无可用通道")
        serial = f"验{datetime.now().strftime('%Y%m%d%H%M%S')}"
        now = now_str()
        cur = conn.execute(
            """
            INSERT INTO sends(serial, phone_mask, scene, status, channel_id, note, created_at)
            VALUES (?, ?, ?, '待投递', ?, ?, ?)
            """,
            (serial, body.手机掩码, body.场景, ch["id"], body.备注, now),
        )
        sid = cur.lastrowid
        audit(conn, "投递单", sid, "创建", serial)
    return {"编号": sid, "投递单号": serial, "通道": ch["name"]}


@router.post("/投递单/{sid}/投递")
def dispatch_send(sid: int):
    with db() as conn:
        s = conn.execute("SELECT * FROM sends WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "投递单不存在")
        if s["status"] not in ("待投递", "已切备"):
            raise HTTPException(400, f"当前状态不可投递：{s['status']}")
        ch_id = s["failover_channel_id"] or s["channel_id"]
        ch = conn.execute("SELECT * FROM channels WHERE id=?", (ch_id,)).fetchone()
        if not ch or ch["status"] != "启用":
            raise HTTPException(400, "目标通道不可用")
        inflight = conn.execute(
            "SELECT COUNT(*) c FROM sends WHERE channel_id=? AND status='投递中'",
            (ch_id,),
        ).fetchone()["c"]
        if inflight >= ch["concurrency_limit"]:
            raise HTTPException(400, "通道并发已满")
        conn.execute(
            "UPDATE sends SET status='投递中', channel_id=?, sent_at=? WHERE id=?",
            (ch_id, now_str(), sid),
        )
        audit(conn, "投递单", sid, "投递", ch["name"])
    return {"结果": "投递中", "通道": ch["name"]}

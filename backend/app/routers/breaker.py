from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import db, rows_to_list
from app.services.common import audit, get_setting, now_str

router = APIRouter(tags=["熔断"])


class FailBody(BaseModel):
    备注: str = "模拟投递失败"


@router.get("/熔断事件")
def list_breaks():
    with db() as conn:
        rows = rows_to_list(
            conn.execute(
                """
                SELECT b.*, c.name AS channel_name
                FROM break_events b JOIN channels c ON c.id = b.channel_id
                ORDER BY b.id DESC LIMIT 100
                """
            ).fetchall()
        )
    return [
        {
            "编号": r["id"],
            "通道": r["channel_name"],
            "动作": r["action"],
            "投递单": r["send_id"],
            "时间": r["created_at"],
            "备注": r["note"],
        }
        for r in rows
    ]


@router.post("/投递单/{sid}/失败")
def mark_fail(sid: int, body: FailBody):
    with db() as conn:
        s = conn.execute("SELECT * FROM sends WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "投递单不存在")
        if s["status"] != "投递中":
            raise HTTPException(400, "仅投递中可记失败")
        ch = conn.execute("SELECT * FROM channels WHERE id=?", (s["channel_id"],)).fetchone()
        fails = ch["consecutive_fails"] + 1
        conn.execute("UPDATE channels SET consecutive_fails=? WHERE id=?", (fails, ch["id"]))
        tripped = fails >= ch["fail_threshold"]
        if tripped:
            conn.execute("UPDATE channels SET status='熔断中' WHERE id=?", (ch["id"],))
            conn.execute(
                "INSERT INTO break_events(channel_id, action, send_id, created_at, note) VALUES (?, '熔断', ?, ?, ?)",
                (ch["id"], sid, now_str(), body.备注),
            )
            backup = conn.execute(
                "SELECT * FROM channels WHERE role='备路' AND status='启用' AND id<>? LIMIT 1",
                (ch["id"],),
            ).fetchone()
            if not backup:
                backup = conn.execute(
                    "SELECT * FROM channels WHERE status='启用' AND id<>? ORDER BY weight DESC LIMIT 1",
                    (ch["id"],),
                ).fetchone()
            if backup:
                conn.execute(
                    """
                    UPDATE sends SET status='已切备', failover_channel_id=?, finished_at=? WHERE id=?
                    """,
                    (backup["id"], now_str(), sid),
                )
                conn.execute(
                    "INSERT INTO break_events(channel_id, action, send_id, created_at, note) VALUES (?, '切备', ?, ?, ?)",
                    (backup["id"], sid, now_str(), f"自 {ch['name']} 切至 {backup['name']}"),
                )
                audit(conn, "熔断", sid, "切备", backup["name"])
                return {"结果": "已切备", "备通道": backup["name"], "原通道熔断": True}
            allow = get_setting(conn, "允许双挂硬投", "否")
            if allow != "是":
                conn.execute(
                    "UPDATE sends SET status='已失败', finished_at=? WHERE id=?",
                    (now_str(), sid),
                )
                audit(conn, "熔断", sid, "双挂失败", body.备注)
                return {"结果": "已失败", "原因": "无可用备通道"}
        conn.execute(
            "UPDATE sends SET status='已失败', finished_at=? WHERE id=?",
            (now_str(), sid),
        )
        audit(conn, "熔断", sid, "失败", body.备注)
    return {"结果": "已失败", "连续失败": fails, "已熔断": tripped}


@router.post("/通道/{cid}/恢复")
def recover(cid: int):
    with db() as conn:
        row = conn.execute("SELECT * FROM channels WHERE id=?", (cid,)).fetchone()
        if not row:
            raise HTTPException(404, "通道不存在")
        conn.execute(
            "UPDATE channels SET status='启用', consecutive_fails=0 WHERE id=?",
            (cid,),
        )
        conn.execute(
            "INSERT INTO break_events(channel_id, action, send_id, created_at, note) VALUES (?, '恢复', NULL, ?, '人工恢复')",
            (cid, now_str()),
        )
        audit(conn, "通道", cid, "恢复", row["name"])
    return {"结果": "已恢复"}

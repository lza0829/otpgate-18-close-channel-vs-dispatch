from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import db, rows_to_list
from app.services.common import audit, get_setting, now_str

router = APIRouter(tags=["回执"])


class ReceiptBody(BaseModel):
    结果: str
    厂商码: str = ""


@router.get("/回执")
def list_receipts():
    with db() as conn:
        rows = rows_to_list(
            conn.execute(
                """
                SELECT r.*, s.serial, c.name AS channel_name
                FROM receipts r
                JOIN sends s ON s.id = r.send_id
                JOIN channels c ON c.id = r.channel_id
                ORDER BY r.id DESC LIMIT 100
                """
            ).fetchall()
        )
    return [
        {
            "编号": r["id"],
            "投递单号": r["serial"],
            "通道": r["channel_name"],
            "结果": r["result"],
            "厂商码": r["vendor_code"],
            "时间": r["created_at"],
        }
        for r in rows
    ]


@router.post("/投递单/{sid}/回执")
def add_receipt(sid: int, body: ReceiptBody):
    if body.结果 not in ("成功", "失败"):
        raise HTTPException(400, "结果非法")
    with db() as conn:
        s = conn.execute("SELECT * FROM sends WHERE id=?", (sid,)).fetchone()
        if not s:
            raise HTTPException(404, "投递单不存在")
        ch_id = s["failover_channel_id"] or s["channel_id"]
        if not ch_id:
            raise HTTPException(400, "无通道")
        conn.execute(
            """
            INSERT INTO receipts(send_id, channel_id, result, vendor_code, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (sid, ch_id, body.结果, body.厂商码, now_str()),
        )
        allow_late = get_setting(conn, "回执晚到可改写", "是")
        if s["status"] in ("投递中", "已切备") or (allow_late == "是" and s["status"] in ("已失败", "已送达")):
            new_status = "已送达" if body.结果 == "成功" else "已失败"
            conn.execute(
                "UPDATE sends SET status=?, finished_at=? WHERE id=?",
                (new_status, now_str(), sid),
            )
            if body.结果 == "成功":
                conn.execute(
                    "UPDATE channels SET consecutive_fails=0 WHERE id=?",
                    (ch_id,),
                )
        audit(conn, "回执", sid, body.结果, body.厂商码)
    return {"结果": "回执已记"}

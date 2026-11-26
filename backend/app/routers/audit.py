from __future__ import annotations
from fastapi import APIRouter
from app.db import db, rows_to_list

router = APIRouter(tags=["审计"])


@router.get("/审计")
def list_audit():
    with db() as conn:
        rows = rows_to_list(
            conn.execute(
                "SELECT * FROM audit_events ORDER BY id DESC LIMIT 200"
            ).fetchall()
        )
    return [
        {
            "编号": r["id"],
            "类别": r["kind"],
            "关联": r["ref_id"],
            "动作": r["action"],
            "时间": r["created_at"],
            "备注": r["note"],
        }
        for r in rows
    ]

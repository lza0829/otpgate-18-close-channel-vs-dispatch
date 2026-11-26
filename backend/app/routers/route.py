from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import db
from app.services.common import audit, now_str

router = APIRouter(tags=["选路"])


class PolicyBody(BaseModel):
    模式: str


@router.get("/选路")
def get_policy():
    with db() as conn:
        row = conn.execute("SELECT * FROM route_policy WHERE id=1").fetchone()
    return {"模式": row["mode"], "更新时间": row["updated_at"]}


@router.put("/选路")
def put_policy(body: PolicyBody):
    if body.模式 not in ("权重", "强制主路", "强制备路"):
        raise HTTPException(400, "模式非法")
    with db() as conn:
        conn.execute(
            "UPDATE route_policy SET mode=?, updated_at=? WHERE id=1",
            (body.模式, now_str()),
        )
        audit(conn, "选路", 1, "改策略", body.模式)
    return {"结果": "已更新", "模式": body.模式}

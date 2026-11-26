from __future__ import annotations
from fastapi import APIRouter
from app.db import db, rows_to_list

router = APIRouter(tags=["总览"])


@router.get("/总览")
def overview():
    with db() as conn:
        dist = {
            "待投递": conn.execute("SELECT COUNT(*) c FROM sends WHERE status='待投递'").fetchone()["c"],
            "投递中": conn.execute("SELECT COUNT(*) c FROM sends WHERE status='投递中'").fetchone()["c"],
            "已送达": conn.execute("SELECT COUNT(*) c FROM sends WHERE status='已送达'").fetchone()["c"],
            "已失败": conn.execute("SELECT COUNT(*) c FROM sends WHERE status='已失败'").fetchone()["c"],
            "已切备": conn.execute("SELECT COUNT(*) c FROM sends WHERE status='已切备'").fetchone()["c"],
            "熔断通道": conn.execute("SELECT COUNT(*) c FROM channels WHERE status='熔断中'").fetchone()["c"],
        }
        inflight = rows_to_list(
            conn.execute(
                """
                SELECT s.id AS 编号, s.serial AS 投递单号, s.phone_mask AS 手机掩码, s.scene AS 场景,
                       s.status AS 状态, c.name AS 当前通道
                FROM sends s LEFT JOIN channels c ON c.id = s.channel_id
                WHERE s.status IN ('待投递','投递中','已切备')
                ORDER BY s.id DESC
                """
            ).fetchall()
        )
        chans = rows_to_list(
            conn.execute(
                """
                SELECT code AS 代号, name AS 名称, role AS 角色, status AS 状态,
                       weight AS 权重, consecutive_fails AS 连续失败
                FROM channels ORDER BY role, id
                """
            ).fetchall()
        )
    return {"分布": dist, "在途": inflight, "通道": chans}

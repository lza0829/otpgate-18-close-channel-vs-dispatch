from __future__ import annotations
from fastapi import APIRouter
from app.db import db

router = APIRouter(tags=["对账"])


@router.get("/对账")
def reconcile():
    with db() as conn:
        sends = conn.execute("SELECT COUNT(*) c FROM sends").fetchone()["c"]
        ok = conn.execute("SELECT COUNT(*) c FROM sends WHERE status='已送达'").fetchone()["c"]
        fail = conn.execute("SELECT COUNT(*) c FROM sends WHERE status='已失败'").fetchone()["c"]
        fo = conn.execute("SELECT COUNT(*) c FROM sends WHERE status='已切备'").fetchone()["c"]
        receipts = conn.execute("SELECT COUNT(*) c FROM receipts").fetchone()["c"]
        receipt_ok = conn.execute("SELECT COUNT(*) c FROM receipts WHERE result='成功'").fetchone()["c"]
        breaks = conn.execute("SELECT COUNT(*) c FROM break_events WHERE action='切备'").fetchone()["c"]
    return {
        "投递申请数": sends,
        "已送达": ok,
        "已失败": fail,
        "已切备在途": fo,
        "回执条数": receipts,
        "回执成功": receipt_ok,
        "切备次数": breaks,
        "送达与回执差": ok - receipt_ok,
    }

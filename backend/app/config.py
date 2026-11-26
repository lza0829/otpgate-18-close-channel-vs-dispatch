from __future__ import annotations
import os
from pathlib import Path

PROJECT_NAME = "验码渠"
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.environ.get("OTPGATE_DB", str(ROOT / "data" / "otpgate.db")))

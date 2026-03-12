"""
Copies the most recent spotify and soundcloud CSVs into frontend/public/data/
so the React app can serve them statically.

Run this after each pipeline execution:
    python scripts/export_for_web.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "frontend" / "public" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sources = {
    "spotify": ROOT / "data" / "spotify",
    "soundcloud": ROOT / "data" / "soundcloud",
}

for name, data_dir in sources.items():
    csvs = list(data_dir.glob("*.csv"))
    if not csvs:
        print(f"No CSVs found in {data_dir}")
        continue
    latest = max(csvs, key=lambda p: p.stat().st_mtime)
    dest = OUT_DIR / f"{name}.csv"
    shutil.copy(latest, dest)
    print(f"Copied {latest.name} -> {dest}")

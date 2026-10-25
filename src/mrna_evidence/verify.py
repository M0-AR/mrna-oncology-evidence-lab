from __future__ import annotations

import json

import pandas as pd

from .manifest import verify_all
from .paths import MANIFESTS, PAPER, TABLES


def verify() -> dict:
    checks = []
    manifests = verify_all()
    checks.append({"name": "manifests", "ok": all(item.get("ok") for item in manifests.values()), "detail": manifests})

    summary = json.loads((PAPER / "results_summary.json").read_text(encoding="utf-8"))
    checks.append({"name": "event_1_return", "ok": abs(next(row for row in summary["event_volume"] if row["event_id"] == "event_1")["volume_multiple"] - 33.4979) < 1e-3})
    checks.append({"name": "event_2_return", "ok": abs(next(row for row in summary["event_volume"] if row["event_id"] == "event_2")["volume_multiple"] - 3.2886) < 1e-3})
    checks.append({"name": "nnt_rfs", "ok": abs(summary["derived_clinical"]["nnt_2y_rfs"] - 8.19672131147541) < 1e-9})
    checks.append({"name": "claim_count", "ok": summary["claim_count"] == 42})
    checks.append({"name": "source_count", "ok": summary["source_count"] == 29})

    event_table = pd.read_csv(TABLES / "event_study.csv")
    checks.append({"name": "event_table_rows", "ok": len(event_table) > 20})
    claims = pd.read_csv(TABLES / "claims.csv")
    checks.append({"name": "claim_table_rows", "ok": len(claims) == 42})
    return {"ok": all(item["ok"] for item in checks), "checks": checks}

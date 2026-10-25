from __future__ import annotations

from collections import Counter

import pandas as pd

from .config import load_config
from .paths import ROOT


def load_claims(config: dict | None = None) -> dict:
    return config or load_config("claims.yaml")


def validate_claims(config: dict) -> list[str]:
    errors = []
    allowed = set(config["allowed_verdicts"])
    source_ids = {source["id"] for source in load_config("sources.yaml")["sources"]}
    seen = set()
    for claim in config["claims"]:
        claim_id = claim["id"]
        if claim_id in seen:
            errors.append(f"duplicate claim id: {claim_id}")
        seen.add(claim_id)
        if claim["verdict"] not in allowed:
            errors.append(f"{claim_id}: invalid verdict {claim['verdict']}")
        if not claim.get("sources"):
            errors.append(f"{claim_id}: no sources")
        for source_id in claim.get("sources", []):
            if source_id not in source_ids:
                errors.append(f"{claim_id}: unknown source {source_id}")
        if not claim.get("evidence"):
            errors.append(f"{claim_id}: no evidence")
    return errors


def claim_table(config: dict | None = None) -> pd.DataFrame:
    config = load_claims(config)
    errors = validate_claims(config)
    if errors:
        raise ValueError("; ".join(errors))
    rows = []
    for claim in config["claims"]:
        row = dict(claim)
        row["sources_joined"] = ";".join(claim["sources"])
        rows.append(row)
    return pd.DataFrame(rows)


def claim_counts(config: dict | None = None) -> pd.DataFrame:
    frame = claim_table(config)
    counts = frame.groupby(["category", "verdict"]).size().reset_index(name="count")
    return counts.sort_values(["category", "verdict"]).reset_index(drop=True)


def verdict_totals(config: dict | None = None) -> dict[str, int]:
    frame = claim_table(config)
    counts = Counter(frame["verdict"])
    return {verdict: int(counts.get(verdict, 0)) for verdict in load_claims(config)["allowed_verdicts"]}


def source_table(config: dict | None = None) -> pd.DataFrame:
    sources = (config or load_config("sources.yaml"))["sources"]
    rows = []
    for source in sources:
        snapshot = source.get("snapshot")
        rows.append(
            {
                "source_id": source["id"],
                "title": source["title"],
                "publisher": source["publisher"],
                "published_at": source["published_at"],
                "type": source["type"],
                "tier": source["tier"],
                "url": source["url"],
                "snapshot": snapshot or "",
                "snapshot_exists": bool(snapshot) and (ROOT / snapshot).exists(),
                "notes": source.get("notes", ""),
            }
        )
    return pd.DataFrame(rows)

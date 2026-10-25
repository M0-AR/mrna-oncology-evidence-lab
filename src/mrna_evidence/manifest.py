from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .paths import MANIFESTS, PRICES, ROOT


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe(path: Path, source: dict | None = None) -> dict:
    record = {
        "path": str(path.relative_to(ROOT)),
        "bytes": int(path.stat().st_size),
        "sha256": sha256(path),
        "retrieved_at": "2026-10-24",
    }
    if source is not None:
        record.update(
            {
                "source_id": source["id"],
                "title": source["title"],
                "publisher": source["publisher"],
                "url": source["url"],
                "tier": source["tier"],
            }
        )
    return record


def build_manifest(sources: list[dict], output: Path | None = None) -> dict:
    output = output or MANIFESTS / "snapshots.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    missing = []
    for source in sources:
        snapshot = source.get("snapshot")
        if not snapshot:
            continue
        path = ROOT / snapshot
        if not path.exists():
            missing.append(snapshot)
            continue
        records.append(describe(path, source))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "sha256",
        "root": ".",
        "count": len(records),
        "missing": missing,
        "files": records,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def build_price_manifest(output: Path | None = None) -> dict:
    output = output or MANIFESTS / "prices.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(PRICES.glob("*.json"))
    records = [describe(path) for path in files]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "sha256",
        "count": len(records),
        "files": records,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def verify_manifest(path: str | Path) -> dict:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    failures = []
    for record in manifest["files"]:
        file_path = ROOT / record["path"]
        if not file_path.exists():
            failures.append({"path": record["path"], "reason": "missing"})
            continue
        actual = sha256(file_path)
        if actual != record["sha256"]:
            failures.append(
                {
                    "path": record["path"],
                    "reason": "hash_mismatch",
                    "expected": record["sha256"],
                    "actual": actual,
                }
            )
    return {
        "checked": len(manifest["files"]),
        "failures": failures,
        "ok": len(failures) == 0,
    }


def verify_all() -> dict:
    results = {}
    for name in ("snapshots.json", "prices.json"):
        path = MANIFESTS / name
        results[name] = verify_manifest(path) if path.exists() else {"ok": False, "reason": "manifest_missing"}
    return results


def hash_files(paths: Iterable[str | Path]) -> dict[str, str]:
    return {str(path): sha256(path) for path in paths}

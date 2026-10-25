from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
RAW = DATA / "raw"
PRICES = RAW / "prices"
PROCESSED = DATA / "processed"
EVIDENCE = ROOT / "evidence"
SNAPSHOTS = EVIDENCE / "snapshots"
MANIFESTS = EVIDENCE / "manifests"
RESULTS = ROOT / "results"
TABLES = RESULTS / "tables"
FIGURES = RESULTS / "figures"
PAPER = ROOT / "paper"
PAPER_FIGURES = PAPER / "figures"


def ensure_directories() -> None:
    for path in (PROCESSED, MANIFESTS, TABLES, FIGURES, PAPER_FIGURES):
        path.mkdir(parents=True, exist_ok=True)

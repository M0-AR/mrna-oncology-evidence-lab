from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import PRICES


def _clean_number(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("$", "").replace(",", "").strip()
    if text in {"", "N/A", "NA", "nan", "None"}:
        return float("nan")
    return float(text)


def load_yahoo(path: str | Path) -> pd.DataFrame:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    result = payload["chart"]["result"][0]
    timestamps = pd.to_datetime(result["timestamp"], unit="s", utc=True)
    timestamps = timestamps.tz_convert("America/New_York").normalize().tz_localize(None)
    quote = result["indicators"]["quote"][0]
    frame = pd.DataFrame(
        {
            "date": timestamps,
            "open": quote.get("open"),
            "high": quote.get("high"),
            "low": quote.get("low"),
            "close": quote.get("close"),
            "volume": quote.get("volume"),
        }
    )
    adjusted = result["indicators"].get("adjclose")
    if adjusted:
        frame["adj_close"] = adjusted[0].get("adjclose")
    else:
        frame["adj_close"] = frame["close"]
    frame = frame.dropna(subset=["close"]).drop_duplicates("date").sort_values("date")
    return frame.set_index("date")


def load_nasdaq(path: str | Path) -> pd.DataFrame:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload["data"]["tradesTable"]["rows"]
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"], format="%m/%d/%Y")
    for column in ("open", "high", "low", "close", "volume"):
        frame[column] = frame[column].map(_clean_number)
    frame["adj_close"] = frame["close"]
    frame = frame.dropna(subset=["close"]).drop_duplicates("date").sort_values("date")
    return frame.set_index("date")


def load_universe() -> dict[str, pd.DataFrame]:
    universe = {
        "MRNA": load_yahoo(PRICES / "MRNA_yahoo_chart.json"),
        "MRK": load_nasdaq(PRICES / "nasdaq_MRK.json"),
        "SPY": load_nasdaq(PRICES / "nasdaq_SPY.json"),
        "XBI": load_nasdaq(PRICES / "nasdaq_XBI.json"),
        "IBB": load_nasdaq(PRICES / "nasdaq_IBB.json"),
    }
    return universe


def close_panel(universe: dict[str, pd.DataFrame]) -> pd.DataFrame:
    series = {ticker: frame["close"] for ticker, frame in universe.items()}
    panel = pd.DataFrame(series).sort_index()
    return panel.dropna(how="any")


def log_returns(panel: pd.DataFrame) -> pd.DataFrame:
    return np.log(panel).diff().dropna()


def cross_check_mrna(universe: dict[str, pd.DataFrame]) -> dict[str, float | int | str]:
    yahoo = universe["MRNA"]["close"]
    nasdaq = load_nasdaq(PRICES / "nasdaq_MRNA.json")["close"]
    joined = pd.concat([yahoo.rename("yahoo"), nasdaq.rename("nasdaq")], axis=1).dropna()
    differences = (joined["yahoo"] - joined["nasdaq"]).abs()
    worst = differences.idxmax()
    return {
        "overlap_days": int(len(joined)),
        "max_abs_close_difference": float(differences.max()),
        "max_difference_date": str(worst.date()),
        "yahoo_close": float(joined.loc[worst, "yahoo"]),
        "nasdaq_close": float(joined.loc[worst, "nasdaq"]),
    }

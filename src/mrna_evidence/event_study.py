from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MarketModel:
    alpha: float
    beta: float
    residual_sigma: float
    r_squared: float
    nobs: int

    def abnormal(self, target: pd.Series, benchmark: pd.Series) -> pd.Series:
        return target - (self.alpha + self.beta * benchmark)


def fit_market_model(
    returns: pd.DataFrame,
    target: str,
    benchmark: str,
    start: str,
    end: str,
) -> MarketModel:
    sample = returns.loc[start:end, [target, benchmark]].dropna()
    if len(sample) < 30:
        raise ValueError(f"Not enough observations for {target} vs {benchmark}")
    y = sample[target].to_numpy(dtype=float)
    x = sample[benchmark].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    coefficients, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
    fitted = design @ coefficients
    residuals = y - fitted
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    sigma = float(np.sqrt(ss_res / max(len(y) - 2, 1)))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return MarketModel(float(coefficients[0]), float(coefficients[1]), sigma, r_squared, len(y))


def _window_positions(index: pd.Index, event_date: str, start: int, end: int) -> np.ndarray:
    position = index.get_loc(pd.Timestamp(event_date))
    offsets = np.arange(start, end + 1)
    positions = position + offsets
    if positions.min() < 0 or positions.max() >= len(index):
        raise ValueError(f"Event window for {event_date} exceeds available data")
    return positions


def _window_sum(series: pd.Series, positions: Iterable[int]) -> float:
    return float(series.iloc[list(positions)].sum())


def _percent(log_return: float) -> float:
    return float(np.expm1(log_return) * 100.0)


def _candidate_positions(
    index: pd.Index,
    window_start: int,
    window_end: int,
    event_dates: Iterable[str],
    guard_days: int,
) -> np.ndarray:
    blocked: set[int] = set()
    for event_date in event_dates:
        event_position = index.get_loc(pd.Timestamp(event_date))
        blocked.update(range(event_position - guard_days, event_position + guard_days + 1))
    candidates = []
    for position in range(len(index)):
        if position + window_start < 0:
            continue
        if position + window_end >= len(index):
            continue
        window_positions = set(range(position + window_start, position + window_end + 1))
        if window_positions & blocked:
            continue
        candidates.append(position)
    return np.asarray(candidates, dtype=int)


def placebo_test(
    abnormal_returns: pd.Series,
    event_car: float,
    window_start: int,
    window_end: int,
    event_dates: Iterable[str],
    draws: int,
    seed: int,
    guard_days: int,
) -> dict[str, float | int]:
    index = abnormal_returns.index
    candidates = _candidate_positions(index, window_start, window_end, event_dates, guard_days)
    if len(candidates) == 0:
        raise ValueError("No placebo candidates available")
    rng = np.random.default_rng(seed)
    sampled = rng.choice(candidates, size=draws, replace=True)
    values = np.asarray(
        [
            abnormal_returns.iloc[position + window_start : position + window_end + 1].sum()
            for position in sampled
        ],
        dtype=float,
    )
    p_value = float((1 + np.sum(np.abs(values) >= abs(event_car))) / (1 + draws))
    standard_deviation = float(values.std(ddof=1))
    z_score = float((event_car - values.mean()) / standard_deviation) if standard_deviation > 0 else float("nan")
    percentile = float((values < event_car).mean() * 100.0)
    return {
        "placebo_draws": int(draws),
        "placebo_mean": float(values.mean()),
        "placebo_sd": standard_deviation,
        "placebo_p": p_value,
        "placebo_z": z_score,
        "placebo_percentile": percentile,
    }


def placebo_distribution(
    abnormal_returns: pd.Series,
    window_start: int,
    window_end: int,
    event_dates: Iterable[str],
    draws: int,
    seed: int,
    guard_days: int,
) -> np.ndarray:
    index = abnormal_returns.index
    candidates = _candidate_positions(index, window_start, window_end, event_dates, guard_days)
    rng = np.random.default_rng(seed)
    sampled = rng.choice(candidates, size=draws, replace=True)
    return np.asarray(
        [
            abnormal_returns.iloc[position + window_start : position + window_end + 1].sum()
            for position in sampled
        ],
        dtype=float,
    )


def estimate_event_rows(
    returns: pd.DataFrame,
    events: list[dict],
    estimation: dict,
    windows: list[list[int]],
    benchmarks: list[str],
    placebo: dict,
) -> pd.DataFrame:
    event_dates = [event["date"] for event in events]
    rows: list[dict] = []
    for event in events:
        for benchmark in benchmarks:
            model = fit_market_model(
                returns,
                target="MRNA",
                benchmark=benchmark,
                start=estimation["start"],
                end=estimation["end"],
            )
            market_abnormal = model.abnormal(returns["MRNA"], returns[benchmark])
            adjusted_abnormal = returns["MRNA"] - returns[benchmark]
            for window in windows:
                start, end = int(window[0]), int(window[1])
                event_position = returns.index.get_loc(pd.Timestamp(event["date"]))
                if event_position + start < 0 or event_position + end >= len(returns.index):
                    continue
                positions = _window_positions(returns.index, event["date"], start, end)
                for model_name, abnormal in (
                    (f"market_model_{benchmark}", market_abnormal),
                    (f"market_adjusted_{benchmark}", adjusted_abnormal),
                ):
                    car = _window_sum(abnormal, positions)
                    raw = _window_sum(returns["MRNA"], positions)
                    placebo_result = placebo_test(
                        abnormal_returns=abnormal,
                        event_car=car,
                        window_start=start,
                        window_end=end,
                        event_dates=event_dates,
                        draws=int(placebo["draws"]),
                        seed=int(placebo["seed"]),
                        guard_days=int(placebo["guard_days"]),
                    )
                    rows.append(
                        {
                            "event_id": event["id"],
                            "event_date": event["date"],
                            "event_label": event["label"],
                            "model": model_name,
                            "benchmark": benchmark,
                            "window_start": start,
                            "window_end": end,
                            "window_days": end - start + 1,
                            "raw_return_pct": _percent(raw),
                            "car_log": car,
                            "car_pct": _percent(car),
                            "alpha": 0.0 if model_name.startswith("market_adjusted") else model.alpha,
                            "beta": 1.0 if model_name.startswith("market_adjusted") else model.beta,
                            "residual_sigma": model.residual_sigma,
                            "r_squared": model.r_squared,
                            "estimation_nobs": model.nobs,
                            **placebo_result,
                        }
                    )
    return pd.DataFrame(rows)


def event_window_table(
    prices: pd.DataFrame,
    events: list[dict],
    pre_days: int = 20,
    post_days: int = 20,
) -> pd.DataFrame:
    rows: list[dict] = []
    for event in events:
        position = prices.index.get_loc(pd.Timestamp(event["date"]))
        start = max(position - pre_days, 0)
        end = min(position + post_days, len(prices) - 1)
        window = prices.iloc[start : end + 1][["MRNA", "MRK", "SPY", "XBI"]].copy()
        base = window.loc[pd.Timestamp(event["date"])]
        indexed = window.divide(base) * 100.0
        indexed["relative_day"] = np.arange(start - position, end - position + 1)
        indexed["event_id"] = event["id"]
        indexed["event_date"] = event["date"]
        indexed["event_label"] = event["label"]
        indexed = indexed.reset_index().rename(columns={"index": "date"})
        rows.append(indexed)
    return pd.concat(rows, ignore_index=True)


def volume_table(prices: pd.DataFrame, raw_volume: pd.Series, events: list[dict], lookback: int) -> pd.DataFrame:
    rows: list[dict] = []
    aligned_volume = raw_volume.reindex(prices.index)
    for event in events:
        position = prices.index.get_loc(pd.Timestamp(event["date"]))
        prior = aligned_volume.iloc[max(0, position - lookback) : position].dropna()
        event_volume = float(aligned_volume.iloc[position])
        median = float(prior.median())
        mad = float((prior - median).abs().median())
        rows.append(
            {
                "event_id": event["id"],
                "event_date": event["date"],
                "volume": event_volume,
                "prior_median_volume": median,
                "volume_multiple": event_volume / median if median > 0 else float("nan"),
                "log_volume_abnormal": float(np.log(event_volume) - np.log(median)) if median > 0 else float("nan"),
                "prior_mad": mad,
                "prior_days": int(len(prior)),
                "prior_percentile": float((prior < event_volume).mean() * 100.0),
                "dollar_volume": float(prices.loc[pd.Timestamp(event["date"]), "MRNA"] * event_volume),
            }
        )
    return pd.DataFrame(rows)


def market_cap_table(
    prices: pd.DataFrame,
    events: list[dict],
    shares_outstanding: int,
) -> pd.DataFrame:
    rows: list[dict] = []
    for event in events:
        event_date = pd.Timestamp(event["date"])
        prior_date = pd.Timestamp(event["prior_date"])
        event_close = float(prices.loc[event_date, "MRNA"])
        prior_close = float(prices.loc[prior_date, "MRNA"])
        event_cap = event_close * shares_outstanding
        prior_cap = prior_close * shares_outstanding
        rows.append(
            {
                "event_id": event["id"],
                "event_date": event["date"],
                "prior_date": event["prior_date"],
                "prior_close": prior_close,
                "event_close": event_close,
                "close_return_pct": (event_close / prior_close - 1.0) * 100.0,
                "prior_market_cap_usd": prior_cap,
                "event_market_cap_usd": event_cap,
                "market_cap_change_usd": event_cap - prior_cap,
                "shares_outstanding": shares_outstanding,
            }
        )
    return pd.DataFrame(rows)

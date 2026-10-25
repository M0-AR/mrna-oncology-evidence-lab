from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from . import figures
from .claims import claim_counts, claim_table, source_table, verdict_totals
from .clinical import (
    derived_clinical_metrics,
    endpoint_table,
    enrollment_table,
    safety_table,
    trial_profile,
)
from .config import load_config
from .event_study import (
    estimate_event_rows,
    event_window_table,
    market_cap_table,
    volume_table,
)
from .financials import annual_table, derived_financial_metrics, quarterly_table
from .manifest import build_manifest, build_price_manifest, verify_all
from .paths import MANIFESTS, PAPER, PROCESSED, TABLES, ensure_directories
from .prices import close_panel, cross_check_mrna, load_universe, log_returns


def _write_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(TABLES / name, index=False)


def _json_default(value: object) -> object:
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def run() -> dict:
    ensure_directories()
    sources = load_config("sources.yaml")
    claims = load_config("claims.yaml")
    events_config = load_config("events.yaml")
    clinical_config = load_config("clinical_endpoints.yaml")
    financial_config = load_config("financials.yaml")

    snapshot_manifest = build_manifest(sources["sources"])
    price_manifest = build_price_manifest()
    verification = verify_all()

    universe = load_universe()
    prices = close_panel(universe)
    returns = log_returns(prices)
    cross_check = cross_check_mrna(universe)

    event_rows = estimate_event_rows(
        returns=returns,
        events=events_config["events"],
        estimation=events_config["estimation"],
        windows=events_config["event_windows"],
        benchmarks=events_config["estimation"]["benchmarks"],
        placebo=events_config["placebo"],
    )
    volumes = volume_table(
        prices=prices,
        raw_volume=universe["MRNA"]["volume"],
        events=events_config["events"],
        lookback=int(events_config["volume_lookback_days"]),
    )
    market_caps = market_cap_table(
        prices=prices,
        events=events_config["events"],
        shares_outstanding=int(events_config["shares_outstanding"]),
    )
    windows = event_window_table(prices, events_config["events"])

    endpoints = endpoint_table(clinical_config)
    safety = safety_table(clinical_config)
    enrollment = enrollment_table(clinical_config)
    clinical_metrics = derived_clinical_metrics(clinical_config)
    profile = trial_profile(clinical_config)

    annual = annual_table(financial_config)
    quarterly = quarterly_table(financial_config)
    financial_metrics = derived_financial_metrics(financial_config)

    claims_frame = claim_table(claims)
    counts = claim_counts(claims)
    totals = verdict_totals(claims)
    sources_frame = source_table(sources)
    missing = sources_frame[(sources_frame["snapshot"] != "") & (~sources_frame["snapshot_exists"])]
    if not missing.empty:
        raise FileNotFoundError(f"Missing source snapshots:\n{missing[['source_id', 'snapshot']].to_string(index=False)}")

    _write_csv(endpoints, "clinical_endpoints.csv")
    _write_csv(safety, "clinical_safety.csv")
    _write_csv(enrollment, "clinical_enrollment.csv")
    _write_csv(clinical_metrics, "derived_clinical_metrics.csv")
    _write_csv(event_rows, "event_study.csv")
    _write_csv(volumes, "event_volume.csv")
    _write_csv(market_caps, "event_market_caps.csv")
    _write_csv(windows, "event_windows.csv")
    _write_csv(annual, "financial_annual.csv")
    _write_csv(quarterly, "financial_quarterly.csv")
    _write_csv(financial_metrics, "derived_financial_metrics.csv")
    _write_csv(claims_frame, "claims.csv")
    _write_csv(counts, "claim_counts.csv")
    _write_csv(sources_frame, "sources.csv")

    prices.to_csv(PROCESSED / "prices.csv")
    returns.to_csv(PROCESSED / "returns.csv")
    event_rows.to_csv(PROCESSED / "event_study.csv", index=False)

    figures.build_all_figures(
        prices=prices,
        windows=windows,
        claim_counts=counts,
        clinical_config=clinical_config,
        financial_config=financial_config,
        returns=returns,
        events=events_config["events"],
        estimation=events_config["estimation"],
        placebo=events_config["placebo"],
    )

    primary_events = event_rows[
        (event_rows["model"] == "market_model_SPY")
        & (event_rows["window_start"].isin([-1, 0]))
        & (event_rows["window_end"].isin([0, 1]))
    ]
    endpoints = {endpoint["id"]: endpoint for endpoint in clinical_config["endpoints"]}

    def endpoint_value(endpoint_id: str) -> float:
        return float(endpoints[endpoint_id]["value"])

    def endpoint_ci(endpoint_id: str) -> list[float]:
        endpoint = endpoints[endpoint_id]
        return [float(endpoint["ci_low"]), float(endpoint["ci_high"])]

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trial": profile,
        "headline": {
            "rfs_itt_hr": endpoint_value("rfs_itt_hr"),
            "rfs_itt_ci": endpoint_ci("rfs_itt_hr"),
            "rfs_risk_reduction_pct": float(endpoints["rfs_itt_hr"]["risk_reduction_pct"]),
            "dmfs_itt_hr": endpoint_value("dmfs_itt_hr"),
            "dmfs_itt_ci": endpoint_ci("dmfs_itt_hr"),
            "dmfs_risk_reduction_pct": float(endpoints["dmfs_itt_hr"]["risk_reduction_pct"]),
            "os_itt_hr": endpoint_value("os_itt_hr"),
            "os_itt_ci": endpoint_ci("os_itt_hr"),
            "first_6m_rfs_hr": endpoint_value("rfs_first_6m_hr"),
            "after_6m_rfs_hr": endpoint_value("rfs_after_6m_hr"),
            "rfs_2y_combination_pct": endpoint_value("rfs_2y_combination"),
            "rfs_2y_control_pct": endpoint_value("rfs_2y_control"),
            "dmfs_2y_combination_pct": endpoint_value("dmfs_2y_combination"),
            "dmfs_2y_control_pct": endpoint_value("dmfs_2y_control"),
            "median_followup_months": float(clinical_config["median_followup_months"]),
        },
        "derived_clinical": clinical_metrics.set_index("metric")["value"].to_dict(),
        "event_study_primary": primary_events.to_dict(orient="records"),
        "event_volume": volumes.to_dict(orient="records"),
        "market_caps": market_caps.to_dict(orient="records"),
        "price_cross_check": cross_check,
        "financial_annual": annual.to_dict(orient="records"),
        "derived_financial": financial_metrics.set_index("metric")["value"].to_dict(),
        "claims": totals,
        "claim_count": int(len(claims_frame)),
        "source_count": int(len(sources_frame)),
        "manifest": {
            "snapshots": snapshot_manifest["count"],
            "prices": price_manifest["count"],
            "missing": snapshot_manifest["missing"],
            "verification": verification,
        },
    }
    (PAPER / "results_summary.json").write_text(
        json.dumps(summary, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    (MANIFESTS / "run_summary.json").write_text(
        json.dumps(summary, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    result = run()
    print(json.dumps({"claims": result["claims"], "sources": result["source_count"], "events": len(result["event_study_primary"])}, indent=2))

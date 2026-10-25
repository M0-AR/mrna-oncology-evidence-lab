from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .clinical import derived_clinical_metrics, endpoint_table
from .event_study import fit_market_model, placebo_distribution
from .financials import annual_table
from .paths import FIGURES, PAPER_FIGURES


def _save(figure: plt.Figure, name: str) -> None:
    figure.tight_layout()
    for directory in (FIGURES, PAPER_FIGURES):
        directory.mkdir(parents=True, exist_ok=True)
        figure.savefig(directory / name, dpi=220, bbox_inches="tight")
    plt.close(figure)


def price_history(prices: pd.DataFrame, events: list[dict]) -> None:
    figure, axis = plt.subplots(figsize=(10, 5.2))
    series = prices["MRNA"].loc["2019-01-01":]
    axis.plot(series.index, series.values, color="#0b4f6c", linewidth=1.4)
    axis.set_yscale("log")
    axis.set_ylim(top=1000)
    axis.set_xlim(series.index.min(), series.index.max() + pd.Timedelta(days=45))
    axis.set_ylabel("Adjusted close (USD, log scale)")
    axis.set_title("Moderna daily close and the two INTerpath-001 shocks")
    axis.grid(alpha=0.25)
    label_y = {"event_1": 650, "event_2": 420}
    for event in events:
        date = pd.Timestamp(event["date"])
        axis.axvline(date, color="#c1121f", linestyle="--", linewidth=1.1)
        axis.text(
            date,
            label_y[event["id"]],
            event["label"],
            ha="right",
            va="bottom",
            fontsize=8,
            color="#c1121f",
        )
    _save(figure, "fig01_mrna_price_history.png")


def event_windows(windows: pd.DataFrame) -> None:
    event_ids = list(windows["event_id"].unique())
    figure, axes = plt.subplots(1, len(event_ids), figsize=(12, 4.8), sharey=False)
    if len(event_ids) == 1:
        axes = [axes]
    colors = {"MRNA": "#c1121f", "MRK": "#2a9d8f", "SPY": "#457b9d", "XBI": "#e9c46a"}
    for axis, event_id in zip(axes, event_ids):
        subset = windows[windows["event_id"] == event_id]
        for ticker in ("MRNA", "MRK", "SPY", "XBI"):
            axis.plot(subset["relative_day"], subset[ticker], label=ticker, color=colors[ticker], linewidth=1.5)
        axis.axvline(0, color="black", linewidth=0.8)
        axis.axhline(100, color="black", linewidth=0.6, linestyle=":")
        axis.set_title(subset["event_label"].iloc[0])
        axis.set_xlabel("Trading days relative to event")
        axis.set_ylabel("Indexed to event day = 100")
        axis.grid(alpha=0.25)
    axes[0].legend(frameon=False, ncol=2)
    _save(figure, "fig02_event_windows.png")


def clinical_forest(config: dict) -> None:
    endpoints = {row["id"]: row for row in config["endpoints"]}
    phase2 = config["phase2_5y"]
    rows = [
        ("Phase 3 RFS, overall", float(endpoints["rfs_itt_hr"]["value"]), float(endpoints["rfs_itt_hr"]["ci_low"]), float(endpoints["rfs_itt_hr"]["ci_high"])),
        ("Phase 3 RFS, first 6 months", float(endpoints["rfs_first_6m_hr"]["value"]), float(endpoints["rfs_first_6m_hr"]["ci_low"]), float(endpoints["rfs_first_6m_hr"]["ci_high"])),
        ("Phase 3 RFS, after 6 months", float(endpoints["rfs_after_6m_hr"]["value"]), float(endpoints["rfs_after_6m_hr"]["ci_low"]), float(endpoints["rfs_after_6m_hr"]["ci_high"])),
        ("Phase 3 DMFS, overall", float(endpoints["dmfs_itt_hr"]["value"]), float(endpoints["dmfs_itt_hr"]["ci_low"]), float(endpoints["dmfs_itt_hr"]["ci_high"])),
        ("Phase 3 DMFS, after 6 months", float(endpoints["dmfs_after_6m_hr"]["value"]), float(endpoints["dmfs_after_6m_hr"]["ci_low"]), float(endpoints["dmfs_after_6m_hr"]["ci_high"])),
        ("Phase 2 RFS, 5-year", float(phase2["rfs"]["hr"]), float(phase2["rfs"]["ci_low"]), float(phase2["rfs"]["ci_high"])),
        ("Phase 2 DMFS, 5-year", float(phase2["dmfs"]["hr"]), float(phase2["dmfs"]["ci_low"]), float(phase2["dmfs"]["ci_high"])),
        ("Phase 3 OS, immature", float(endpoints["os_itt_hr"]["value"]), float(endpoints["os_itt_hr"]["ci_low"]), float(endpoints["os_itt_hr"]["ci_high"])),
    ]
    figure, axis = plt.subplots(figsize=(8.4, 5.6))
    positions = np.arange(len(rows))[::-1]
    for position, (label, value, low, high) in zip(positions, rows):
        axis.plot([low, high], [position, position], color="#264653", linewidth=1.6)
        axis.plot(value, position, "o", color="#c1121f", markersize=6)
    axis.axvline(1.0, color="black", linestyle="--", linewidth=0.9)
    axis.set_xscale("log")
    axis.set_xlim(0.12, 1.6)
    axis.set_yticks(positions)
    axis.set_yticklabels([f"{label}   {value:.2f} ({low:.2f}-{high:.2f})" for label, value, low, high in rows], fontsize=9)
    axis.set_xlabel("Hazard ratio (log scale)")
    axis.set_title("Delayed divergence and Phase 2 to Phase 3 attenuation")
    axis.grid(axis="x", alpha=0.25)
    _save(figure, "fig03_clinical_forest.png")


def claim_ledger(counts: pd.DataFrame) -> None:
    verdict_order = ["supported", "partially_supported", "unsupported", "not_verifiable"]
    colors = {
        "supported": "#2a9d8f",
        "partially_supported": "#e9c46a",
        "unsupported": "#c1121f",
        "not_verifiable": "#6c757d",
    }
    pivot = counts.pivot(index="category", columns="verdict", values="count").fillna(0)
    pivot = pivot.reindex(columns=[column for column in verdict_order if column in pivot.columns], fill_value=0)
    figure, axes = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [2.2, 1]})
    pivot.plot(kind="barh", stacked=True, ax=axes[0], color=[colors[column] for column in pivot.columns])
    axes[0].set_xlabel("Claims")
    axes[0].set_ylabel("")
    axes[0].set_title("Claim ledger by category and verdict")
    axes[0].legend(frameon=False, ncol=2, fontsize=8)
    axes[0].grid(axis="x", alpha=0.25)
    totals = counts.groupby("verdict")["count"].sum().reindex(verdict_order).fillna(0)
    axes[1].bar(totals.index, totals.values, color=[colors[column] for column in totals.index])
    axes[1].set_title("Verdict totals")
    axes[1].tick_params(axis="x", rotation=20, labelsize=8)
    axes[1].grid(axis="y", alpha=0.25)
    for index, value in enumerate(totals.values):
        axes[1].text(index, value + 0.3, str(int(value)), ha="center", fontsize=9)
    _save(figure, "fig04_claim_ledger.png")


def financial_trends(config: dict) -> None:
    annual = annual_table(config)
    figure, axis = plt.subplots(figsize=(9, 5))
    x = np.arange(len(annual))
    width = 0.38
    axis.bar(x - width / 2, annual["total_revenue"], width, label="Total revenue", color="#457b9d")
    axis.bar(x + width / 2, annual["product_sales"], width, label="Product sales", color="#2a9d8f")
    axis.set_xticks(x)
    axis.set_xticklabels(annual["year"].astype(int))
    axis.set_ylabel("USD millions")
    axis.grid(axis="y", alpha=0.25)
    axis2 = axis.twinx()
    axis2.plot(x, annual["net_income"], color="#c1121f", marker="o", linewidth=1.6, label="Net income")
    axis2.axhline(0, color="black", linewidth=0.7, linestyle=":")
    axis2.set_ylabel("Net income (USD millions)")
    handles1, labels1 = axis.get_legend_handles_labels()
    handles2, labels2 = axis2.get_legend_handles_labels()
    axis.legend(handles1 + handles2, labels1 + labels2, frameon=False, loc="upper right")
    axis.set_title("Moderna revenue and profitability after the pandemic peak")
    _save(figure, "fig05_financial_trends.png")


def placebo_panel(
    returns: pd.DataFrame,
    events: list[dict],
    estimation: dict,
    placebo: dict,
) -> None:
    event = events[0]
    model = fit_market_model(returns, "MRNA", "SPY", estimation["start"], estimation["end"])
    abnormal = model.abnormal(returns["MRNA"], returns["SPY"])
    distribution = placebo_distribution(
        abnormal_returns=abnormal,
        window_start=0,
        window_end=0,
        event_dates=[item["date"] for item in events],
        draws=int(placebo["draws"]),
        seed=int(placebo["seed"]),
        guard_days=int(placebo["guard_days"]),
    )
    observed = float(abnormal.loc[pd.Timestamp(event["date"])])
    p_value = float((1 + np.sum(np.abs(distribution) >= abs(observed))) / (1 + len(distribution)))
    distribution_pct = np.expm1(distribution) * 100.0
    observed_pct = float(np.expm1(observed) * 100.0)
    figure, axis = plt.subplots(figsize=(8.4, 4.8))
    axis.hist(distribution_pct, bins=70, color="#457b9d", alpha=0.8, density=True)
    axis.axvline(observed_pct, color="#c1121f", linewidth=2, label=f"Observed {observed_pct:.1f}%")
    axis.set_xlabel("Placebo abnormal return (%)")
    axis.set_ylabel("Density")
    axis.set_title(f"Placebo distribution for the topline event (empirical p={p_value:.4f})")
    axis.legend(frameon=False)
    axis.grid(alpha=0.2)
    _save(figure, "fig06_placebo_distribution.png")


def build_all_figures(
    prices: pd.DataFrame,
    windows: pd.DataFrame,
    claim_counts: pd.DataFrame,
    clinical_config: dict,
    financial_config: dict,
    returns: pd.DataFrame,
    events: list[dict],
    estimation: dict,
    placebo: dict,
) -> None:
    price_history(prices, events)
    event_windows(windows)
    clinical_forest(clinical_config)
    claim_ledger(claim_counts)
    financial_trends(financial_config)
    placebo_panel(returns, events, estimation, placebo)

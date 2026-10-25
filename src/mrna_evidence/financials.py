from __future__ import annotations

import pandas as pd

from .config import load_config


def annual_table(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config("financials.yaml")
    frame = pd.DataFrame(config["annual"]).sort_values("year").reset_index(drop=True)
    frame["revenue_yoy_pct"] = frame["total_revenue"].pct_change() * 100.0
    frame["product_sales_yoy_pct"] = frame["product_sales"].pct_change() * 100.0
    frame["net_margin_pct"] = frame["net_income"] / frame["total_revenue"] * 100.0
    frame["rnd_intensity_pct"] = frame["rnd"] / frame["total_revenue"] * 100.0
    return frame


def derived_financial_metrics(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config("financials.yaml")
    annual = annual_table(config)
    by_year = annual.set_index("year")
    keytruda = config["keytruda"]
    keytruda_share = keytruda["sales"] / keytruda["merck_total_sales"] * 100.0
    rows = [
        ("pandemic_revenue_2021_2022", float(by_year.loc[2021, "total_revenue"] + by_year.loc[2022, "total_revenue"]), "USD_millions", "2021 plus 2022 total revenue"),
        ("pandemic_product_sales_2021_2022", float(by_year.loc[2021, "product_sales"] + by_year.loc[2022, "product_sales"]), "USD_millions", "2021 plus 2022 product sales"),
        ("revenue_change_2023_2024_pct", float(by_year.loc[2024, "revenue_yoy_pct"]), "percent", "2024 total revenue growth"),
        ("product_change_2023_2024_pct", float(by_year.loc[2024, "product_sales_yoy_pct"]), "percent", "2024 product sales growth"),
        ("revenue_change_2024_2025_pct", float(by_year.loc[2025, "revenue_yoy_pct"]), "percent", "2025 total revenue growth"),
        ("product_change_2024_2025_pct", float(by_year.loc[2025, "product_sales_yoy_pct"]), "percent", "2025 product sales growth"),
        ("net_margin_2022_pct", float(by_year.loc[2022, "net_margin_pct"]), "percent", "2022 net income over revenue"),
        ("net_margin_2023_pct", float(by_year.loc[2023, "net_margin_pct"]), "percent", "2023 net income over revenue"),
        ("net_margin_2024_pct", float(by_year.loc[2024, "net_margin_pct"]), "percent", "2024 net income over revenue"),
        ("net_margin_2025_pct", float(by_year.loc[2025, "net_margin_pct"]), "percent", "2025 net income over revenue"),
        ("rnd_intensity_2023_pct", float(by_year.loc[2023, "rnd_intensity_pct"]), "percent", "2023 R&D over revenue"),
        ("rnd_intensity_2024_pct", float(by_year.loc[2024, "rnd_intensity_pct"]), "percent", "2024 R&D over revenue"),
        ("rnd_intensity_2025_pct", float(by_year.loc[2025, "rnd_intensity_pct"]), "percent", "2025 R&D over revenue"),
        ("keytruda_share_merck_2022_pct", keytruda_share, "percent", "Keytruda sales over Merck total sales"),
        ("keytruda_sales_2022", float(keytruda["sales"]), "USD_millions", "2022 Keytruda sales"),
        ("merck_total_sales_2022", float(keytruda["merck_total_sales"]), "USD_millions", "2022 Merck total sales"),
    ]
    return pd.DataFrame(rows, columns=["metric", "value", "unit", "definition"])


def quarterly_table(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config("financials.yaml")
    quarterly = config["quarterly_2026_q2"]
    return pd.DataFrame(
        [
            {
                "period": "2026-Q2",
                "total_revenue": quarterly["total_revenue"],
                "net_loss": quarterly["net_loss"],
                "eps": quarterly["eps"],
                "rnd": quarterly["rnd"],
                "source": quarterly["source"],
            }
        ]
    )

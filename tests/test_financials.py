import pytest

from mrna_evidence.financials import annual_table, derived_financial_metrics, quarterly_table


def test_annual_table():
    annual = annual_table().set_index("year")
    assert annual.loc[2021, "total_revenue"] == 18471
    assert annual.loc[2022, "total_revenue"] == 19263
    assert annual.loc[2023, "net_income"] == -4714
    assert annual.loc[2024, "total_revenue"] == 3236
    assert annual.loc[2025, "total_revenue"] == 1944


def test_derived_financials():
    metrics = derived_financial_metrics().set_index("metric")["value"]
    assert metrics["pandemic_revenue_2021_2022"] == pytest.approx(37734)
    assert metrics["pandemic_product_sales_2021_2022"] == pytest.approx(36110)
    assert metrics["keytruda_share_merck_2022_pct"] == pytest.approx(35.3170386114063, abs=1e-9)
    assert metrics["net_margin_2023_pct"] == pytest.approx(-68.83761682242991, abs=1e-9)


def test_quarterly():
    quarterly = quarterly_table().iloc[0]
    assert quarterly["total_revenue"] == 145
    assert quarterly["net_loss"] == -782
    assert quarterly["eps"] == pytest.approx(-1.97)

import numpy as np
import pandas as pd
import pytest

from mrna_evidence.event_study import (
    _window_positions,
    fit_market_model,
    market_cap_table,
    placebo_test,
)


def synthetic_returns(periods=400, beta=1.4, seed=7):
    rng = np.random.default_rng(seed)
    index = pd.bdate_range("2020-01-01", periods=periods)
    benchmark = pd.Series(rng.normal(0.0003, 0.01, periods), index=index)
    noise = pd.Series(rng.normal(0.0, 0.008, periods), index=index)
    target = 0.0002 + beta * benchmark + noise
    return pd.DataFrame({"MRNA": target, "SPY": benchmark})


def test_market_model_recovers_beta():
    returns = synthetic_returns()
    model = fit_market_model(returns, "MRNA", "SPY", "2020-01-01", "2021-04-01")
    assert model.beta == pytest.approx(1.4, abs=0.08)
    assert 0.5 < model.r_squared <= 1.0
    assert model.nobs > 250


def test_event_window_positions():
    returns = synthetic_returns(periods=50)
    positions = _window_positions(returns.index, str(returns.index[10].date()), -2, 2)
    assert positions.tolist() == [8, 9, 10, 11, 12]


def test_placebo_p_value_is_bounded():
    returns = synthetic_returns()
    model = fit_market_model(returns, "MRNA", "SPY", "2020-01-01", "2021-04-01")
    abnormal = model.abnormal(returns["MRNA"], returns["SPY"])
    result = placebo_test(
        abnormal_returns=abnormal,
        event_car=0.05,
        window_start=0,
        window_end=0,
        event_dates=[str(returns.index[300].date())],
        draws=500,
        seed=1,
        guard_days=5,
    )
    assert 0.0 < result["placebo_p"] <= 1.0
    assert result["placebo_draws"] == 500


def test_market_cap_arithmetic():
    index = pd.bdate_range("2026-08-18", periods=2)
    prices = pd.DataFrame({"MRNA": [62.96, 174.38]}, index=index)
    events = [{"id": "event_1", "date": "2026-08-19", "prior_date": "2026-08-18"}]
    table = market_cap_table(prices, events, shares_outstanding=399_235_889)
    row = table.iloc[0]
    assert row["market_cap_change_usd"] == pytest.approx((174.38 - 62.96) * 399_235_889)
    assert row["close_return_pct"] == pytest.approx(176.96950444726812, abs=1e-9)

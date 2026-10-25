import numpy as np
import pandas as pd
import pytest

from mrna_evidence.prices import close_panel, cross_check_mrna, load_universe, log_returns


@pytest.fixture(scope="module")
def universe():
    return load_universe()


def test_known_event_closes(universe):
    mrna = universe["MRNA"]["close"]
    assert mrna.loc[pd.Timestamp("2026-08-18")] == pytest.approx(62.96, abs=1e-4)
    assert mrna.loc[pd.Timestamp("2026-08-19")] == pytest.approx(174.38, abs=1e-4)
    assert mrna.loc[pd.Timestamp("2026-10-22")] == pytest.approx(202.63, abs=1e-4)
    assert universe["MRNA"]["volume"].loc[pd.Timestamp("2026-08-19")] == pytest.approx(199252300)


def test_source_cross_check(universe):
    check = cross_check_mrna(universe)
    assert check["overlap_days"] == 454
    assert check["max_abs_close_difference"] < 1e-4


def test_panel_alignment(universe):
    panel = close_panel(universe)
    assert list(panel.columns) == ["MRNA", "MRK", "SPY", "XBI", "IBB"]
    assert panel.index.is_monotonic_increasing
    assert not panel.isna().any().any()
    returns = log_returns(panel)
    assert len(returns) == len(panel) - 1
    assert np.isfinite(returns.to_numpy()).all()

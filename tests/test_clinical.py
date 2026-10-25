import pytest

from mrna_evidence.clinical import (
    derived_clinical_metrics,
    endpoint_table,
    enrollment_table,
    safety_table,
)


def test_endpoint_table():
    table = endpoint_table()
    assert len(table) == 13
    rfs = table.set_index("id").loc["rfs_itt_hr"]
    assert rfs["value"] == pytest.approx(0.58)
    assert rfs["ci_low"] == pytest.approx(0.45)
    assert rfs["ci_high"] == pytest.approx(0.75)


def test_derived_delayed_divergence():
    metrics = derived_clinical_metrics().set_index("metric")["value"]
    assert metrics["absolute_rfs_gain_2y_pct"] == pytest.approx(12.2)
    assert metrics["nnt_2y_rfs"] == pytest.approx(8.19672131147541)
    assert metrics["delayed_effect_ratio"] == pytest.approx(0.42424242424242425)
    assert metrics["phase2_to_phase3_rfs_attenuation_pp"] == pytest.approx(7.0)
    assert metrics["phase2_to_phase3_dmfs_attenuation_pp"] == pytest.approx(21.0)


def test_safety_arithmetic():
    metrics = derived_clinical_metrics().set_index("metric")["value"]
    assert metrics["trae_any_excess_pp"] == pytest.approx(5.8)
    assert metrics["nnh_any_trae"] == pytest.approx(17.241379310344836)
    assert metrics["nnh_grade3_5_trae"] == pytest.approx(125.0)


def test_enrollment_and_safety_tables():
    enrollment = enrollment_table().iloc[0]
    assert enrollment["randomized"] == 1137
    assert enrollment["combination_n"] + enrollment["control_n"] == 1137
    assert enrollment["safety_combination_n"] + enrollment["safety_control_n"] == 1135
    safety = safety_table()
    assert len(safety) == 4

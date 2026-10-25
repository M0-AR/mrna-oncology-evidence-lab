from __future__ import annotations

import pandas as pd

from .config import load_config


def endpoint_table(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config("clinical_endpoints.yaml")
    rows = []
    for endpoint in config["endpoints"]:
        row = dict(endpoint)
        row["kind"] = "endpoint"
        rows.append(row)
    return pd.DataFrame(rows)


def safety_table(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config("clinical_endpoints.yaml")
    rows = []
    for event in config["safety"]:
        row = dict(event)
        row["kind"] = "safety"
        rows.append(row)
    return pd.DataFrame(rows)


def enrollment_table(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config("clinical_endpoints.yaml")
    enrollment = config["enrollment"]
    return pd.DataFrame(
        [
            {
                "randomized": enrollment["randomized"],
                "combination_n": enrollment["combination_n"],
                "control_n": enrollment["control_n"],
                "safety_combination_n": enrollment["safety_combination_n"],
                "safety_control_n": enrollment["safety_control_n"],
                "randomization_ratio": enrollment["ratio"],
                "median_followup_months": config["median_followup_months"],
            }
        ]
    )


def derived_clinical_metrics(config: dict | None = None) -> pd.DataFrame:
    config = config or load_config("clinical_endpoints.yaml")
    endpoints = {row["id"]: row for row in config["endpoints"]}
    phase2 = config["phase2_5y"]
    rfs_2y_combination = float(endpoints["rfs_2y_combination"]["value"])
    rfs_2y_control = float(endpoints["rfs_2y_control"]["value"])
    dmfs_2y_combination = float(endpoints["dmfs_2y_combination"]["value"])
    dmfs_2y_control = float(endpoints["dmfs_2y_control"]["value"])
    absolute_rfs = rfs_2y_combination - rfs_2y_control
    absolute_dmfs = dmfs_2y_combination - dmfs_2y_control
    first_6m_rfs = float(endpoints["rfs_first_6m_hr"]["value"])
    after_6m_rfs = float(endpoints["rfs_after_6m_hr"]["value"])
    phase3_rfs_reduction = float(endpoints["rfs_itt_hr"]["risk_reduction_pct"])
    phase3_dmfs_reduction = float(endpoints["dmfs_itt_hr"]["risk_reduction_pct"])
    phase2_rfs_reduction = float(phase2["rfs"]["risk_reduction_pct"])
    phase2_dmfs_reduction = float(phase2["dmfs"]["risk_reduction_pct"])
    safety = {row["id"]: row for row in config["safety"]}
    trae_excess = float(safety["trae_any_combination"]["value"]) - float(safety["trae_any_control"]["value"])
    grade35_excess = float(safety["trae_grade3_5_combination"]["value"]) - float(safety["trae_grade3_5_control"]["value"])
    rows = [
        ("absolute_rfs_gain_2y_pct", absolute_rfs, "percentage_points", "2-year RFS difference"),
        ("absolute_dmfs_gain_2y_pct", absolute_dmfs, "percentage_points", "2-year DMFS difference"),
        ("nnt_2y_rfs", 100.0 / absolute_rfs, "patients", "Number needed to treat for one additional recurrence-free patient"),
        ("nnt_2y_dmfs", 100.0 / absolute_dmfs, "patients", "Number needed to treat for one additional distant-metastasis-free patient"),
        ("delayed_effect_ratio", after_6m_rfs / first_6m_rfs, "ratio", "Post-six-month HR divided by first-six-month HR"),
        ("delayed_relative_reduction_pct", (1.0 - after_6m_rfs / first_6m_rfs) * 100.0, "percent", "Relative reduction after six months versus first six months"),
        ("phase2_to_phase3_rfs_attenuation_pp", phase2_rfs_reduction - phase3_rfs_reduction, "percentage_points", "Phase 2 minus Phase 3 RFS reduction"),
        ("phase2_to_phase3_dmfs_attenuation_pp", phase2_dmfs_reduction - phase3_dmfs_reduction, "percentage_points", "Phase 2 minus Phase 3 DMFS reduction"),
        ("phase2_to_phase3_rfs_attenuation_relative_pct", (phase2_rfs_reduction - phase3_rfs_reduction) / phase2_rfs_reduction * 100.0, "percent", "Relative attenuation in RFS effect"),
        ("phase2_to_phase3_dmfs_attenuation_relative_pct", (phase2_dmfs_reduction - phase3_dmfs_reduction) / phase2_dmfs_reduction * 100.0, "percent", "Relative attenuation in DMFS effect"),
        ("phase3_phase2_hr_ratio_rfs", float(endpoints["rfs_itt_hr"]["value"]) / float(phase2["rfs"]["hr"]), "ratio", "Phase 3 HR divided by Phase 2 HR"),
        ("phase3_phase2_hr_ratio_dmfs", float(endpoints["dmfs_itt_hr"]["value"]) / float(phase2["dmfs"]["hr"]), "ratio", "Phase 3 HR divided by Phase 2 HR"),
        ("mitt_vs_itt_hr_ratio_rfs", float(endpoints["rfs_mitt_hr"]["value"]) / float(endpoints["rfs_itt_hr"]["value"]), "ratio", "mITT HR divided by ITT HR"),
        ("trae_any_excess_pp", trae_excess, "percentage_points", "Any TRAE combination minus control"),
        ("nnh_any_trae", 100.0 / trae_excess, "patients", "Number needed to harm for one additional any-grade TRAE"),
        ("trae_grade3_5_excess_pp", grade35_excess, "percentage_points", "Grade 3-5 TRAE combination minus control"),
        ("nnh_grade3_5_trae", 100.0 / grade35_excess, "patients", "Number needed to harm for one additional Grade 3-5 TRAE"),
    ]
    return pd.DataFrame(rows, columns=["metric", "value", "unit", "definition"])


def trial_profile(config: dict | None = None) -> dict:
    config = config or load_config("clinical_endpoints.yaml")
    return {
        "trial": config["trial"],
        "registry": config["registry"],
        "median_followup_months": config["median_followup_months"],
        "enrollment": config["enrollment"],
        "phase2_5y": config["phase2_5y"],
    }

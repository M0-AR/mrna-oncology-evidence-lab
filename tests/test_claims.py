import pandas as pd

from mrna_evidence.claims import (
    claim_counts,
    claim_table,
    source_table,
    validate_claims,
    verdict_totals,
)
from mrna_evidence.config import load_config


def test_claims_validate():
    config = load_config("claims.yaml")
    assert validate_claims(config) == []
    assert len(config["claims"]) == 42


def test_claim_totals_sum():
    totals = verdict_totals()
    assert sum(totals.values()) == 42
    assert totals["supported"] == 18
    assert totals["partially_supported"] == 14
    assert totals["unsupported"] == 10


def test_claim_table_and_counts():
    table = claim_table()
    assert len(table) == 42
    assert table["sources_joined"].str.len().min() > 0
    counts = claim_counts()
    assert counts["count"].sum() == 42


def test_specific_grades():
    table = claim_table().set_index("id")
    assert table.loc["C05", "verdict"] == "unsupported"
    assert table.loc["C16", "verdict"] == "partially_supported"
    assert table.loc["C27", "sources_joined"] == "merck_10k_2025"
    assert table.loc["C31", "verdict"] == "partially_supported"


def test_sources():
    sources = source_table()
    assert len(sources) == 29
    assert sources["snapshot_exists"].sum() == 28

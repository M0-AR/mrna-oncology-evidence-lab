from mrna_evidence.manifest import build_manifest, build_price_manifest, sha256, verify_all
from mrna_evidence.config import load_config
from mrna_evidence.paths import MANIFESTS


def test_sha256_known(tmp_path):
    path = tmp_path / "value.txt"
    path.write_text("evidence\n", encoding="utf-8")
    digest = sha256(path)
    assert len(digest) == 64
    assert int(digest, 16) >= 0


def test_manifests_verify():
    if not (MANIFESTS / "snapshots.json").exists():
        build_manifest(load_config("sources.yaml")["sources"])
    if not (MANIFESTS / "prices.json").exists():
        build_price_manifest()
    result = verify_all()
    assert result["snapshots.json"]["ok"]
    assert result["prices.json"]["ok"]
    assert result["snapshots.json"]["checked"] == 28
    assert result["prices.json"]["checked"] == 6

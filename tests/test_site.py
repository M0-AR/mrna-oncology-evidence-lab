import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_site_files_exist():
    required = [
        "preview.html",
        "index.html",
        ".nojekyll",
        "assets/site.css",
        "assets/site.js",
        "assets/site-data.js",
        "assets/preview-hero.png",
        "assets/social-preview.png",
        "assets/demo.gif",
    ]
    for relative in required:
        assert (ROOT / relative).is_file(), relative


def test_site_data_bundle():
    raw = (ROOT / "assets" / "site-data.js").read_text(encoding="utf-8")
    payload = json.loads(raw.split("window.EVIDENCE_DATA = ", 1)[1].rsplit(";", 1)[0])
    assert payload["generatedFrom"] == "results/tables/claims.csv"
    assert payload["total"] == 42
    assert len(payload["claims"]) == 42
    assert payload["verdictCounts"] == {
        "supported": 18,
        "partially_supported": 14,
        "unsupported": 10,
        "not_verifiable": 0,
    }
    assert all(claim["sourceCount"] >= 1 for claim in payload["claims"])


def test_preview_is_self_contained():
    text = (ROOT / "preview.html").read_text(encoding="utf-8")
    assert '<meta property="og:image" content="assets/social-preview.png">' in text
    assert '<meta name="twitter:card" content="summary_large_image">' in text
    assert '<script src="http' not in text
    assert '<link rel="stylesheet" href="http' not in text
    for target in re.findall(r'(?:src|href)="([^"#]+)"', text):
        if target.startswith(("http://", "https://", "data:", "mailto:")):
            continue
        assert (ROOT / target.split("?", 1)[0]).is_file(), target


def test_index_redirects_to_preview():
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'http-equiv="refresh"' in text
    assert "url=preview.html" in text


def test_readme_beginner_guide_and_voice():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## 🌱 Beginner guide — read this and you are a professional" in text
    assert "[🌱 Beginner guide](#-beginner-guide--read-this-and-you-are-a-professional)" in text
    assert "You will know more than most interview candidates." in text
    assert "Let's work this out in a step-by-step way to be sure we have the right answer." in text
    lower = text.lower()
    assert "donkey" not in lower
    assert "playwright" not in lower

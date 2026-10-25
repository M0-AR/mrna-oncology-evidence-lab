from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    preview = (ROOT / "preview.html").read_text(encoding="utf-8")
    for prefix in ("assets/", "results/", "paper/", "config/", "evidence/"):
        preview = preview.replace(f'"{prefix}', f'"../{prefix}')
    (DOCS / "preview.html").write_text(preview, encoding="utf-8")
    (DOCS / "index.html").write_text(
        (ROOT / "index.html").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print("wrote docs/preview.html, docs/index.html, docs/.nojekyll")


if __name__ == "__main__":
    main()

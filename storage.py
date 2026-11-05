from pathlib import Path
from config import SITEMAPS_DIR, RAW_DIR, PARSED_DIR, FILTERED_DIR
import json
import yaml

def ensure_dirs() -> None: 
    for directory in (SITEMAPS_DIR, RAW_DIR, PARSED_DIR, FILTERED_DIR):
        directory.mkdir(parents=True, exist_ok=True)

def slug_from_url(url: str) -> str: 
    return url.split("/")[-1]

def raw_path(slug: str) -> Path:
    return RAW_DIR / f"{slug}.html"

def is_already_fetched(slug: str) -> bool: 
    return raw_path(slug).exists()

def save_raw_html(slug: str, html: str) -> None: 
    raw_path(slug).write_text(html, encoding="utf-8")

def load_raw_html(slug: str) -> str: 
    return raw_path(slug).read_text(encoding="utf-8")

def save_json(path: Path, data) -> None: 
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_json(path: Path): 
    return (json.loads(path.read_text(encoding="utf-8")))

def load_cv(path: Path) -> dict: 
    return yaml.safe_load(path.read_text())

if __name__ == "__main__":
    ensure_dirs()

    slug = "test-offer"
    save_raw_html(slug, "<html>zażółć gęślą jaźń</html>")
    assert is_already_fetched(slug) is True
    assert load_raw_html(slug) == "<html>zażółć gęślą jaźń</html>"
    raw_path(slug).unlink()
    assert is_already_fetched(slug) is False

    json_path = PARSED_DIR / "test.json"
    save_json(json_path, {"city": "Dąbrowa Górnicza"})
    assert load_json(json_path) == {"city": "Dąbrowa Górnicza"}
    json_path.unlink()

    cv = load_cv(Path(__file__).parent / "cv.yaml")
    assert "Katowice" in cv["preferences"]["cities"]

    print("All passed")
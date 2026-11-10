"""Parse sitemap XML and offer HTML into plain data. No network access."""

import json
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
# justjoin.it appends an 8-character hash to some offer URLs, e.g. "...-data-093aeccd"
URL_HASH = re.compile(r"[0-9a-f]{8}")


def parse_sitemaps(xml: bytes) -> list[dict]:
    root = ET.fromstring(xml)
    offers = []
    for entry in root:
        loc = entry.find("sm:loc", SITEMAP_NS)
        lastmod = entry.find("sm:lastmod", SITEMAP_NS)
        offers.append(
            {
                "url": loc.text,
                "category": category_from_url(loc.text),
                "lastmod": lastmod.text,
            }
        )
    return offers


def category_from_url(url: str) -> str:
    parts = url.split("-")
    if URL_HASH.fullmatch(parts[-1]):
        return parts[-2]
    return parts[-1]


def parse_offer(html: str, url: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")

    # Soft 404: the active-jobs sitemap can still list expired offers.
    # The page returns HTTP 200 but shows "Offer expired" instead of the offer.
    if soup.find(string="Offer expired"):
        return None

    # TODO: return None for a field when its chip is missing instead of crashing
    json_ld = soup.find("script", type="application/ld+json")
    json_ld_data = json.loads(json_ld.string)
    seniority = (
        soup.find("svg", class_="lucide-graduation-cap")
        .parent.find_next_sibling()
        .get_text()
    )
    work_type = (
        soup.find("svg", class_="lucide-map-pinned")
        .parent.find_next_sibling()
        .get_text()
    )

    return {
        "url": url,
        "json_ld_data": json_ld_data,
        "seniority": seniority,
        "work_type": work_type,
        "city": city_from_json_ld(json_ld_data),
    }


def city_from_json_ld(json_ld_data: dict) -> str | None:
    location = json_ld_data.get("jobLocation")
    if isinstance(location, list):
        location = location[0] if location else None
    if not location:
        return None
    return location.get("address", {}).get("addressLocality")


if __name__ == "__main__":
    from config import RAW_DIR

    plain_url = "https://justjoin.it/job-offer/firma-data-engineer-krakow-data"
    assert category_from_url(plain_url) == "data"
    assert category_from_url(plain_url + "-093aeccd") == "data"

    sample = b"""<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://justjoin.it/job-offer/firma-python-developer-katowice-python</loc>
    <lastmod>2026-10-20T10:00:00+00:00</lastmod>
  </url>
</urlset>"""
    offers = parse_sitemaps(sample)
    assert offers[0]["category"] == "python"
    assert offers[0]["lastmod"] == "2026-10-20T10:00:00+00:00"

    raw_files = list(RAW_DIR.glob("*.html"))
    if raw_files:
        path = raw_files[0]
        html = path.read_text(encoding="utf-8")
        result = parse_offer(html, f"https://justjoin.it/job-offer/{path.stem}")
        if result is None:
            print("Offer expired")
        else:
            print(result["seniority"], result["work_type"], result["city"])
    else:
        print("No files in data/raw, skipping parse_offer check")

    print("All passed.")

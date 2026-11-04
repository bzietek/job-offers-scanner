# xml/html na dane
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import json


def parse_sitemaps(xml: bytes) -> list[dict]:
    root = ET.fromstring(xml)
    offers = []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    for entry in root:
        loc = entry.find("sm:loc", ns)
        lastmod = entry.find("sm:lastmod", ns)
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
    if re.fullmatch(r"[0-9a-f]{8}", parts[-1]):
        return parts[-2]
    return parts[-1]


def parse_offer(html: str, url: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")

    # Soft 404: the active-jobs sitemap can still list expired offers.
    # The page returns HTTP 200 but shows "Offer expired" instead of the offer
    if soup.find(string="Offer expired"):
        return None

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
    }


if __name__ == "__main__":
    from pathlib import Path

    # 1. category_from_url: adres bez kodu i z kodem
    print(
        category_from_url(
            "https://justjoin.it/job-offer/firma-data-engineer-krakow-data"
        )
    )  # data
    print(
        category_from_url(
            "https://justjoin.it/job-offer/firma-data-engineer-krakow-data-093aeccd"
        )
    )  # data

    # 2. parse_sitemaps na małym XML-u wpisanym w kod
    sample = b"""<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://justjoin.it/job-offer/firma-python-developer-katowice-python</loc>
    <lastmod>2026-10-20T10:00:00+00:00</lastmod>
  </url>
</urlset>"""
    print(parse_sitemaps(sample))

    # 3. parse_offer na pierwszym zapisanym pliku z data/raw
    raw_files = list(Path("data/raw").glob("*.html"))
    if not raw_files:
        print("Brak plików w data/raw")
    else:
        path = raw_files[0]
        html = path.read_text(encoding="utf-8")
        result = parse_offer(html, f"https://justjoin.it/job-offer/{path.stem}")
        if result is None:
            print("Oferta wygasła")
        else:
            print(result["seniority"], result["work_type"])

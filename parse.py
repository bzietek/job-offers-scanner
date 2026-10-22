#xml/html na dane
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import json

def parse_sitemaps(xml: bytes) -> list[dict]:
    root = ET.fromstring(xml)
    offers = []    
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    for url in root:
        job_category = category_from_url(url)
        lastmod = url.find('sm:lastmod', ns)
        loc = url.find('sm:loc', ns)
        offers.append({"url" : loc.text,
                       "category": job_category,
                       "lastmod": lastmod.text})        
    
    return offers

def category_from_url(url: str) -> str:
    parts = url.split("-")
    if re.fullmatch(r"[0-9a-f]{8}", parts[-1]):
        return parts[-2]
    return parts[-1]


def parse_offer(html: str, url: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")

    if soup.find(string="Offer expired"):
        return
    
    json_ld = soup.find("script", type="application/ld+json")
    description = json.loads(json_ld.string)
    seniority = soup.find("svg", class_="lucide-graduation-cap").parent.find_next_sibling().get_text()
    work_type = soup.find("svg", class_="lucide-map-pinned").parent.find_next_sibling().get_text()
    
    return {
        "url" : url,
        "description" : description,
        "seniority" : seniority,
        "work_type": work_type
    }
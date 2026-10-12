import xml.etree.ElementTree as ET
import requests
import re
import json
from datetime import datetime
from collections import Counter


r = requests.get('https://justjoin.it/sitemaps/active-jobs/part0.xml')
root= ET.fromstring(r.content)
offers = []
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

for url in root:
    loc = url.find('sm:loc', ns)
    lastmod = url.find('sm:lastmod', ns)
    parts = loc.text.split('-')

    if re.fullmatch(r"[0-9a-f]{8}", parts[-1]):
        job_category = parts[-2]
    else: 
        job_category = parts[-1]
    offers.append({"url" : loc.text,
                    "category": job_category,
                    "lastmod": lastmod.text})


# TODO: it can be done in one line
def count_offers_per_category(offers):
    categories = []
    for offer in offers:
        categories.append(offer["category"])
    return Counter(categories)



print(count_offers_per_category(offers))
with open(f"./data/offers_{datetime.today().strftime('%Y-%m-%d')}.json", "w", encoding="utf-8") as f:
    json.dump(offers, f, ensure_ascii=False, indent=2)
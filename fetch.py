import xml.etree.ElementTree as ET
import requests
import re
import json
from datetime import datetime
from collections import Counter
import time
from http import HTTPStatus
from requests.exceptions import HTTPError

initial_url = "https://justjoin.it/sitemaps/active-jobs/part0.xml"
retries = 3
retry_codes = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]

for n in range(retries):
    try:
        response = requests.get(initial_url)
        response.raise_for_status()

        break

    except HTTPError as exc:
        code = exc.response.status_code

        if code in retry_codes:
            time.sleep(n)
            continue

        raise

root= ET.fromstring(response.content)
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

    if job_category in ['data', 'analytics', 'ai', 'python', 'other']:
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
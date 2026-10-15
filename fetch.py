import xml.etree.ElementTree as ET
import requests
import re
import json
from datetime import datetime
from collections import Counter
import time
from http import HTTPStatus
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup

sitemap_url = "https://justjoin.it/sitemaps/active-jobs/part0.xml"
retries = 3
retry_codes = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]

# TODO: it needs adjustments 
for n in range(retries):
    try:
        response = requests.get(sitemap_url)
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
    parts = loc.text.split('-')
    lastmod = url.find('sm:lastmod', ns)

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



# print(count_offers_per_category(offers))
with open(f"./data/sitemaps/offers_{datetime.today().strftime('%Y-%m-%d')}.json", "w", encoding="utf-8") as f:
    json.dump(offers, f, ensure_ascii=False, indent=2)


USER_AGENT = "job-offers-scanner/0.1 (+https://github.com/bzietek/job-offers-scanner)"
headers = {"User-Agent" : USER_AGENT}

single_offers = []
# htmls = []
for offer in offers[:10]:
    offer_response = requests.get(offer["url"], headers=headers)
    html = offer_response.text
    file_title = offer["url"].split("/")[-1]

    with open(f"./data/raw/{file_title}.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    if soup.find(string="Offer expired"):
        continue
    json_ld = soup.find("script", type="application/ld+json")
    description = json.loads(json_ld.string)
    seniority = soup.find("svg", class_="lucide-graduation-cap").parent.find_next_sibling().get_text()
    work_type = soup.find("svg", class_="lucide-map-pinned").parent.find_next_sibling().get_text()
    # TODO: city = soup.find()

    # single_offers.append({
    #     "url" : offer["url"],
    #     "description" : description,
    #     "seniority" : seniority,
    #     "work_type": work_type
    #     # TODO: "city" : city
    # })

    single_offer = ({
        "url" : offer["url"],
        "description" : description,
        "seniority" : seniority,
        "work_type": work_type
        # TODO: "city" : city
    })

    with open(f"./data/parsed/{file_title}.json", "w", encoding="utf-8") as f:
        json.dump(single_offer, f, ensure_ascii=False, indent=2)
  




filtered_offers = []
for url in root:
    loc = url.find('sm:loc', ns)
    parts = loc.text.split('-')
    if ["senior", "manager", "lead", "architect"] in parts:
        pass

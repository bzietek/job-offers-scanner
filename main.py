from datetime import date

import requests

from config import BASE_DIR, FILTERED_DIR, PARSED_DIR, SITEMAPS_DIR
from fetch import create_session, fetch_offer_html, fetch_sitemap
from filters import passes_cheap_filters, passes_content_filters
from parse import parse_offer, parse_sitemaps
from storage import (
    ensure_dirs,
    is_already_fetched,
    load_cv,
    load_raw_html,
    save_json,
    save_raw_html,
    slug_from_url,
)

MAX_OFFERS = 10  # limit while developing; None = no limit


def main() -> None:
    # 1. Setup
    ensure_dirs()
    session = create_session()
    cv = load_cv(BASE_DIR / "cv.yaml")
    cities = set(cv["preferences"]["cities"])

    # 2. Save sitemap snapshot
    sitemap_xml = fetch_sitemap(session)
    offers = parse_sitemaps(sitemap_xml)
    save_json(SITEMAPS_DIR / f"{date.today().isoformat()}.json", offers)

    # 3. Cheap filters and new offers only
    candidates = [offer for offer in offers if passes_cheap_filters(offer)]
    new_offers = [
        offer
        for offer in candidates
        if not is_already_fetched(slug_from_url(offer["url"]))
    ]
    to_fetch = new_offers[:MAX_OFFERS]

    # 4. Fetch and save raw HTML
    fetched = []
    failed = []
    for offer in to_fetch:
        slug = slug_from_url(offer["url"])
        try:
            html = fetch_offer_html(session, offer["url"])
            save_raw_html(slug, html)
            fetched.append(offer)
        except (requests.RequestException, RuntimeError) as exc:
            print(f"Failed to fetch {offer['url']}: {exc}")
            failed.append(offer)

    # 5. Parse saved HTML
    parsed = []
    expired = []
    for offer in fetched:
        slug = slug_from_url(offer["url"])
        html = load_raw_html(slug)
        parsed_offer = parse_offer(html, offer["url"])
        if parsed_offer is None:
            expired.append(offer)
        else:
            parsed.append(parsed_offer)
            save_json(PARSED_DIR / f"{slug}.json", parsed_offer)

    # 6. Content filters
    filtered = []
    for parsed_offer in parsed:
        if passes_content_filters(parsed_offer, cities):
            slug = slug_from_url(parse_offer["url"])
            save_json(FILTERED_DIR / f"{slug}.json", parsed_offer)
            filtered.append(parsed_offer)

    # 7. Summary
    print(f"{'Offers in sitemap:':<26}{len(offers)}")
    print(f"{'After cheap filters:':<26}{len(candidates)}")
    print(f"{'New (not fetched yet):':<26}{len(new_offers)}")
    print(f"{'To fetch (limit):':<26}{len(to_fetch)}")
    print(f"{'Fetched / failed:':<26}{len(fetched)} / {len(failed)}")
    print(f"{'Expired:':<26}{len(expired)}")
    print(f"{'Parsed:':<26}{len(parsed)}")
    print(f"{'Passed content filters:':<26}{len(filtered)}")


if __name__ == "__main__":
    main()

import requests
from datetime import date
from config import BASE_DIR, SITEMAPS_DIR, PARSED_DIR, FILTERED_DIR
from fetch import create_session, fetch_sitemap, fetch_offer_html
from parse import parse_sitemaps, parse_offer
from filters import passes_cheap_filters, passes_content_filters
from storage import (ensure_dirs, slug_from_url, is_already_fetched,
                     save_raw_html, load_raw_html, save_json, load_cv)

MAX_OFFERS = 10  # tests


def main() -> None:
    # 1. Setup
    ensure_dirs()
    session = create_session()
    cv = load_cv(BASE_DIR / "cv.yaml")
    cities = set(cv["preferences"]["cities"])
    
    # 2. Save sitemap snapshots
    sitemap_xml = fetch_sitemap(session)
    offers = parse_sitemaps(sitemap_xml)
    save_json(SITEMAPS_DIR / f"{date.today().isoformat()}.json", offers)

    # 3. Cheap filters and new offers only
    candidates = [offer for offer in offers if passes_cheap_filters(offer)]
    new_offers = [offer for offer in candidates
    if not is_already_fetched(slug_from_url(offer["url"]))]
    to_fetch = new_offers[:MAX_OFFERS]
    print(len(offers), len(candidates), len(new_offers), len(to_fetch))

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

    print(len(fetched), len(failed))

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

if __name__ == "__main__":
    main()
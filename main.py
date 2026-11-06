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
    to_fetch = [offer for offer in candidates if not is_already_fetched(slug_from_url(offer["url"]))][:MAX_OFFERS]
    print(len(offers), len(candidates), len(to_fetch))
   
if __name__ == "__main__":
    main()
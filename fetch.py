"""HTTP requests: session, retries, sitemap and offer pages."""

import time

import requests

from config import (
    REQUEST_DELAY_S,
    REQUEST_TIMEOUT_S,
    RETRY_CODES,
    SITEMAP_URL,
    USER_AGENT,
)


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def get_with_retry(
    session: requests.Session, url: str, retries: int = 3
) -> requests.Response:
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT_S)
            response.raise_for_status()
            return response
        except requests.HTTPError as exc:
            if exc.response.status_code not in RETRY_CODES:
                raise
        except (requests.ConnectionError, requests.Timeout):
            pass

        if attempt < retries - 1:
            time.sleep(2**attempt)

    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts.")


def fetch_sitemap(session: requests.Session) -> bytes:
    response = get_with_retry(session, SITEMAP_URL)
    return response.content


def fetch_offer_html(session: requests.Session, url: str) -> str:
    response = get_with_retry(session, url)
    time.sleep(REQUEST_DELAY_S)
    return response.text


if __name__ == "__main__":
    from parse import parse_sitemaps

    session = create_session()

    response = get_with_retry(session, "https://httpbin.org/status/200")
    assert response.status_code == 200

    try:
        get_with_retry(session, "https://httpbin.org/status/404")
    except requests.HTTPError:
        pass
    else:
        raise AssertionError("Expected HTTPError for 404")

    try:
        get_with_retry(session, "https://httpbin.org/status/503")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError for 503")

    offers = parse_sitemaps(fetch_sitemap(session))
    assert len(offers) > 0
    print(len(offers), offers[0])

    print("All passed.")

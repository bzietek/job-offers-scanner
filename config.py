# constants
from pathlib import Path
from http import HTTPStatus

SITEMAP_URL = "https://justjoin.it/sitemaps/active-jobs/part0.xml"
USER_AGENT = "job-offers-scanner/0.1 (+https://github.com/bzietek/job-offers-scanner)"
CATEGORIES = {"data", "analytics", "ai", "python"}
EXCLUDED_TITLE_WORDS = {"senior", "lead", "manager", "architect"}
ACCEPTED_SENIORITY = {"Junior", "Mid"}
REQUEST_DELAY_S = 2
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SITEMAPS_DIR = DATA_DIR / "sitemaps"
RAW_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
FILTERED_DIR = DATA_DIR / "filtered"
RETRY_CODES = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]

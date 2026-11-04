# filtry
from config import CATEGORIES, EXCLUDED_TITLE_WORDS, ACCEPTED_SENIORITY


def passes_cheap_filters(offer: dict) -> bool:
    slug_words = set(offer["url"].split("/")[-1].split("-"))
    is_target_category = offer["category"] in CATEGORIES
    has_excluded_word = bool(slug_words & EXCLUDED_TITLE_WORDS)
    return is_target_category and not has_excluded_word


def passes_content_filters(offer: dict, cities: set[str]) -> bool:
    is_accepted_seniority = offer["seniority"] in ACCEPTED_SENIORITY
    is_remote = offer["work_type"] == "Remote"
    is_nearby = offer["city"] in cities
    return is_accepted_seniority and (is_remote or is_nearby)


if __name__ == "__main__":
    cities = {"Katowice", "Sosnowiec", "Gliwice"}

    # passes_content_filters
    senior_nearby = {"seniority": "Senior", "work_type": "Hybrid", "city": "Katowice"}
    assert passes_content_filters(senior_nearby, cities) is False

    junior_hybrid_far = {"seniority": "Junior", "work_type": "Hybrid", "city": "Poznań"}
    assert passes_content_filters(junior_hybrid_far, cities) is False

    junior_remote_far = {
        "seniority": "Junior",
        "work_type": "Remote",
        "city": "Warszawa",
    }
    assert passes_content_filters(junior_remote_far, cities) is True

    junior_hybrid_nearby = {
        "seniority": "Junior",
        "work_type": "Hybrid",
        "city": "Katowice",
    }
    assert passes_content_filters(junior_hybrid_nearby, cities) is True

    # passes_cheap_filters
    senior_in_title = {
        "url": "https://justjoin.it/job-offer/firma-senior-data-engineer-katowice-data",
        "category": "data",
    }
    assert passes_cheap_filters(senior_in_title) is False

    wrong_category = {
        "url": "https://justjoin.it/job-offer/firma-java-developer-katowice-java",
        "category": "java",
    }
    assert passes_cheap_filters(wrong_category) is False

    valid_junior_offer = {
        "url": "https://justjoin.it/job-offer/firma-junior-data-analyst-katowice-data",
        "category": "data",
    }
    assert passes_cheap_filters(valid_junior_offer) is True

    print("All passed")

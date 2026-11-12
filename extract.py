"""Extract structured requirements from offer descriptions with an LLM."""

import json

from bs4 import BeautifulSoup
from openai import OpenAI
from pydantic import BaseModel

from config import LLM_MODEL


class Skill(BaseModel):
    name: str
    category: str
    level: str | None
    years: int | None


class OfferRequirements(BaseModel):
    required_skills: list[Skill]
    nice_to_have_skills: list[Skill]
    years_of_experience: int | None
    languages: list[str]
    responsibilities_summary: str
    project_summary: str | None


SYSTEM_PROMPT = (
    "You extract requirements from job offers. "
    "Use only information stated in the offer. "
    "If something is not mentioned, return null or an empty list. Do not guess."
)


def extract_requirements(
    client: OpenAI, description_html: str
) -> tuple[OfferRequirements, int]:
    description = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)
    response = client.responses.parse(
        model=LLM_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": description},
        ],
        text_format=OfferRequirements,
    )
    return response.output_parsed, response.usage.total_tokens


if __name__ == "__main__":
    from dotenv import load_dotenv

    from config import PARSED_DIR
    from storage import load_json

    load_dotenv()
    client = OpenAI()

    offer_path = next(PARSED_DIR.glob("*.json"))  # first parsed offer on this machine
    offer = load_json(offer_path)
    requirements, tokens = extract_requirements(client, offer["json_ld_data"]["description"])
    print(offer_path.stem)
    print(json.dumps(requirements.model_dump(), indent=2, ensure_ascii=False))
    print(f"Tokens used: {tokens}")
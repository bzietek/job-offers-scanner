"""Extract structured requirements from offer descriptions with an LLM."""

import json
from typing import Literal

from bs4 import BeautifulSoup
from openai import OpenAI
from pydantic import BaseModel

from config import LLM_MODEL

Category = Literal["programming language", "library", "tool", "concept", "method"]
Level = Literal["basic", "intermediate", "advanced"]


class Skill(BaseModel):
    name: str
    category: Category
    level: Level | None
    years: int | None


class Language(BaseModel):
    name: str
    level: str | None
    required: bool


class OfferRequirements(BaseModel):
    required_skills: list[Skill]
    nice_to_have_skills: list[Skill]
    years_of_experience: int | None
    education: str | None
    languages: list[Language]
    responsibilities_summary: str
    project_summary: str | None


SYSTEM_PROMPT = """You extract requirements from a job offer.

Rules:
- Use only information stated in the offer. If something is not mentioned,
  return null or an empty list. Do not guess.
- A skill is a short, standard name of a technology or concept, for example
  "Python", "Azure", "machine learning". Never a full sentence.
- Do not include soft skills or management skills (communication, leadership,
  problem solving, teamwork, building or managing teams).
- Put degree requirements in "education", not in skills.
- Categories: Python packages and frameworks (e.g. PyTorch, pandas) are "library";
  cloud platforms, databases and other software are "tool"; Python or SQL are
  "programming language"; fields like statistics or deep learning are "concept".
- Level: set it only if the offer states it explicitly, mapped to basic,
  intermediate or advanced.
- Languages: one entry per language. "level" is the level stated in the offer
  (for example "C1", "B2", "fluent"), otherwise null. "required" is false when
  the offer says the language is optional or a plus.
- Write all values in English.
- required is true by default; set it to false only for languages the offer explicitly calls optional or a plus
"""


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
        reasoning={"effort": "medium"},
    )
    return response.output_parsed, response.usage.total_tokens


if __name__ == "__main__":
    from dotenv import load_dotenv

    from config import PARSED_DIR
    from storage import load_json

    load_dotenv()
    client = OpenAI()

    total_tokens = 0
    for offer_path in sorted(PARSED_DIR.glob("*.json"))[:3]:
        offer = load_json(offer_path)
        requirements, tokens = extract_requirements(
            client, offer["json_ld_data"]["description"]
        )
        total_tokens += tokens
        print(offer_path.stem)
        # print(json.dumps(requirements.model_dump(), indent=2, ensure_ascii=False))
        print([skill.name for skill in requirements.required_skills])
        print(requirements.languages)
        print(f"Tokens used: {tokens}\n")

    print(f"Total tokens: {total_tokens}")
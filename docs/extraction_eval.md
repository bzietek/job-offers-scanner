# Extraction evaluation

Manual check of the LLM extraction against the original offers on justjoin.it.
Model in all runs: `gpt-5-mini`, structured outputs with a Pydantic schema.

Error types:
- **missing**: a requirement is in the offer but was not extracted
- **invented**: extracted, but not a requirement in the offer (e.g. taken from the company description)
- **wrong list**: required vs nice-to-have mixed up
- **wrong value**: e.g. wrong category, level or language flag

Test offers:
- **game economy**: bluebinary-io-game-economy-designer-wroclaw-analytics (Polish, very senior role)
- **cloudatus (Poznań / Rzeszów)**: the same Data Scientist / ML Engineer offer published in two cities

## Prompt and schema versions

| Version | Changes |
|---|---|
| v1 | Free-text category and level, languages as strings, three-sentence prompt |
| v2 | `Literal` categories and levels, `education` field, rules: short skill names, no soft skills, English values |
| v3 | Languages as objects (`name`, `level`, `required`), management skills excluded |
| v4 | `required` is true by default for languages; extract only from requirements, not from the company description |

## Results

| Run | Prompt | Reasoning effort | Tokens (3 offers) |
|---|---|---|---|
| 0 | v1 | default | 4 079 (1 offer: P&G Data Scientist) |
| 1 | v2 | low | 7 561 |
| 2 | v3 | low | 8 182 |
| 3 | v3 | medium | 15 391 |
| 4 | v4 | medium | 13 562 |

### Run 0: v1 (P&G Data Scientist, not compared with the original)
- Categories as free text ("Technical", "Cloud Infrastructure", "Cloud / Infrastructure")
- Sentences extracted as skills ("Production-grade data science / algorithmically enabled applications")
- Soft skills and the degree requirement mixed into skills
- 1 536 of 2 691 output tokens were reasoning tokens

### Run 1: v2, low
- **cloudatus (both)**: missing confidence intervals, significance tests, survival analysis; German listed like English (schema could not mark it as optional)
- **cloudatus**: the two copies of the same offer gave different skill names ("Statistics" vs "statistics", "data analysis" vs "data science")
- **game economy**: "building teams" extracted (management skill)

### Run 2: v3, low
- **cloudatus Poznań**: R, MLOps and ML pipelines in required (wrong list: R is "a plus", MLOps is "desirable"); English `required: false` (wrong value)
- **cloudatus Rzeszów**: MLOps got level "basic" (invented); vague items "data-science libraries", "model deployment / MLOps practices"; English `required: false`
- **cloudatus (both)**: statistics details still missing
- **game economy**: "building teams" still extracted despite the rule

### Run 3: v3, medium
- **cloudatus Poznań**: statistics details extracted; R and MLOps correctly nice-to-have; IaaS, PaaS, SaaS invented from the company description
- **cloudatus Rzeszów**: survival analysis and significance testing extracted, confidence intervals missing; English `required: false`
- **game economy**: "building teams" gone; Jira, Asana, Slack correctly nice-to-have; English C1 `required: false` (wrong value)
- Categories "concept" vs "method" assigned inconsistently (the same algorithms are "concept" in one copy and "method" in the other)

### Run 4: v4, medium
- **languages**: correct in all three offers (English required, German optional)
- **cloudatus Poznań**: IaaS, PaaS, SaaS gone; statistics details extracted
- **cloudatus Rzeszów**: statistics details missing again (only "statistical analysis"); "data-science libraries" still extracted
- **game economy**: Jira, Asana, Slack, Google Workspace in required (wrong list: the offer lists them under "Mile widziane"); loot tables, progression loops, currency design and KPI analysis taken from the responsibilities section into required skills

## Findings

1. **Reasoning effort:** medium fixed most "missing" and "wrong list" errors from low, for about 1.7–1.9× more tokens (about 0.8 cent per offer at list prices, free within the daily data-sharing quota). Chosen: medium.
2. **The model is not deterministic:** the two copies of the cloudatus offer never gave the same result. Duplicates should be removed before the LLM step; skill names should be normalised in code before matching.
3. **Rules that the model ignored** (e.g. "building teams" in run 2) are better enforced in code than in the prompt.
4. **Responsibilities vs requirements:** the model often turns tasks into required skills. Open decision: either allow it (tasks show what is needed) or keep required skills strictly from the requirements section.
5. **Seniority is not captured:** the game economy offer asks for "very large experience" and team management, but `years_of_experience` is null because no number is given.

## Next steps

- Deduplicate offers (company + title from JSON-LD) before extraction
- Normalise skill names in code (casefold, synonym map)
- Decide on responsibilities vs requirements and on merging "concept" and "method"
- Save extraction results to `data/extracted/` and add the step to `main.py`

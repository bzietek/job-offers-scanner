# Design: job-offers-scanner

Status: work in progress. Last update: November 2026.

## Problem

Going through job offers by hand takes a lot of time, and the filters on job boards are not reliable: companies label offers differently, so "mid" at one company is not the same as "mid" at another. Most offers are also for senior roles.

Scale (justjoin.it):
- 14.10.2026, offers in my categories: data 1055, analytics 982, ai 584, python 512, other 501
- November 2026: about 11,000 offers in the sitemap, about 1,750 left after the cheap filters

## MVP

- One source: justjoin.it, through the sitemap it publishes.
- Categories: data, analytics, ai, python.
- Pipeline: fetch, filter, parse and save offers (done), then extract requirements with an LLM and match offers to my CV (next).
- I run it manually once a day (`python main.py`).

## Out of scope (for now)

- Tailoring my CV to a selected offer
- More job boards
- Dashboard

Planned after matching works: automatic daily runs and notifications about new, well-matched offers.

## Pipeline: input and output of each step

| Step | Input | Output |
|---|---|---|
| 1. Setup | `cv.yaml` | data folders, HTTP session, set of accepted cities |
| 2. Sitemap | sitemap URL | list of `{url, category, lastmod}`, saved to `data/sitemaps/<date>.json` |
| 3. Cheap filters | sitemap list | offers in target categories, without excluded title words, not fetched yet |
| 4. Fetch | offer URLs | raw HTML in `data/raw/<slug>.html` |
| 5. Parse | raw HTML | `{url, json_ld_data, seniority, work_type, city}` in `data/parsed/` |
| 6. Content filters | parsed offers, cities | offers that pass, in `data/filtered/` |
| 7. Summary | all lists | funnel counts printed to the console |
| 8. LLM extraction (next) | offer description | structured requirements |
| 9. Matching (next) | requirements, `cv.yaml` | match score per offer |

## Data

- **CV:** `cv.yaml`, written by hand (skills with level and category, preferred cities). Not in the repository; `cv.yaml.example` shows the format.
- **Sitemap:** URL, last modification date; the category is the last part of the URL (or the one before an 8-character hash).
- **Offer page:** JSON-LD (title, company, location, full description as one long string) and "chips" with seniority, work mode and contract type.
- **Tech stack on the page:** the author pins technologies with a 1–5 scale. From my experience this scale doesn't tell the whole story, so requirements will come from the description, analysed by an LLM. The tech stack list can still be used to check the extraction.
- **Storage layers:** `sitemaps/` and `raw/` are source data and are never changed; `parsed/` and `filtered/` are derived and can be rebuilt from `raw/` at any time.

## AI (next step)

- **Extraction:** an LLM turns the description into structured fields, for example required and nice-to-have technologies, years of experience, languages, responsibilities. Output validated against a schema.
- **Matching:** start with the simplest approach and compare others on the benchmark. Candidates: overlap of skills, embedding similarity, LLM as a judge.

## Benchmark

- **Matching:** label about 30 offers by hand as match or no match, with both kinds included. Metric: how many of the top 5 offers I would actually apply to.
- **Extraction:** check field by field on 20–30 offers how often the LLM is wrong.

## Decisions

- **Sitemap instead of the search page or API.** The sitemap is allowed in robots.txt and lists all active offers; `/api/` is disallowed.
- **Cheap filters before downloading.** Rules on the URL cost nothing, downloading costs time and server load.
- **Raw data first.** Pages are saved before parsing, so filters and the parser can change without downloading again.
- **Only new offers are downloaded.** An offer counts as fetched when its raw HTML file exists.
- **Category "other" dropped.** Only some of these offers met my expectations.
- **Seniority and work mode from page chips,** found by icon classes (`lucide-graduation-cap`, `lucide-map-pinned`), not by generated CSS classes that change with every deployment.
- **Cities as a fixed list for the MVP.** Remote offers pass regardless of city.
- **Polite fetching:** own User-Agent, delay between requests, timeouts, retries with exponential backoff.

## What can go wrong

- Expired offers in the sitemap: the page returns HTTP 200 but says "Offer expired" (soft 404). Handled: such offers are skipped.
- The page structure changes and a chip disappears: the parser currently crashes. TODO: return `None` for missing fields and count how often it happens.
- Encoding: the sitemap starts with a UTF-8 BOM. Handled by parsing bytes instead of text.
- The same offer in several cities gets a URL with a hash at the end.
- The sitemap may be split into more parts (`part1.xml`) when it exceeds 50,000 URLs. Currently only `part0.xml` is read.
- Dates without a time zone: a cloud server running in UTC may save the sitemap snapshot with yesterday's date.
- Later: the LLM may invent requirements that are not in the offer.

## Cost

- Now: free (only HTTP requests).
- LLM: about (new offers per day) × (tokens per offer) × (price per token). The first run covers about 1,750 offers, later runs only new ones. Options: paid API with a spending limit, a free tier, or a local model. Decision pending.

## Open questions

- Skill name variants in offers, for example "sklearn" vs "scikit-learn": how to normalise them?
- Offers without a seniority chip: reject them (current behaviour) or send them to the LLM?
- JSON-LD has only one city, while an offer can have more; the other cities are probably in the HTML.
- Comparing locations by city name is not convenient; geocoding city names once and using distance could work better.
- Which LLM provider and model, and how to keep the cost under control?

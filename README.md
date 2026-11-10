# job-offers-scanner

A Python pipeline that collects job offers from justjoin.it, filters them against my CV and preferences, and keeps the ones worth a closer look.

## Why

I built this tool so I don't have to go through every job offer by hand. Job boards have filters, but companies label their offers differently: a "mid" role at one company is not the same as a "mid" role at another. I also wanted to practise building a complete data pipeline on real data instead of a ready-made dataset.

## How it works

1. **Load my CV** from a hand-written `cv.yaml` file with my skills and preferred cities.
2. **Fetch the sitemap** that justjoin.it publishes, which lists all active offers.
3. **Parse the sitemap** into a list of offers, each with its URL, category (taken from the URL) and last modification date. The full list is saved to `data/sitemaps/`.
4. **Cheap filters**, applied before any page is downloaded:
   - keep only the categories I'm interested in (data, analytics, AI, Python),
   - drop offers with words like "senior", "lead" or "architect" in the title.
5. **Skip offers that are already downloaded**, so every run only fetches new ones.
6. **Download the offer pages** and save the raw HTML to `data/raw/`.
7. **Parse each page** into a record with the URL, structured offer data (JSON-LD, including the full description), seniority, work mode (remote, hybrid or office) and city. Records are saved to `data/parsed/`.
8. **Content filters**:
   - seniority must be junior or mid,
   - the job must be remote, or the office must be in one of the cities near me.
9. **Save the offers that pass** to `data/filtered/` and print a summary of the whole funnel.

A typical run (November 2026): about 11,000 offers in the sitemap, about 1,750 after the cheap filters.

## Design notes

- **Raw data first.** Every downloaded page is saved before it is parsed or filtered, so I can change the filters or fix the parser and re-run them offline.
- **Cheap filters first.** Rules on the URL cost nothing, downloading a page costs time and server load, so the cheap rules run first.
- **Incremental runs.** An offer is downloaded only once; re-running the pipeline does not fetch it again.
- **Polite scraping.** The pipeline uses only pages allowed by robots.txt, identifies itself with its own User-Agent, waits between requests, and retries failed requests with timeouts and exponential backoff.

More details and open questions: [docs/design.md](docs/design.md).

## Project structure

```
config.py    constants: URLs, filter rules, data paths
fetch.py     HTTP: session, retries with backoff, sitemap and offer pages
parse.py     XML and HTML into data: sitemap entries, offer fields, city
filters.py   rules: cheap filters on sitemap data, content filters on parsed offers
storage.py   disk: folders, raw HTML, JSON files, CV
main.py      runs the pipeline step by step and prints the summary
data/        sitemaps/, raw/, parsed/, filtered/ (not in the repository)
```

## Setup and usage

Requires Python 3.10 or newer.

```
git clone https://github.com/bzietek/job-offers-scanner.git
cd job-offers-scanner
pip install -r requirements.txt
```

Copy `cv.yaml.example` to `cv.yaml` and fill in your own data, then run:

```
python main.py
```

While developing, `MAX_OFFERS` in `main.py` limits how many offer pages are downloaded in one run. Set it to `None` to download all new offers.

Development tools and module self-tests:

```
pip install -r requirements-dev.txt
ruff check .
python parse.py
python filters.py
python storage.py
python fetch.py    # needs an internet connection
```

## Status and next steps

Work in progress. Fetching, parsing and filtering work; next steps:

- analyse offer descriptions with an LLM to extract requirements,
- match offers to my CV and measure the matching on a hand-labelled set of offers,
- send notifications about new, well-matched offers,
- tailor my CV to a selected offer, using only facts from my CV,
- a dashboard with the results and job market statistics.

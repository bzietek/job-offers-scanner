WIP
## Problem
How many offers are opened, in what category
example: offers in preferred categories on 14.10.2026 'data': 1055, 'analytics': 982, 'ai': 584, 'python': 512, 'other': 501

## MVP
Offers are fetched from justjoin.it through sitemap. Currently I'm focusing on [data, analytics, ai, python, other] categories.
For now, I'm manually starting the fetching everyday around 10:00 am CEST.

## Out of scope
Features in the future: automatically generating CV based on best offer, more sites to fetch offers from, dashboard/notifications

## Input / Output
Fetch sitemap
Input: sitemap index URL, job offer URL
Output: list of {url, category, lastmod}, JSON-LD block from offer

## Data
CV file manually written
justjoin.it gives author of the offer an option to pin technology/skill to an offer with 1-5 scale. From my own experience, this scale doesn't tell whole story, it is still better to fetch information from description using LLM.

## AI


## Benchmark 
I will manually match 30 job offers as matching and use it as testing data set.

## What can go wrong?
offer can be in sitemap even though it expired


## Cost

## Open questions
offers can have for example sklearn instead of scikit-learn 
category 'other' is problematic - only some of them meet my expectations
it would be better to filter them through seniority, as most of the offers are for senior/experts/leads, but not all urls have seniority in them
JSON-LD blocks have "description" : "" with big string of whole offer as a string - it will probably has to be analyzed bo LLM?
how to compare job location with my location? comparing city names is not convenient 
JSON-LD has only one city, when offer can contain more 
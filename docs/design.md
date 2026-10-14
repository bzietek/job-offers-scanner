WIP
## Problem
How many new offers appear every day, in what category
example: offers in preferred categories on 14.10.2026 'data': 1055, 'analytics': 982, 'ai': 584, 'python': 512, 'other': 501

## MVP
Offers are fetched from justjoin.it through sitemap. Currently I'm focusing on [data, analytics, ai, python, other] categories.
For now, I'm manually starting the fetching everyday around 10:00 am CEST.

## Out of scope
Features in the future: automatically generating CV based on best offer, more sites to fetch offers from, dashboard/notifications

## Input / Output
Fetch sitemap
Input: sitemap index URL
Output: list of {url, category, lastmod}

## Data
CV file manually written

## AI


## Benchmark 
I will manually match 30 job offers as matching and use it as testing data set.

## What can go wrong?

## Cost

## Open questions
offers can have for example sklearn instead of scikit-learn 
category 'other' is problematic - only some of them meet my expectations
it would be better to filter them through seniority, as most of the offers are for senior/experts/leads, but not all urls have seniority in them
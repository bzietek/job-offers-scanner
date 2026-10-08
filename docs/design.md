## Problem
The job market for junior-level roles is tough. As I'm trying to get the job, I'll need something to automate it. The idea is to check new offers everyday, get qualifications from them and match them with my CV. Then, I'll get notification with best matches.

## MVP
In the beggining, I will automaticaly analyze the offers, match them with my CV and notify me with the best results. In the future I would like to automatically redesign my CV to match the offers. I would like to add more job portals and nice dashboard.

## Input / Output
I will take job offers from justjoin.it, analyze them, match them with my CV by AI and give me the notification with best matches.

## Data
I'll keep the data localy on my PC. I'm requesting GET from justjoin.it, extracting urls, job category and date of posting. Then, I'm saving them into json file with the date of extracting.

## AI
LLMs will take information from offers, and ML will match them with my CV.

## Benchmark
I will manually match 30 job offers as matching and use it as testing data set.

## What can go wrong?
The model might not work precisly, as the training set will be small.

## Cost
There is no cost, only learning through developing.
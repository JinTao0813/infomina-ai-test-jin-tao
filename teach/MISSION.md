# Learning Goal: Defend the Location Entropy Solution End to End

## Why this guide exists
I want to explain the full submitted solution in my own words: the entropy calculation, data checks, analysis, findings, product reasoning, generated case-study site, deterministic Discovery Mode prototype, and their limits—not memorize polished answers.

## What I should be able to do
- Tell the end-to-end story in two minutes without opening the code.
- Work through raw and normalized Shannon entropy with a small example.
- Explain what the loader, metric function, tests, notebook, exporter, candidate generator, API, ranker, and frontend each contribute.
- Derive the prototype's applied-discovery and candidate-score calculations with a worked example.
- Explain why profile entropy, aggregate candidate novelty, and category familiarity are different signals.
- Give a straightforward reason for important choices and acknowledge weak spots.
- Answer follow-up questions without presenting historical check-ins as complete mobility, the prototype as learned, or its rankings as validated.

## How to use it
- Keep all study material under `teach/`.
- Work through short lessons, then answer the prompts aloud before opening the model answer.
- Return to weak topics after a break; rereading alone is not enough.

## What it does not cover
- Rebuilding the submission, training a recommender, or claiming the prototype is production-ready.
- General data-science interview preparation unrelated to this project.
- Information theory beyond what is needed here.

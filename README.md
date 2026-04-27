# Trial Alerts

Daily ntfy push notifications when new clinical trials open on [ClinicalTrials.gov](https://clinicaltrials.gov) for specific conditions.

## What it does

Once a day at 7 AM Pacific, the GitHub Actions workflow queries ClinicalTrials.gov for trials matching each condition in `check_trials.py` that are either `RECRUITING` or `NOT_YET_RECRUITING`. New trials (ones not in `seen.json` from prior runs) trigger a single ntfy notification with a click-through to the study record.

Currently watching:

- Chronic Urticaria
- Parkinson's Disease

To add a condition, append an entry to the `CONDITIONS` list in `check_trials.py`:

```python
{
    "name": "Display name",
    "query": "search term",
    "key": "stable_key_for_seen.json",
},
```

## Setup

1. Fork or clone this repo.
2. Add an `NTFY_TOPIC` secret to the GitHub repo (your ntfy topic — pick something hard to guess; ntfy is open).
3. Subscribe to that topic in the [ntfy app](https://ntfy.sh/) on your phone.

The workflow commits `seen.json` back to the repo so you only get notified once per trial.

## Stack

- Python 3.12 (stdlib + `requests`)
- GitHub Actions cron (runs free)
- ntfy.sh for push notifications (free, no account)
- ClinicalTrials.gov API v2 (free, no key)

## Run locally

```sh
NTFY_TOPIC=your-topic python3 check_trials.py
```

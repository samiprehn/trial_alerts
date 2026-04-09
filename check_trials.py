import requests
import json
import os

NTFY_TOPIC = os.environ['NTFY_TOPIC']
SEEN_FILE = 'seen.json'

CONDITIONS = [
    {
        "name": "Chronic Urticaria",
        "query": "chronic urticaria",
        "key": "urticaria",
    },
]


def load_seen():
    try:
        with open(SEEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_seen(seen):
    with open(SEEN_FILE, 'w') as f:
        json.dump(seen, f, indent=2)


def notify(title, message, url=None):
    headers = {"Title": title}
    if url:
        headers["Click"] = url
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode(), headers=headers)


def fetch_trials(query):
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.cond": query,
        "filter.overallStatus": "RECRUITING,NOT_YET_RECRUITING",
        "pageSize": 1000,
        "format": "json",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("studies", [])


def check_condition(condition, seen):
    key = condition["key"]
    first_run = key not in seen
    seen_ids = set(seen.get(key, []))

    studies = fetch_trials(condition["query"])
    new_trials = []

    for study in studies:
        proto = study.get("protocolSection", {})
        id_module = proto.get("identificationModule", {})
        nct_id = id_module.get("nctId")
        title = id_module.get("briefTitle", "Unknown title")

        if nct_id and nct_id not in seen_ids:
            seen_ids.add(nct_id)
            if not first_run:
                new_trials.append({"nct_id": nct_id, "title": title})

    if first_run:
        print(f"First run for {condition['name']}: indexed {len(seen_ids)} existing trials, no notifications sent")
    elif new_trials:
        for trial in new_trials:
            ct_url = f"https://clinicaltrials.gov/study/{trial['nct_id']}"
            notify(f"New {condition['name']} Trial", trial["title"], ct_url)
            print(f"Notified: {trial['nct_id']} — {trial['title']}")
    else:
        print(f"No new {condition['name']} trials ({len(seen_ids)} known)")

    seen[key] = list(seen_ids)


def main():
    seen = load_seen()
    for condition in CONDITIONS:
        check_condition(condition, seen)
    save_seen(seen)


if __name__ == "__main__":
    main()

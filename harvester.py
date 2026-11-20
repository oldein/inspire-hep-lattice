"""
Download INSPIRE-HEP literature records info (title, abstract etc.) by subject category and date range.
Settings are in config.py. 
"""
import json
import time
from datetime import timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
import config

#Split [start, end] into consecutive windows of number of days.
def date_windows(start, end, days):
    current = start
    while current <= end:
        window_end = min(current + timedelta(days=days - 1), end)
        yield current, window_end
        current = window_end + timedelta(days=1)

#Search by subject
def subject_term(subject):
    return f'inspire_categories.term:"{subject}"'

#Build query string from parameters for one date window
def build_query(start, end):
    parts = [f"{config.DATE_TYPE} {start}->{end}"]
    if config.SUBJECTS_ANY:
        parts.append("(" + " or ".join(subject_term(s) for s in config.SUBJECTS_ANY) + ")")
    for s in config.SUBJECTS_ALL:
        parts.append(subject_term(s))
    for s in config.SUBJECTS_NONE:
        parts.append("not " + subject_term(s))
    return " and ".join(parts)

#Metadata is huge, keep only fields from settings (config.py)
def clean_record(hit):
    metadata = hit.get("metadata", {})
    return {field: metadata.get(field) for field in config.FIELDS}

#Make HTTP session with retries for different errors & limits
def make_session():
    retries = Retry(
        total=config.MAX_RETRIES,
        backoff_factor=5, 
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

#Download all records for one date window (page by page within window)
def fetch_window(session, start, end):
    params = {
        "q": build_query(start, end),
        "size": config.PAGE_SIZE,
        "fields": ",".join(config.FIELDS),
        "page": 1,
    }
    records = []
    while True:
        response = session.get(config.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        time.sleep(config.REQUEST_DELAY)

        hits = response.json()["hits"]
        total = hits["total"]
        if total > config.MAX_RECORDS_PER_QUERY:
            raise ValueError(
                f"{start} to {end} has {total} records, over the limit. "
                "Make WINDOW_DAYS smaller in config.py."
            )

        records.extend(clean_record(hit) for hit in hits["hits"])
        if not hits["hits"] or len(records) >= total:
            return records
        params["page"] += 1


def main():
    config.DATA_DIR.mkdir(exist_ok=True)
    session = make_session()
    windows = list(date_windows(config.START_DATE, config.END_DATE, config.WINDOW_DAYS))
    new_records = 0
    t0 = time.perf_counter()

    with tqdm(windows, unit="window") as bar:
        for start, end in bar:
            path = config.DATA_DIR / f"{start}_to_{end}.json"
            if path.exists():
                bar.write(f"Skipping {path.name}: already downloaded")
                continue

            bar.set_description(f"{start} to {end}")
            records = fetch_window(session, start, end)

            # write to a temp file first
            tmp = path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False)
            tmp.replace(path)

            new_records += len(records)
            bar.set_postfix(records=new_records)

    minutes, seconds = divmod(int(time.perf_counter() - t0), 60)
    print(f"New records downloaded: {new_records}")
    print(f"Time: {minutes}m {seconds}s")


if __name__ == "__main__":
    main()
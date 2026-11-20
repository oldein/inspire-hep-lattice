"""
Merge the per-window JSON files from harvest.py into one JSON Lines file,simplify metadata structure
Run after harvester.py
"""
import json

from tqdm import tqdm

import config
from harvester import date_windows

#Flatten metadata fields
def simplify(record):
    out = {}
    for field, value in record.items():
        if field == "titles":
            out["title"] = value[0].get("title") if value else None
        elif field == "abstracts":
            out["abstract"] = " ".join(value[0].get("value", "").split()) if value else None
        elif field == "inspire_categories":
            out["categories"] = [c.get("term") for c in value] if value else []
        else:
            out[field] = value
    return out


def main():
    windows = list(date_windows(config.START_DATE, config.END_DATE, config.WINDOW_DAYS))
    paths = [config.DATA_DIR / f"{start}_to_{end}.json" for start, end in windows]

    missing = [p.name for p in paths if not p.exists()]
    if missing:
        print(f"Missing {len(missing)} of {len(paths)} files, run harvest.py again:")
        for name in missing:
            print("  ", name)
        return

    written = 0
    with open(config.COMBINED_FILE, "w", encoding="utf-8") as out:
        for path in tqdm(paths, desc="Combining"):
            with open(path, encoding="utf-8") as f:
                for record in json.load(f):
                    out.write(json.dumps(simplify(record), ensure_ascii=False) + "\n")
                    written += 1

    print(f"Wrote {written} records to {config.COMBINED_FILE}")


if __name__ == "__main__":
    main()
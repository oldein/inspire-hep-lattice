"""
Convert the combined records.jsonl into a CSV file.
Run after combine_json.py
"""
import csv
import json

import config

#make value fit to a single cell 
def to_cell(value):
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return "; ".join(value)  # e.g. categories -> "Lattice; Phenomenology-HEP"
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)  # nested fields kept as JSON text
    return value


def main():
    src = config.COMBINED_FILE
    dst = src.with_suffix(".csv")
    if not src.exists():
        print(f"{src} not found. Run combine_json.py first.")
        return

    rows = 0
    with open(src, encoding="utf-8") as f_in, \
         open(dst, "w", encoding="utf-8-sig", newline="") as f_out:
        writer = None
        for line in f_in:
            record = json.loads(line)
            if writer is None:  # take column names from the first record
                writer = csv.DictWriter(f_out, fieldnames=list(record))
                writer.writeheader()
            writer.writerow({k: to_cell(v) for k, v in record.items()})
            rows += 1

    print(f"Wrote {rows} rows to {dst}")


if __name__ == "__main__":
    main()
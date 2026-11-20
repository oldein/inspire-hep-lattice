# inspire-harvester

Small script to download papers info (title, abstract, subject categories, date) from
[INSPIRE-HEP](https://inspirehep.net) by subject category and date range.
Set up for Lattice papers from 2016 to 2025, but easy to change.

## How to run

```
pip install -r requirements.txt

python harvest.py        # downloads into data/
python combine_json.py   # merges everything into data/records.jsonl
python json_to_csv.py    # optional, makes data/records.csv
```

If `harvest.py` stops halfway, just run it again, it skips what's already downloaded.

## Changing what you download

Everything is in `config.py`:

- `SUBJECTS_ANY` / `SUBJECTS_ALL` / `SUBJECTS_NONE`: categories to match
  any of, all of, or exclude. Leave a list empty to ignore it.
  (Lattice note: makes sense to exlude "Condensed Matter" category)
- `DATE_TYPE`: `"de"` for when the paper first appeared, `"dadd"` for when
  it was added to INSPIRE
- `START_DATE`, `END_DATE`: date range
- `FIELDS`: which metadata to keep

Category names are INSPIRE's own: Lattice, Theory-HEP, Phenomenology-HEP,
Experiment-HEP, Astrophysics, Gravitation and Cosmology, etc.

## Things to watch out for

- If you change the config, **empty `data/` first**, otherwise old files get reused.
- INSPIRE returns max 10000 records per query, so the download is split into
  date windows (`WINDOW_DAYS`, 1 year by default). If you get an "over the limit"
  error, make it smaller. 
- Rate limiting (15 requests per 5 s) is handled by the script.
- Only the first abstract is kept if a paper has several.
- `control_number` is the INSPIRE id: `https://inspirehep.net/literature/<control_number>`

## Useful links

- [INSPIRE API docs](https://github.com/inspirehep/rest-api-doc)
- [Literature record schema](https://inspire-schemas.readthedocs.io/en/latest/schemas/hep.html) (all fields you can put in `FIELDS`)
- [Search syntax](https://help.inspirehep.net/knowledge-base/inspire-paper-search/)
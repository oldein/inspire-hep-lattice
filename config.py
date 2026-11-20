"""
Settings for the INSPIRE (Literature) harvester.
This is the only file you should need to edit.
"""
from datetime import date
from pathlib import Path

# SEARCH FIELDS
# INSPIRE subject categories
# Available: Accelerators, Astrophysics, Computing, Experiment-HEP, Experiment-Nucl,General Physics, Gravitation and Cosmology, Instrumentation, Lattice, Math and Math Physics, Other, Phenomenology-HEP, Theory-HEP, Theory-Nucl
SUBJECTS_ANY  = ["Lattice"]   # at least one of these (OR)
SUBJECTS_ALL  = [] # every one of these (AND)
SUBJECTS_NONE = [] # none of these (NOT)

# # DATE RANGES
DATE_TYPE = "de" #date of the earlies paper appearance
START_DATE = date(2016, 1, 1)
END_DATE = date(2025, 12, 31)

# Length of each date window in days. INSPIRE returns at most 10,000 records per query, so if a window goes over that, make this smaller (unlikely for Lattice, likely for big categories).
WINDOW_DAYS = 365

#METADATA FIELDS
FIELDS = [
    "control_number",      # INSPIRE record id
    "titles",
    "abstracts",
    "inspire_categories",
    "earliest_date",
]

#OUTPUT
DATA_DIR = Path("data") # per-window JSON files go here
COMBINED_FILE = DATA_DIR / "records.jsonl"

#API SETTINGS
BASE_URL = "https://inspirehep.net/api/literature"
PAGE_SIZE = 500  # records per request, max 1000
REQUEST_DELAY = 0.5 # seconds between requests (limit: 15 per 5 s)
MAX_RETRIES = 5 # retries on errors and 429s
MAX_RECORDS_PER_QUERY = 9900 # safety margin below the 10000 
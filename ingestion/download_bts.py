"""
Download BTS On-Time Performance for one month.
Manual download (already done): https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ
Filter: Year=2026, Period=August. Select the 30 fields from docs/data_dictionary.md.
Save as data/raw/bts_aug2026.csv.
"""
import os
from config import BTS_CSV_PATH

if not os.path.exists(BTS_CSV_PATH):
    raise FileNotFoundError(f"BTS CSV not found at {BTS_CSV_PATH}. Download manually from BTS.")
print(f"BTS CSV ready: {BTS_CSV_PATH}")
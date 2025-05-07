#!/usr/bin/env python3

import pandas as pd
import json
import sys
from pathlib import Path

# 1) Try to locate the CSV in two places
candidates = [
    Path("Male-FF.csv"),             # same folder as script
    Path("/mnt/data/Male-FF.csv"),   # common upload folder
]

csv_path = None
for p in candidates:
    if p.exists():
        csv_path = p
        break

if csv_path is None:
    print(
        "❌ Error: Could not find 'Male-FF.csv'.\n"
        "Looked for:\n  " +
        "\n  ".join(str(p) for p in candidates) +
        "\nMake sure the file is named exactly 'Male-FF.csv' and placed in one of those locations.",
        file=sys.stderr
    )
    sys.exit(1)

# 2) Load the CSV
df = pd.read_csv(csv_path)

# 3) Drop any column that’s completely empty
df = df.dropna(axis=1, how="all")

# 4) Normalize empty strings → proper missing (so JSON emits null)
df = df.replace({"": pd.NA}).where(pd.notnull(df), None)

# 5) Whitelist exactly your nine columns
keep = [
    "Gender",
    "Rise Preference",
    "Fit Preference",
    "Footwear",
    "Stretch Preference",
    "Style Persona",
    "FIT",
    "FIT.1",
    "FIT.2",
]
keep = [c for c in keep if c in df.columns]
if len(keep) < 9:
    missing = set([
        "Gender","Rise Preference","Fit Preference",
        "Footwear","Stretch Preference","Style Persona",
        "FIT","FIT.1","FIT.2"
    ]) - set(keep)
    print(f"⚠️ Warning: Missing columns in CSV: {missing}", file=sys.stderr)

clean = df[keep]

# 6) Write out clean JSON
out_path = "male_quiz_data.json"
records = clean.to_dict(orient="records")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"✅ Wrote {len(records)} records to {out_path}")

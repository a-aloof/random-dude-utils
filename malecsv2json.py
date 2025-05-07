import pandas as pd
import json

# 1) Load the CSV
df = pd.read_csv("Male-FF.csv")

# 2) Drop any column that’s completely empty
df = df.dropna(axis=1, how="all")

# 3) Normalize empty strings → proper missing, so JSON emits null
df = df.replace({"": pd.NA}).where(pd.notnull(df), None)

# 4) Keep only your 9 quiz fields
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
keep = [c for c in keep if c in df.columns]  # filter in case headers differ
clean = df[keep]

# 5) Write out clean JSON
records = clean.to_dict(orient="records")
with open("male_quiz_data.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(records)} records to male_quiz_data.json")

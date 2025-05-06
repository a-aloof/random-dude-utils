import streamlit as st

# 1️⃣ Check for openpyxl up front
try:
    import openpyxl
except ImportError:
    st.error(
        "🔴 Missing optional dependency `openpyxl`.\n\n"
        "Please add it to your requirements.txt (or run `pip install openpyxl`) and redeploy."
    )
    st.stop()

import pandas as pd
import json

st.set_page_config(page_title="FitFinder JSON Generator")
st.title("📝 FitFinder Quiz Data → JSON")

st.markdown(
    """
1. **Upload** your Male FIT and Female FIT Excel files (.xlsx).  
2. The app will **detect** the sheet containing your `FIT` columns, **normalize** any `FITS` → `FIT`, and **combine** both.  
3. **Preview** the table below, then **Download** the final JSON.
"""
)

male_file = st.file_uploader("📥 Upload Male Fit Excel", type="xlsx", key="male")
female_file = st.file_uploader("📥 Upload Female Fit Excel", type="xlsx", key="female")

def load_fit_sheet(buf, label):
    """
    1) Scans each sheet for a column starting with 'FIT'
    2) Reads it with openpyxl
    3) Normalizes any 'FITS' → 'FIT'
    4) Drops unnamed columns
    """
    try:
        xls = pd.ExcelFile(buf, engine="openpyxl")
    except Exception as e:
        st.error(f"Could not read {label}: {e}")
        return pd.DataFrame()

    for sheet in xls.sheet_names:
        cols = pd.read_excel(buf, sheet_name=sheet, nrows=0, engine="openpyxl").columns
        if any(c.strip().upper().startswith("FIT") for c in cols):
            df = pd.read_excel(buf, sheet_name=sheet, engine="openpyxl")
            # Normalize FITS → FIT
            rename_map = {
                c: c.upper().replace("FITS", "FIT")
                for c in df.columns
                if c.strip().upper().startswith("FITS")
            }
            df = df.rename(columns=rename_map)
            # Drop any unnamed columns
            df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
            return df

    st.error(f"No sheet with FIT columns found in {label}")
    return pd.DataFrame()

if male_file and female_file:
    male_df = load_fit_sheet(male_file, "Male Excel")
    female_df = load_fit_sheet(female_file, "Female Excel")

    if not male_df.empty and not female_df.empty:
        combined = pd.concat([male_df, female_df], ignore_index=True)

        st.markdown("### 👀 Combined Data Preview")
        st.dataframe(combined)

        records = combined.to_dict(orient="records")
        json_str = json.dumps(records, indent=2, ensure_ascii=False)

        st.download_button(
            label="📤 Download JSON",
            data=json_str,
            file_name="fit_quiz_data.json",
            mime="application/json",
        )

st.markdown("---")
st.markdown(
    "Built with ❤️ by Amazing Variable. "
    "Make sure your `requirements.txt` includes:\n\n"
    "```\n"
    "streamlit\n"
    "pandas\n"
    "openpyxl\n"
    "```"
)

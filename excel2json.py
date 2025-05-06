import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="FitFinder CSV → JSON")
st.title("FitFinder CSV → JSON")

st.markdown("""
1. Upload your `male.csv` and `female.csv`.  
2. The app will combine them, drop any fully empty columns, remove all `FITS*` junk columns,  
   and keep only the first three `FIT*` columns.  
3. Preview and Download your clean `fit_quiz_data.json`.
""")

male_csv   = st.file_uploader("📥 Upload male.csv",   type="csv", key="m")
female_csv = st.file_uploader("📥 Upload female.csv", type="csv", key="f")

if male_csv and female_csv:
    # 1) Load & stack
    df = pd.concat([
        pd.read_csv(male_csv),
        pd.read_csv(female_csv)
    ], ignore_index=True)

    # 2) Drop any column where every value is NaN/empty
    df = df.dropna(axis=1, how="all")

    # 3) Remove stray FITS* columns
    df = df.loc[:, ~df.columns.str.upper().str.startswith("FITS")]

    # 4) Keep only the first three FIT* columns
    fit_cols = [c for c in df.columns if c.upper().startswith("FIT")]
    fit_cols = fit_cols[:3]
    df = df[fit_cols]

    st.markdown("### 👀 Cleaned Data Preview")
    st.dataframe(df)

    # 5) Download JSON
    records = df.to_dict(orient="records")
    js = json.dumps(records, indent=2, ensure_ascii=False)
    st.download_button(
        "📤 Download JSON",
        data=js,
        file_name="fit_quiz_data.json",
        mime="application/json",
    )
else:
    st.info("Waiting for both CSVs to be uploaded…")

import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="FitFinder CSV → JSON")
st.title("FitFinder CSV → JSON")

st.markdown("""
1. Upload your **male.csv** and **female.csv**.  
2. The app will normalize **FITS→FIT**, combine both files, drop any completely empty columns,  
   and keep only your quiz inputs plus **FIT**, **FIT.1**, **FIT.2**.  
3. Preview below and Download the final **fit_quiz_data.json**.
""")

male_csv   = st.file_uploader("📥 Upload male.csv",   type="csv", key="m")
female_csv = st.file_uploader("📥 Upload female.csv", type="csv", key="f")

if male_csv and female_csv:
    # 1) Load both CSVs
    df_m = pd.read_csv(male_csv)
    df_f = pd.read_csv(female_csv)

    # 2) Rename female FITS* columns -> FIT*
    rename_map = {
        col: col.replace("FITS", "FIT")
        for col in df_f.columns
        if col.upper().startswith("FITS")
    }
    df_f = df_f.rename(columns=rename_map)

    # 3) Combine into one DataFrame
    df = pd.concat([df_m, df_f], ignore_index=True)

    # 4) Drop any column where every value is NaN/empty
    df = df.dropna(axis=1, how="all")

    # 5) Define exactly which columns to keep
    inputs = [
        "Gender",
        "Rise Preference",
        "Fit Preference",
        "Footwear",
        "Stretch Preference",
        "Style Persona",
    ]
    fit_cols = [c for c in df.columns if c.upper().startswith("FIT")]
    fit_cols = sorted(fit_cols)[:3]  # take FIT, FIT.1, FIT.2 (in order)
    keep = inputs + fit_cols

    # 6) Filter out any missing input columns
    keep = [c for c in keep if c in df.columns]
    clean = df[keep]

    st.markdown("### 👀 Cleaned Data Preview")
    st.dataframe(clean)

    # 7) Download as JSON
    records = clean.to_dict(orient="records")
    js = json.dumps(records, indent=2, ensure_ascii=False)
    st.download_button(
        "📤 Download JSON",
        data=js,
        file_name="fit_quiz_data.json",
        mime="application/json",
    )
else:
    st.info("Waiting for both CSVs to be uploaded…")

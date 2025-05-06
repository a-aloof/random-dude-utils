import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="FitFinder CSV → JSON", layout="wide")
st.title("📝 FitFinder CSV → JSON")

st.markdown("""
Upload your **male.csv** and **female.csv** (each with exactly 9 columns:  
`Gender, Rise Preference, Fit Preference, Footwear, Stretch Preference, Style Persona, FIT, FIT, FIT`  
and  
`Gender, Rise Preference, Fit Preference, Footwear, Stretch Preference, Style Persona, FITS, FITS, FITS`).

This app will:
1. Rename the *last three* columns to `FIT1`, `FIT2`, `FIT3` (so duplicates don’t matter).  
2. Stack both files into one DataFrame.  
3. Drop any column that’s 100% empty.  
4. Keep only your **six inputs** + `FIT1, FIT2, FIT3`.  
5. Preview and let you download a clean JSON.
""")

male_csv   = st.file_uploader("📥 Upload male.csv",   type="csv", key="m")
female_csv = st.file_uploader("📥 Upload female.csv", type="csv", key="f")

def standardize_last3(df):
    """
    Overwrite df.columns so:
      - first 6 names remain as-is
      - last 3 columns become FIT1, FIT2, FIT3
    """
    cols = list(df.columns)
    if len(cols) < 9:
        st.error(f"Expected ≥9 columns, got {len(cols)}. Please check your CSV.")
        st.stop()
    first6 = cols[:6]
    new_last3 = ["FIT1", "FIT2", "FIT3"]
    df.columns = first6 + new_last3 + cols[9:]
    return df

if male_csv and female_csv:
    # 1) Load
    df_m = pd.read_csv(male_csv)
    df_f = pd.read_csv(female_csv)

    # 2) Standardize column names
    df_m = standardize_last3(df_m)
    df_f = standardize_last3(df_f)

    # 3) Stack them
    df = pd.concat([df_m, df_f], ignore_index=True)

    # 4) Drop any column that is entirely empty
    df = df.dropna(axis=1, how="all")

    # 5) Whitelist exactly the 6 inputs + FIT1-3
    inputs = [
        "Gender",
        "Rise Preference",
        "Fit Preference",
        "Footwear",
        "Stretch Preference",
        "Style Persona",
    ]
    desired = inputs + ["FIT1", "FIT2", "FIT3"]
    keep = [c for c in desired if c in df.columns]
    clean = df[keep]

    # 6) Preview
    st.markdown("### 👀 Cleaned Data Preview")
    st.dataframe(clean, height=450)

    # 7) Download JSON
    records = clean.to_dict(orient="records")
    js = json.dumps(records, indent=2, ensure_ascii=False)
    st.download_button(
        "📥 Download fit_quiz_data.json",
        data=js,
        file_name="fit_quiz_data.json",
        mime="application/json",
    )
else:
    st.info("Please upload both CSV files to proceed.")

# Footer
st.markdown("---")
st.markdown(
    "Ensure your `requirements.txt` contains:\n\n"
    "```\n"
    "streamlit\n"
    "pandas\n"
    "```"
)

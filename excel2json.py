import streamlit as st
import pandas as pd
import json

st.title("FitFinder CSV → JSON")

male_csv   = st.file_uploader("Upload male.csv",   type="csv")
female_csv = st.file_uploader("Upload female.csv", type="csv")

if male_csv and female_csv:
    df1 = pd.read_csv(male_csv)
    df2 = pd.read_csv(female_csv)
    combined = pd.concat([df1, df2], ignore_index=True)

    st.dataframe(combined)

    json_str = json.dumps(combined.to_dict(orient="records"),
                          indent=2, ensure_ascii=False)
    st.download_button("Download JSON", json_str,
                       file_name="fit_quiz_data.json",
                       mime="application/json")

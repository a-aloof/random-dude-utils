# seach-analyzer.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

st.set_page_config(page_title="🔍 GSC Search Analyzer", layout="wide")

st.title("🔍 Google Search Console Full Analyzer")

st.markdown("""
Upload the following CSVs exported from Google Search Console:

- Queries.csv
- Pages.csv
- Countries.csv
- Devices.csv
- Dates.csv
- Search appearance.csv

**Upload all your GSC CSV files**
""")

uploaded_files = st.file_uploader("Upload your GSC CSV files", type=['csv'], accept_multiple_files=True)

if uploaded_files:
    data = {}
    
    for file in uploaded_files:
        filename = file.name.lower()
        if 'query' in filename:
            queries = pd.read_csv(file)
            data['queries'] = queries
        elif 'page' in filename:
            pages = pd.read_csv(file)
            data['pages'] = pages
        elif 'country' in filename:
            countries = pd.read_csv(file)
            data['countries'] = countries
        elif 'device' in filename:
            devices = pd.read_csv(file)
            data['devices'] = devices
        elif 'date' in filename:
            dates = pd.read_csv(file)
            data['dates'] = dates
        elif 'search appearance' in filename:
            search_appearance = pd.read_csv(file)
            data['search_appearance'] = search_appearance
    
    # Preprocessing: Clean CTR and Position columns
    if 'queries' in data:
        queries = data['queries']
        if 'ctr' in queries.columns:
            queries['ctr'] = queries['ctr'].str.rstrip('%').astype(float)
        if 'position' in queries.columns:
            queries['position'] = pd.to_numeric(queries['position'], errors='coerce')
    
    if 'pages' in data:
        pages = data['pages']
        if 'ctr' in pages.columns:
            pages['ctr'] = pages['ctr'].str.rstrip('%').astype(float)
        if 'position' in pages.columns:
            pages['position'] = pd.to_numeric(pages['position'], errors='coerce')
    
    st.header("📈 Overall Performance Metrics")
    try:
        total_clicks = queries['clicks'].sum()
        total_impressions = queries['impressions'].sum()
        avg_ctr = queries['ctr'].mean()
        avg_position = queries['position'].mean()
        
        st.metric("Total Clicks", f"{total_clicks:,}")
        st.metric("Total Impressions", f"{total_impressions:,}")
        st.metric("Average CTR", f"{avg_ctr:.2f}%")
        st.metric("Average Position", f"{avg_position:.2f}")
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")

    st.header("🔎 Top Queries")
    top_queries = queries.sort_values(by='clicks', ascending=False).head(20)
    st.dataframe(top_queries)

    st.subheader("CTR vs Position Scatter Plot")
    fig = px.scatter(queries, x="position", y="ctr", size="impressions", hover_data=["query"], title="CTR vs Position")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Opportunity Queries (High Impressions, Low CTR)")
    opportunity = queries[(queries['impressions'] > queries['impressions'].quantile(0.75)) & (queries['ctr'] < queries['ctr'].median())]
    st.dataframe(opportunity.sort_values(by='impressions', ascending=False))

    st.header("🖥️ Device Performance")
    if 'devices' in data:
        fig = px.pie(data['devices'], names='device', values='clicks', title="Clicks by Device")
        st.plotly_chart(fig, use_container_width=True)

    st.header("🌍 Top Countries")
    if 'countries' in data:
        fig = px.bar(data['countries'].sort_values(by='clicks', ascending=False).head(10),
                     x='country', y='clicks', title="Top Countries by Clicks")
        st.plotly_chart(fig, use_container_width=True)

    st.header("🗓️ Clicks & Impressions Over Time")
    if 'dates' in data:
        dates = data['dates']
        fig = px.line(dates, x='date', y=['clicks', 'impressions'], title="Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)

    st.header("🔎 Search Appearance Analysis")
    if 'search_appearance' in data:
        fig = px.bar(data['search_appearance'], x='searchAppearance', y='clicks', title="Clicks by Search Appearance")
        st.plotly_chart(fig, use_container_width=True)

    st.header("🔍 Keyword Clustering (Bonus)")
    try:
        # Simple keyword clustering using TF-IDF and KMeans
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(queries['query'])

        n_clusters = 5
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        queries['cluster'] = kmeans.fit_predict(X)

        for i in range(n_clusters):
            cluster_df = queries[queries['cluster'] == i]
            st.subheader(f"Cluster {i+1} (Top keywords)")
            st.dataframe(cluster_df[['query', 'clicks', 'impressions']].sort_values(by='clicks', ascending=False).head(10))
    except Exception as e:
        st.warning(f"Keyword clustering failed: {e}")

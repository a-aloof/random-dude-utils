import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

st.set_page_config(page_title="GSC Full Analyzer", layout="wide")
st.title("🔍 Google Search Console Full Analyzer")

st.markdown("""
Upload the following CSVs exported from Google Search Console:
- Queries.csv
- Pages.csv
- Countries.csv
- Devices.csv
- Dates.csv
- Search appearance.csv
""")

uploaded_files = st.file_uploader("Upload all your GSC CSV files", type=["csv"], accept_multiple_files=True)

# Dictionary to store dataframes
data = {}

# Map filename keywords to keys
dataset_keys = {
    'queries': 'queries',
    'pages': 'pages',
    'countries': 'countries',
    'devices': 'devices',
    'dates': 'dates',
    'search appearance': 'search_appearance'
}

if uploaded_files:
    for file in uploaded_files:
        for key in dataset_keys:
            if key in file.name.lower():
                data[dataset_keys[key]] = pd.read_csv(file)

    missing_sections = [v for v in dataset_keys.values() if v not in data]
    if missing_sections:
        st.warning(f"Missing files for: {', '.join(missing_sections)}")

    # Process Queries.csv
    if 'queries' in data:
        queries = data['queries']
        queries.columns = [col.strip().lower().replace(' ', '_') for col in queries.columns]

        st.header("📈 Overall Performance Metrics")
        total_clicks = queries['clicks'].sum()
        total_impressions = queries['impressions'].sum()
        avg_ctr = queries['ctr'].mean()
        avg_position = queries['position'].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Clicks", f"{total_clicks:,}")
        col2.metric("Total Impressions", f"{total_impressions:,}")
        col3.metric("Avg CTR", f"{avg_ctr:.2f}%")
        col4.metric("Avg Position", f"{avg_position:.2f}")

        st.subheader("🔝 Top Queries")
        top_queries = queries.sort_values(by='clicks', ascending=False).head(10)
        st.dataframe(top_queries[['query', 'clicks', 'impressions', 'ctr', 'position']])
        fig = px.bar(top_queries, x='query', y='clicks', title='Top Queries by Clicks')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🎯 Opportunity Queries (Low CTR, High Impressions)")
        opp_queries = queries[(queries['impressions'] > 1000) & (queries['ctr'] < 1)]
        st.dataframe(opp_queries[['query', 'clicks', 'impressions', 'ctr', 'position']])

        st.subheader("📊 CTR vs Position (Queries)")
        fig3 = px.scatter(queries, x='position', y='ctr', hover_data=['query'], trendline='ols', title='CTR vs Position')
        st.plotly_chart(fig3, use_container_width=True)

    # Process Pages.csv
    if 'pages' in data:
        pages = data['pages']
        pages.columns = [col.strip().lower().replace(' ', '_') for col in pages.columns]

        st.header("📄 Top Pages")
        top_pages = pages.sort_values(by='clicks', ascending=False).head(10)
        st.dataframe(top_pages[['page', 'clicks', 'impressions', 'ctr', 'position']])
        fig = px.bar(top_pages, x='page', y='clicks', title='Top Pages by Clicks')
        st.plotly_chart(fig, use_container_width=True)

    # Process Devices.csv
    if 'devices' in data:
        devices = data['devices']
        devices.columns = [col.strip().lower().replace(' ', '_') for col in devices.columns]

        st.header("📱 Device Performance")
        fig = px.pie(devices, values='clicks', names='device', title='Clicks by Device')
        st.plotly_chart(fig, use_container_width=True)

    # Process Countries.csv
    if 'countries' in data:
        countries = data['countries']
        countries.columns = [col.strip().lower().replace(' ', '_') for col in countries.columns]

        st.header("🌎 Country Performance")
        top_countries = countries.sort_values(by='clicks', ascending=False).head(10)
        st.dataframe(top_countries[['country', 'clicks', 'impressions', 'ctr', 'position']])
        fig = px.bar(top_countries, x='country', y='clicks', title='Top Countries by Clicks')
        st.plotly_chart(fig, use_container_width=True)

    # Process Dates.csv
    if 'dates' in data:
        dates = data['dates']
        dates.columns = [col.strip().lower().replace(' ', '_') for col in dates.columns]

        st.header("📅 Performance Over Time")
        fig = px.line(dates, x='date', y=['clicks', 'impressions'], title='Clicks and Impressions Over Time')
        st.plotly_chart(fig, use_container_width=True)

    # Process Search Appearance
    if 'search_appearance' in data:
        appearance = data['search_appearance']
        appearance.columns = [col.strip().lower().replace(' ', '_') for col in appearance.columns]

        st.header("✨ Search Appearance Performance")
        st.dataframe(appearance)
        fig = px.bar(appearance, x='search_appearance', y='clicks', title='Clicks by Search Appearance')
        st.plotly_chart(fig, use_container_width=True)

    # Keyword Clustering (from Queries)
    if 'queries' in data:
        st.header("🧠 Keyword Clustering (KMeans + TF-IDF)")
        num_clusters = st.slider("Select number of clusters", 2, 10, 5)
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(queries['query'])
        kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(X)
        queries['cluster'] = kmeans.labels_
        cluster_summary = queries.groupby('cluster').agg({
            'query': 'count',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        cluster_summary.columns = ['Cluster', 'Num Queries', 'Total Clicks', 'Total Impressions']
        st.dataframe(cluster_summary)

    st.success("✅ Full Analysis Complete!")

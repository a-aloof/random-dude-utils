import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

st.set_page_config(page_title="🔍 GSC Search Analyzer", layout="wide")

st.title("🔍 Google Search Console Full Analyzer")

st.sidebar.title("📊 Report Sections")
show_queries = st.sidebar.checkbox("Top Queries & CTR Scatter", value=True)
show_opportunities = st.sidebar.checkbox("Opportunity Queries", value=True)
show_devices = st.sidebar.checkbox("Device Performance", value=True)
show_countries = st.sidebar.checkbox("Top Countries", value=True)
show_dates = st.sidebar.checkbox("Time Series (Clicks/Impressions)", value=True)
show_search_appearance = st.sidebar.checkbox("Search Appearance", value=True)
show_clusters = st.sidebar.checkbox("Keyword Clusters", value=True)

st.markdown("""
Upload the following CSVs exported from Google Search Console:

- Queries.csv
- Pages.csv
- Countries.csv
- Devices.csv
- Dates.csv
- Search appearance.csv
""")

uploaded_files = st.file_uploader("Upload your GSC CSV files", type=['csv'], accept_multiple_files=True)

if uploaded_files:
    data = {}
    for file in uploaded_files:
        filename = file.name.lower()
        if 'query' in filename:
            queries = pd.read_csv(file)
            if 'ctr' in queries.columns:
                queries['ctr'] = queries['ctr'].str.rstrip('%').astype(float)
            if 'position' in queries.columns:
                queries['position'] = pd.to_numeric(queries['position'], errors='coerce')
            data['queries'] = queries
        elif 'page' in filename:
            pages = pd.read_csv(file)
            if 'ctr' in pages.columns:
                pages['ctr'] = pages['ctr'].str.rstrip('%').astype(float)
            if 'position' in pages.columns:
                pages['position'] = pd.to_numeric(pages['position'], errors='coerce')
            data['pages'] = pages
        elif 'country' in filename:
            data['countries'] = pd.read_csv(file)
        elif 'device' in filename:
            data['devices'] = pd.read_csv(file)
        elif 'date' in filename:
            data['dates'] = pd.read_csv(file)
        elif 'search appearance' in filename:
            data['search_appearance'] = pd.read_csv(file)

    if 'queries' in data:
        queries = data['queries']
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

    if show_queries and 'queries' in data:
        st.header("🔎 Top Queries")
        top_queries = queries.sort_values(by='clicks', ascending=False).head(20)
        st.dataframe(top_queries)

        st.subheader("CTR vs Position Scatter Plot")
        fig = px.scatter(queries, x="position", y="ctr", size="impressions", hover_data=["query"], title="CTR vs Position")
        st.plotly_chart(fig, use_container_width=True)

    if show_opportunities and 'queries' in data:
        st.subheader("🎯 Opportunity Queries (High Impressions, Low CTR)")
        opportunity = queries[(queries['impressions'] > queries['impressions'].quantile(0.75)) & (queries['ctr'] < queries['ctr'].median())]
        st.dataframe(opportunity.sort_values(by='impressions', ascending=False))

    if show_devices and 'devices' in data:
        st.header("🖥️ Device Performance")
        fig = px.pie(data['devices'], names='device', values='clicks', title="Clicks by Device")
        st.plotly_chart(fig, use_container_width=True)

    if show_countries and 'countries' in data:
        st.header("🌍 Top Countries")
        fig = px.bar(data['countries'].sort_values(by='clicks', ascending=False).head(10),
                     x='country', y='clicks', title="Top Countries by Clicks")
        st.plotly_chart(fig, use_container_width=True)

    if show_dates and 'dates' in data:
        st.header("🗓️ Clicks & Impressions Over Time")
        dates = data['dates']
        fig = px.line(dates, x='date', y=['clicks', 'impressions'], title="Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)

    if show_search_appearance and 'search_appearance' in data:
        st.header("🔎 Search Appearance Analysis")
        fig = px.bar(data['search_appearance'], x='searchAppearance', y='clicks', title="Clicks by Search Appearance")
        st.plotly_chart(fig, use_container_width=True)

    if show_clusters and 'queries' in data:
        st.header("🧠 Keyword Clustering (KMeans + TF-IDF)")
        try:
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

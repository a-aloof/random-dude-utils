import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

st.set_page_config(page_title="🔍 GSC Search Analyzer", layout="wide")
st.title("🔍 Google Search Console Full Analyzer")

# Sidebar toggles
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

# Columns expected
REQUIRED_QUERY_COLUMNS = ['query', 'clicks', 'impressions', 'ctr', 'position']
COLUMN_RENAME_MAP = {
    'top queries': 'query',
    'search term': 'query',
    'clicks': 'clicks',
    'impressions': 'impressions',
    'ctr': 'ctr',
    'position': 'position'
}

def fix_query_file(df):
    df.columns = [col.strip().lower() for col in df.columns]
    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)
    return df

if uploaded_files:
    data = {}
    for file in uploaded_files:
        filename = file.name.lower()
        try:
            df = pd.read_csv(file)
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            if 'query' in filename:
                df = fix_query_file(df)

                # Show debug info
                st.caption("✅ Uploaded Queries.csv Columns:")
                st.write(df.columns.tolist())

                if 'ctr' in df.columns:
                    df['ctr'] = df['ctr'].astype(str).str.rstrip('%').astype(float)
                if 'position' in df.columns:
                    df['position'] = pd.to_numeric(df['position'], errors='coerce')

                missing = [col for col in REQUIRED_QUERY_COLUMNS if col not in df.columns]
                if not missing:
                    data['queries'] = df
                else:
                    st.warning(f"⚠️ Queries.csv is missing columns: {missing}")

            elif 'page' in filename:
                data['pages'] = df

            elif 'country' in filename:
                data['countries'] = df

            elif 'device' in filename:
                data['devices'] = df

            elif 'date' in filename:
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                if 'clicks' in df.columns:
                    df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
                if 'impressions' in df.columns:
                    df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
                data['dates'] = df

            elif 'search appearance' in filename:
                data['search_appearance'] = df

        except Exception as e:
            st.warning(f"❌ Failed to load {file.name}: {e}")

    # Now all visualizations based on uploaded files
    if 'queries' in data:
        queries = data['queries']
        st.header("📈 Overall Performance Metrics")
        try:
            st.metric("Total Clicks", f"{queries['clicks'].sum():,}")
            st.metric("Total Impressions", f"{queries['impressions'].sum():,}")
            st.metric("Average CTR", f"{queries['ctr'].mean():.2f}%")
            st.metric("Average Position", f"{queries['position'].mean():.2f}")
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
        opp_queries = queries[(queries['impressions'] > queries['impressions'].quantile(0.75)) & (queries['ctr'] < queries['ctr'].median())]
        st.dataframe(opp_queries.sort_values(by='impressions', ascending=False))

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
        fig = px.line(data['dates'], x='date', y=['clicks', 'impressions'], title="Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)

    if show_search_appearance and 'search_appearance' in data:
        st.header("🔎 Search Appearance Analysis")
        fig = px.bar(data['search_appearance'], x='search_appearance', y='clicks', title="Clicks by Search Appearance")
        st.plotly_chart(fig, use_container_width=True)

    if show_clusters and 'queries' in data:
        st.header("🧠 Keyword Clustering (KMeans + TF-IDF)")
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(queries['query'])
        kmeans = KMeans(n_clusters=5, random_state=42)
        queries['cluster'] = kmeans.fit_predict(X)

        for cluster_id in sorted(queries['cluster'].unique()):
            cluster_df = queries[queries['cluster'] == cluster_id]
            st.subheader(f"Cluster {cluster_id + 1}")
            st.dataframe(cluster_df[['query', 'clicks', 'impressions']].sort_values(by='clicks', ascending=False).head(10))

import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import io

st.set_page_config(page_title="Search Console Analyzer", layout="wide")
st.title("📈 Google Search Console Analyzer")

uploaded_file = st.file_uploader("Upload your GSC CSV export", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Standardize column names
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # Ensure key columns exist
    required_cols = ['query', 'page', 'clicks', 'impressions', 'ctr', 'position']
    if not all(col in df.columns for col in required_cols):
        st.error("Uploaded CSV doesn't have the required columns.")
    else:
        st.success("File successfully uploaded and processed.")

        # Metrics
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        avg_ctr = df['ctr'].mean()
        avg_position = df['position'].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Clicks", f"{total_clicks:,}")
        col2.metric("Total Impressions", f"{total_impressions:,}")
        col3.metric("Avg CTR", f"{avg_ctr:.2f}%")
        col4.metric("Avg Position", f"{avg_position:.2f}")

        st.subheader("🔝 Top Performing Queries")
        top_queries = df.sort_values(by='clicks', ascending=False).head(10)
        st.dataframe(top_queries[['query', 'clicks', 'impressions', 'ctr', 'position']])
        fig = px.bar(top_queries, x='query', y='clicks', title='Top Queries by Clicks')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🚨 Underperforming Pages")
        underperforming = df[(df['impressions'] > 1000) & (df['ctr'] < 1)]
        st.dataframe(underperforming[['page', 'clicks', 'impressions', 'ctr', 'position']].sort_values(by='ctr'))

        st.subheader("🧠 Keyword Clustering (KMeans + TF-IDF)")
        num_clusters = st.slider("Select number of clusters", 2, 10, 5)
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(df['query'])
        kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(X)
        df['cluster'] = kmeans.labels_
        cluster_summary = df.groupby('cluster').agg({
            'query': 'count',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        cluster_summary.columns = ['Cluster', 'Num Queries', 'Total Clicks', 'Total Impressions']
        st.dataframe(cluster_summary)

        st.subheader("📉 Ranking Trend Simulation")
        st.info("Simulated example: Avg CTR vs Position")
        position_range = np.arange(1, 21)
        ctr_values = [30/(p+1)**1.5 for p in position_range]
        fig2 = px.line(x=position_range, y=ctr_values, labels={'x': 'Position', 'y': 'Estimated CTR'}, title='CTR Curve by Position')
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("🎯 Opportunity Finder")
        opportunities = df[(df['position'] > 8) & (df['position'] < 15) & (df['impressions'] > 500)]
        st.dataframe(opportunities[['query', 'clicks', 'impressions', 'ctr', 'position']].sort_values(by='ctr'))

        st.subheader("📊 CTR vs Position")
        fig3 = px.scatter(df, x='position', y='ctr', hover_data=['query'], trendline='ols', title='CTR vs Position')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("🔍 Lost vs Potential Clicks")
        def expected_ctr(pos):
            return 30 / (pos + 1)**1.5
        df['expected_ctr'] = df['position'].apply(expected_ctr)
        df['potential_clicks'] = df['expected_ctr'] * df['impressions'] / 100
        df['lost_clicks'] = df['potential_clicks'] - df['clicks']
        df_clicks = df[['query', 'clicks', 'potential_clicks', 'lost_clicks']].sort_values(by='lost_clicks', ascending=False).head(10)
        st.dataframe(df_clicks)

        fig4 = px.bar(df_clicks, x='query', y=['clicks', 'potential_clicks'], barmode='group', title='Actual vs Potential Clicks')
        st.plotly_chart(fig4, use_container_width=True)

        st.success("✅ All analysis complete. Share this dashboard with stakeholders!")

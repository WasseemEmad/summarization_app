import streamlit as st
from llm_functions import analyze_articles
import pandas as pd


st.set_page_config(page_title="3D Printing Lead Finder", layout="wide")
st.title("🔍 3D Printing Market Article Analyzer")

# Initialize session state for summaries
if 'summaries' not in st.session_state:
    st.session_state.summaries = []

# Topic input
topic = st.text_input("Enter a topic to search for (e.g., '3D Printing trends')", value="3D Printing trends")

# Analyze button
if st.button("Analyze"):
    with st.spinner("🔎 Fetching and analyzing articles..."):
        summaries = analyze_articles(topic=topic, max_results=5, save_csv=True)
        st.session_state.summaries = summaries

# Display results if available
if st.session_state.summaries:
    st.success("✅ Analysis complete! Scroll down to view insights.")
    for idx, article in enumerate(st.session_state.summaries, 1):
        summary_text = article['summary'].lower()
        if len(article['summary']) < 300 or "access denied" in summary_text:
            continue  # skip short summaries
        with st.expander(f"Article #{idx}: {article['title']}"):
            st.markdown(f"**URL**: [{article['url']}]({article['url']})")
            st.markdown(article['summary'])

    st.markdown("---")

    # Load and prepare CSV for download
    csv_file_path = "3d_trend_company_insights.csv"
    try:
        df = pd.read_csv(csv_file_path)
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_bytes,
            file_name="3d_trend_company_insights.csv",
            mime="text/csv"
        )
    except FileNotFoundError:
        st.warning("⚠️ CSV file not found.")
else:
    st.info("Enter a topic and click 'Analyze' to begin.")

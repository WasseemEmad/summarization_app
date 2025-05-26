import streamlit as st
from llm_functions import get_message,get_summary_from_openai

st.header("Article summirization")

text = st.text_input("Enter a topic to search for")

if text:
    with st.spinner("Fetching articles..."):
        message = get_message(text, max_results=5)
    
    with st.spinner("Generating summary..."):
        summary = get_summary_from_openai(message)
    
    st.subheader("Summary")
    st.markdown(summary)
else:
    st.warning("Please enter a topic to search for articles.")
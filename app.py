"""Streamlit UI for the App Review Responder demo."""
from __future__ import annotations

from typing import List, Dict

import streamlit as st

from bright_data import fetch_reviews_from_bright_data
from faq_loader import load_faq_entries
from pipeline import AiriaPipeline, ReviewResult
from retrieval import LLAMA_AVAILABLE

st.set_page_config(page_title="App Review Responder", layout="wide")
st.title("📱 App Review Responder")
st.caption(
    "Fetch store reviews via Bright Data, ground them in an FAQ knowledge base, and respond with an Airia pipeline."
)


if "reviews" not in st.session_state:
    st.session_state["reviews"] = []
if "results" not in st.session_state:
    st.session_state["results"] = []

with st.sidebar:
    st.header("Configuration")
    app_id = st.text_input("App ID or Bundle ID", value="com.demo.app")
    store = st.selectbox("Store", options=["google", "apple"], index=0)
    max_reviews = st.slider("Max reviews", min_value=1, max_value=10, value=4)
    api_token = st.text_input("Bright Data API token", type="password")
    run_honeyhive = st.checkbox("Run HoneyHive evaluation", value=True)
    st.markdown(
        "**LlamaIndex**: {}".format("✅ available" if LLAMA_AVAILABLE else "⚠️ using keyword fallback")
    )
    st.markdown(
        "The FAQ base currently contains **{}** entries.".format(len(load_faq_entries()))
    )

col_fetch, col_run = st.columns(2)
with col_fetch:
    if st.button("Fetch reviews", key="fetch_reviews"):
        st.session_state["reviews"] = fetch_reviews_from_bright_data(
            app_id=app_id,
            store=store,
            max_reviews=max_reviews,
            api_token=api_token or None,
        )
        st.session_state["results"] = []
        st.success(f"Loaded {len(st.session_state['reviews'])} reviews.")

with col_run:
    if st.button("Run pipeline", key="run_pipeline", type="primary"):
        pipeline = AiriaPipeline(enable_honeyhive=run_honeyhive)
        st.session_state["results"] = [pipeline.run(review) for review in st.session_state["reviews"]]
        if st.session_state["results"]:
            st.success("Pipeline generated responses.")
        else:
            st.info("No reviews available. Fetch reviews first.")

reviews: List[Dict[str, str]] = st.session_state.get("reviews", [])
results: List[ReviewResult] = st.session_state.get("results", [])

left, right = st.columns(2)

with left:
    st.subheader("Raw reviews")
    if not reviews:
        st.info("Fetch reviews to populate this column.")
    else:
        for idx, review in enumerate(reviews, start=1):
            st.markdown(f"**Review {idx}** — {review.get('author', 'Anonymous')} ({review.get('rating', 'N/A')}★)")
            st.write(review.get("text", ""))
            meta = {key: review[key] for key in ["id", "date", "store"] if key in review}
            if meta:
                st.caption(str(meta))
            st.markdown("---")

with right:
    st.subheader("Airia responses")
    if not results:
        st.info("Run the pipeline to generate responses.")
    else:
        for idx, result in enumerate(results, start=1):
            st.markdown(f"**Response {idx}** — classified as `{result.category}`")
            st.write(result.response)
            with st.expander("Matched FAQ"):
                st.write(result.faq_entry.get("title", ""))
                st.caption(result.faq_entry.get("body", ""))
            if result.honeyhive_score:
                st.caption(
                    "HoneyHive (mock) — tone: {tone:.2f}, helpfulness: {helpfulness:.2f}. {notes}".format(
                        tone=result.honeyhive_score.tone,
                        helpfulness=result.honeyhive_score.helpfulness,
                        notes=result.honeyhive_score.notes,
                    )
                )
            st.markdown("---")

st.markdown("---")
st.markdown(
    "Need to automate further? Export the Airia pipeline YAML from the repo and upload to Airia to orchestrate the same flow."
)

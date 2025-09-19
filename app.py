"""Streamlit UI for the App Review Responder demo."""
from __future__ import annotations

from typing import List, Dict

import streamlit as st

from faq_loader import load_faq_entries
from pipeline import AiriaPipeline, ReviewResult
from retrieval import LLAMA_AVAILABLE

# Sample reviews for demo purposes
SAMPLE_REVIEWS = [
    {
        "id": "1",
        "author": "Alice",
        "rating": 2,
        "text": "App keeps crashing when I try to upload photos. Really frustrated!",
        "date": "2024-01-15",
        "store": "google"
    },
    {
        "id": "2", 
        "author": "Bob",
        "rating": 5,
        "text": "Love this app! Would be great to have a dark mode feature though.",
        "date": "2024-01-16",
        "store": "apple"
    },
    {
        "id": "3",
        "author": "Carol",
        "rating": 1,
        "text": "Billing is confusing and I got charged twice. Please fix this!",
        "date": "2024-01-17", 
        "store": "google"
    },
    {
        "id": "4",
        "author": "David",
        "rating": 4,
        "text": "Great app overall but it's a bit slow on my older phone.",
        "date": "2024-01-18",
        "store": "apple"
    }
]

st.set_page_config(page_title="App Review Responder", layout="wide")
st.title("📱 App Review Responder")
st.caption(
    "Demo app showing LlamaIndex retrieval and HoneyHive metrics for app review responses."
)


if "reviews" not in st.session_state:
    st.session_state["reviews"] = []
if "results" not in st.session_state:
    st.session_state["results"] = []

with st.sidebar:
    st.header("Configuration")
    run_honeyhive = st.checkbox("Enable HoneyHive evaluation", value=True)
    
    st.markdown("---")
    st.markdown("**System Status**")
    st.markdown(
        "**LlamaIndex**: {}".format("✅ available" if LLAMA_AVAILABLE else "⚠️ using keyword fallback")
    )
    st.markdown(
        "**FAQ Database**: {} entries loaded".format(len(load_faq_entries()))
    )
    
    # Check HoneyHive status
    import os
    honeyhive_key = os.getenv("HONEYHIVE_API_KEY")
    if honeyhive_key:
        st.markdown("**HoneyHive**: ✅ API key configured")
    else:
        st.markdown("**HoneyHive**: ⚠️ using mock evaluation")
        st.caption("Set HONEYHIVE_API_KEY environment variable for real tracking")

col_load, col_run = st.columns(2)
with col_load:
    if st.button("Load Sample Reviews", key="load_reviews"):
        st.session_state["reviews"] = SAMPLE_REVIEWS.copy()
        st.session_state["results"] = []
        st.success(f"Loaded {len(st.session_state['reviews'])} sample reviews.")

with col_run:
    if st.button("Run Pipeline", key="run_pipeline", type="primary"):
        if not st.session_state.get("reviews"):
            st.warning("Please load sample reviews first!")
        else:
            pipeline = AiriaPipeline(enable_honeyhive=run_honeyhive)
            st.session_state["results"] = [pipeline.run(review) for review in st.session_state["reviews"]]
            st.success("Pipeline completed! Check the responses below.")

reviews: List[Dict[str, str]] = st.session_state.get("reviews", [])
results: List[ReviewResult] = st.session_state.get("results", [])

left, right = st.columns(2)

with left:
    st.subheader("📱 Sample Reviews")
    if not reviews:
        st.info("Click 'Load Sample Reviews' to populate this column.")
    else:
        for idx, review in enumerate(reviews, start=1):
            st.markdown(f"**Review {idx}** — {review.get('author', 'Anonymous')} ({review.get('rating', 'N/A')}★)")
            st.write(f"*\"{review.get('text', '')}\"*")
            meta = {key: review[key] for key in ["id", "date", "store"] if key in review}
            if meta:
                st.caption(str(meta))
            st.markdown("---")

with right:
    st.subheader("🤖 AI Responses")
    if not results:
        st.info("Run the pipeline to generate responses.")
    else:
        for idx, result in enumerate(results, start=1):
            st.markdown(f"**Response {idx}** — classified as `{result.category}`")
            st.write(f"*\"{result.response}\"*")
            
            with st.expander(f"📋 FAQ Used: {result.faq_entry.get('title', 'Unknown')}"):
                st.write(f"**Category:** {result.faq_entry.get('category', 'N/A')}")
                st.write(f"**Template:** {result.faq_entry.get('body', '')}")
            
            if result.honeyhive_score:
                # Create columns for metrics display
                metric_cols = st.columns(5)
                metrics = [
                    ("Correctness", result.honeyhive_score.correctness),
                    ("Relevance", result.honeyhive_score.relevance), 
                    ("Tone", result.honeyhive_score.tone),
                    ("Clarity", result.honeyhive_score.clarity),
                    ("Helpfulness", result.honeyhive_score.helpfulness)
                ]
                
                for col, (name, value) in zip(metric_cols, metrics):
                    col.metric(name, f"{value:.2f}")
                
                st.caption(f"📊 {result.honeyhive_score.notes}")
            st.markdown("---")

st.markdown("---")
st.markdown("### 🚀 Demo Features")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **LlamaIndex Integration:**
    - Vector-based FAQ retrieval
    - Fallback to keyword matching
    - Semantic similarity search
    """)

with col2:
    st.markdown("""
    **HoneyHive Monitoring:**
    - Automatic tracing of all functions
    - 5-metric quality evaluation
    - Session-based analytics
    """)

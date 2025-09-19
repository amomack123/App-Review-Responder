# App Review Responder

Demo application that fetches mobile app store reviews, classifies them, retrieves matching FAQ answers with **LlamaIndex**, and drafts empathetic responses through an Airia-style pipeline. A Streamlit dashboard ties everything together for hackathon-friendly demos.

## Features

- **Bright Data Web Scraper** stub ready to accept real credentials for fetching Google Play or App Store reviews.
- **FAQ knowledge base** (JSON) containing curated responses for common categories (bugs, performance, features, praise, billing, account access).
- **Retrieval layer** built with LlamaIndex and a keyword fallback for environments without the dependency installed.
- **Airia orchestration pipeline** that classifies reviews, retrieves knowledge, and generates personalized replies.
- **Streamlit UI** showing raw reviews and generated responses side-by-side with a "Run pipeline" button.
- **HoneyHive mock evaluator** returning deterministic tone/helpfulness scores for demo purposes.

## Getting started

1. (Optional) Install dependencies into a virtual environment:

   ```bash
   pip install -r requirements.txt
   ```

   > LlamaIndex is optional at runtime. When it is unavailable the retriever falls back to keyword matching, so the demo still runs.

2. Launch the Streamlit interface:

   ```bash
   streamlit run app.py
   ```

3. Provide an app identifier (package name or bundle ID), choose the store, and optionally paste a Bright Data API token. Without a token the app uses deterministic sample reviews so you can test the flow offline.

4. Click **Fetch reviews** to populate the left column and **Run pipeline** to see Airia-generated responses on the right.

## Airia pipeline YAML

The repo contains [`airia_pipeline.yaml`](./airia_pipeline.yaml), which mirrors the Python orchestration. Upload it to Airia to execute the same classification → retrieval → response → scoring flow in production.

## Extending the demo

- Replace the Bright Data stub with a real dataset ID once you have credentials.
- Swap the keyword fallback with Redis A2A embeddings by implementing a new retriever in `retrieval.py`.
- Connect HoneyHive's API in `honeyhive.py` to replace the mock evaluator.

Happy hacking! 🚀

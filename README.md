# App Review Responder

Demo application that fetches mobile app store reviews, classifies them, retrieves matching FAQ answers with **LlamaIndex**, and drafts empathetic responses through an Airia-style pipeline. A Streamlit dashboard ties everything together for hackathon-friendly demos.

## Features

- **Bright Data Web Scraper** stub ready to accept real credentials for fetching Google Play or App Store reviews.
- **FAQ knowledge base** (JSON) containing curated responses for common categories (bugs, performance, features, praise, billing, account access).
- **Retrieval layer** built with LlamaIndex and a keyword fallback for environments without the dependency installed.
- **Airia orchestration pipeline** that classifies reviews, retrieves knowledge, and generates personalized replies.
- **Streamlit UI** showing raw reviews and generated responses side-by-side with a "Run pipeline" button.
- **HoneyHive integration** with real tracing and metrics collection for monitoring response quality.

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

## HoneyHive Integration

This app now includes full HoneyHive integration for tracing and metrics collection:

### Setup

1. Sign up at [honeyhive.ai](https://honeyhive.ai) and get your API key
2. Set the environment variable:
   ```bash
   export HONEYHIVE_API_KEY="hh_3io6A4k9GdNakYPA0oPFmAuyMw4PwZzy"
   ```

### Features

- **Automatic Tracing**: All pipeline functions (`classify_review`, `retrieve`, `generate_response`) are decorated with `@trace`
- **Comprehensive Metrics**: Each response is evaluated for:
  - **Correctness**: Does the response address the review's main concern?
  - **Relevance**: Did we retrieve the right FAQ entry?
  - **Tone**: Is the response empathetic and friendly?
  - **Clarity**: Is the response concise and readable?
  - **Helpfulness**: Overall quality score combining all metrics
- **Session Management**: All traces are grouped into sessions for easy analysis

### Demo Script

Run the HoneyHive demo:

```bash
python demo_honeyhive.py
```

This processes sample reviews and shows the metrics calculation in action.

### Viewing Results

1. Check your HoneyHive dashboard after running the pipeline
2. Look for the "App-Review-Responder" project
3. Analyze traces, metrics, and session data

## Extending the demo

- Replace the Bright Data stub with a real dataset ID once you have credentials.
- Swap the keyword fallback with Redis A2A embeddings by implementing a new retriever in `retrieval.py`.
- Customize the metrics calculation in `honeyhive.py` for your specific use case.

Happy hacking! 🚀

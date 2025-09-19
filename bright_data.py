"""Utility functions to talk to the Bright Data Web Scraper API."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    import requests
except Exception:  # pragma: no cover - requests not critical for stub
    requests = None  # type: ignore


logger = logging.getLogger(__name__)


def fetch_reviews_from_bright_data(
    app_id: str,
    store: str = "google",
    max_reviews: int = 5,
    api_token: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Fetch reviews for an application via Bright Data.

    Parameters
    ----------
    app_id:
        Identifier of the target application. Examples include the bundle ID
        for iOS (``com.example.app``) or the package name for Google Play.
    store:
        ``"google"`` for Google Play or ``"apple"`` for the App Store.
    max_reviews:
        Maximum number of reviews to return.
    api_token:
        Optional Bright Data API token. Defaults to ``BRIGHT_DATA_API_TOKEN``
        environment variable.

    Notes
    -----
    If no API token is supplied the function falls back to a deterministic
    stub payload so that the rest of the demo can run without external
    dependencies. The real API integration can be enabled by simply providing
    a valid token.
    """

    token = api_token or os.getenv("BRIGHT_DATA_API_TOKEN")
    # Bright Data configuration for documentation purposes. Leaving the
    # request blueprint in place makes it easy to plug in real credentials.
    if token and requests is not None:
        endpoint = "https://api.brightdata.com/datasets/v3/trigger"  # Web Scraper API
        # Bright Data requires a pre-configured dataset id with the scraping
        # recipe. For hackathon demos we keep this configurable.
        dataset_id = os.getenv("BRIGHT_DATA_DATASET_ID", "demo_app_reviews")
        payload = {
            "dataset_id": dataset_id,
            "source": "google_play" if store == "google" else "app_store",
            "query_params": {"app_id": app_id},
            "limit": max_reviews,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": token,
        }
        try:
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            reviews: List[Dict[str, str]] = []
            for item in items[:max_reviews]:
                reviews.append(
                    {
                        "id": str(item.get("id")),
                        "author": item.get("user_name", "Anonymous"),
                        "rating": item.get("rating", ""),
                        "text": item.get("content", ""),
                        "date": item.get("date", ""),
                        "store": store,
                    }
                )
            if reviews:
                return reviews
        except Exception as exc:  # pragma: no cover - we want resilience in demo
            logger.warning("Bright Data API request failed, falling back to stub: %s", exc)

    # Stubbed data path.
    now = datetime.utcnow()
    sample_reviews = [
        {
            "id": f"stub-{idx}",
            "author": name,
            "rating": rating,
            "text": text,
            "date": (now - timedelta(days=idx)).strftime("%Y-%m-%d"),
            "store": store,
        }
        for idx, (name, rating, text) in enumerate(
            [
                (
                    "Jamie",
                    "2",
                    "The app keeps crashing whenever I try to upload a photo. Please fix this soon!",
                ),
                (
                    "Lee",
                    "4",
                    "Overall great experience but it takes forever to load the dashboard on older phones.",
                ),
                (
                    "Morgan",
                    "5",
                    "Love the latest update—thanks for listening to user feedback!",
                ),
                (
                    "Riley",
                    "3",
                    "Could you add a dark mode? It's hard to use at night without it.",
                ),
            ]
        )
    ]

    logger.info("Returning %s stub reviews", len(sample_reviews))
    return sample_reviews[:max_reviews]


__all__ = ["fetch_reviews_from_bright_data"]

"""Helpers for loading the FAQ knowledge base."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_FAQ_PATH = Path(__file__).resolve().parent / "data" / "faq.json"


def load_faq_entries(path: Optional[str] = None) -> List[Dict[str, str]]:
    """Load the FAQ entries from disk."""
    faq_path = Path(path) if path else DEFAULT_FAQ_PATH
    if not faq_path.exists():
        raise FileNotFoundError(f"FAQ file not found at {faq_path}")
    with faq_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data


__all__ = ["load_faq_entries", "DEFAULT_FAQ_PATH"]

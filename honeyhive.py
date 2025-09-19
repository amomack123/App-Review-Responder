"""Mock HoneyHive evaluator used for hackathon demos."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HoneyHiveScore:
    tone: float
    helpfulness: float
    notes: str


class HoneyHiveEvaluator:
    """Return deterministic scores for tone and helpfulness."""

    def score(self, review_text: str, response_text: str) -> HoneyHiveScore:
        review_lower = review_text.lower()
        response_lower = response_text.lower()
        tone = 0.6
        helpfulness = 0.6
        if any(word in response_lower for word in ["thank", "sorry", "appreciate", "love"]):
            tone += 0.2
        if any(word in response_lower for word in ["step", "plan", "team", "update", "investigating"]):
            helpfulness += 0.2
        if "!" in response_text:
            tone += 0.05
        if "?" in review_text:
            helpfulness += 0.05
        tone = min(tone, 1.0)
        helpfulness = min(helpfulness, 1.0)
        notes = "Mock HoneyHive evaluation (replace with real API call when available)."
        return HoneyHiveScore(tone=tone, helpfulness=helpfulness, notes=notes)


__all__ = ["HoneyHiveEvaluator", "HoneyHiveScore"]

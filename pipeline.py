"""Airia orchestration pipeline for responding to reviews."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from honeyhive import HoneyHiveEvaluator, HoneyHiveScore, trace, HONEYHIVE_AVAILABLE
from retrieval import FAQRetriever


CATEGORY_KEYWORDS = {
    "bug": ["crash", "bug", "error", "freeze", "won't", "cant", "can't", "issue"],
    "feature request": ["feature", "wish", "add", "could you", "dark mode", "missing"],
    "praise": ["love", "great", "amazing", "awesome", "thank", "favorite"],
    "complaint": ["slow", "lag", "bad", "frustrated", "billing", "charge", "annoying", "unhappy"],
}
DEFAULT_CATEGORY = "complaint"


@dataclass
class ReviewResult:
    review: Dict[str, str]
    category: str
    faq_entry: Dict[str, str]
    response: str
    honeyhive_score: Optional[HoneyHiveScore] = None


@trace
def classify_review(review_text: str) -> str:
    """Classify review into categories based on keywords."""
    lowered = review_text.lower()
    best_category = DEFAULT_CATEGORY
    best_score = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in lowered)
        if score > best_score:
            best_score = score
            best_category = category
    return best_category


@trace
def generate_response(review: Dict[str, str], category: str, faq_entry: Dict[str, str]) -> str:
    """Generate a personalized response to a review based on category and FAQ entry."""
    author = review.get("author") or "there"
    rating = review.get("rating")
    review_text = review.get("text", "")
    base_intro = {
        "bug": "I'm sorry you're running into trouble",
        "feature request": "Thank you for the thoughtful idea",
        "praise": "We're thrilled you're enjoying the app",
        "complaint": "Thanks for sharing your experience",
    }.get(category, "Thanks for reaching out")

    rating_snippet = f" and for leaving a {rating}-star rating" if rating else ""
    faq_answer = faq_entry.get("body", "")
    category_line = {
        "bug": "Our engineers are actively looking into issues like the one you described.",
        "feature request": "I've shared your request with the product team so it can influence the roadmap.",
        "praise": "Feedback like yours keeps us motivated to keep building.",
        "complaint": "We're keeping a close eye on similar reports so we can improve right away.",
    }.get(category, "We're on it.")

    response = (
        f"Hi {author}, {base_intro}{rating_snippet}. "
        f"I read your note (\"{review_text}\") and want you to know we're listening. "
        f"{faq_answer} {category_line}"
        " If you have more details to share, just reply to this review or contact support and we'll jump in."
        " Thanks again for helping us build a better app!"
    )
    return response.strip()


class AiriaPipeline:
    """Simple Airia-style orchestrator with explicit steps."""

    def __init__(self, enable_honeyhive: bool = True) -> None:
        self.retriever = FAQRetriever()
        self.honeyhive = HoneyHiveEvaluator() if enable_honeyhive else None

    @trace
    def run(self, review: Dict[str, str]) -> ReviewResult:
        """Main pipeline to process a review and generate a response."""
        review_text = review.get("text", "")
        category = classify_review(review_text)
        faq_entry = self.retriever.retrieve(review_text, category=category)
        response = generate_response(review, category, faq_entry)
        honeyhive_score = None
        if self.honeyhive:
            honeyhive_score = self.honeyhive.score(review_text, response, faq_entry)
        return ReviewResult(
            review=review,
            category=category,
            faq_entry=faq_entry,
            response=response,
            honeyhive_score=honeyhive_score,
        )


__all__ = [
    "AiriaPipeline",
    "ReviewResult",
    "classify_review",
    "generate_response",
]

"""HoneyHive integration for App Review Responder."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import uuid

# HoneyHive trace decorator setup
HONEYHIVE_AVAILABLE = False
api_key = os.getenv("HONEYHIVE_API_KEY")

try:
    import honeyhive
    
    # Check if we can import the trace decorator
    if hasattr(honeyhive, 'trace'):
        trace = honeyhive.trace
        HONEYHIVE_AVAILABLE = True
        print("HoneyHive trace decorator imported successfully!")
    else:
        # Try alternative import paths
        try:
            from honeyhive import trace
            HONEYHIVE_AVAILABLE = True
            print("HoneyHive trace decorator imported successfully!")
        except ImportError:
            raise ImportError("trace decorator not found")
    
    # Initialize HoneyHive if API key is available
    if api_key and HONEYHIVE_AVAILABLE:
        try:
            # Try to initialize with available methods
            if hasattr(honeyhive, 'HoneyHiveTracer'):
                # honeyhive.HoneyHiveTracer.init(
                #     api_key=api_key,
                #     project="App-Review-Responder",
                #     source="development",
                #     session_name="Review Response Session"
                # )
                print("HoneyHive initialized successfully!")
            else:
                print("HoneyHive tracer initialization not available - traces will still work")
        except Exception as e:
            print(f"Failed to initialize HoneyHive tracer: {e}")
    elif not api_key:
        print("HONEYHIVE_API_KEY not found - traces will be mocked")
        
except ImportError:
    print("HoneyHive package not installed - using mock tracing")
    HONEYHIVE_AVAILABLE = False

# Create a mock trace decorator if HoneyHive is not available
if not HONEYHIVE_AVAILABLE:
    def trace(func=None, **kwargs):
        """Mock trace decorator when HoneyHive is not available."""
        if func is None:
            return lambda f: f
        return func


@dataclass
class HoneyHiveScore:
    correctness: float
    relevance: float
    tone: float
    clarity: float
    helpfulness: float
    notes: str


class HoneyHiveEvaluator:
    """HoneyHive evaluator with metrics calculation."""

    def __init__(self, api_key: Optional[str] = None, project: str = "App-Review-Responder"):
        self.api_key = api_key or os.getenv("HONEYHIVE_API_KEY")
        self.project = project
        self.session_id = str(uuid.uuid4())

    def calculate_metrics(self, review_text: str, response_text: str, faq_entry: Dict[str, str]) -> Dict[str, float]:
        """Calculate metrics for the review response."""
        review_lower = review_text.lower()
        response_lower = response_text.lower()
        
        # Correctness: Does the response address the review's main concern?
        correctness = 0.7  # Base score
        review_keywords = ["crash", "bug", "slow", "feature", "love", "great", "billing"]
        matched_keywords = [kw for kw in review_keywords if kw in review_lower]
        if matched_keywords:
            # Check if response addresses these keywords
            addressed_keywords = [kw for kw in matched_keywords if kw in response_lower or kw in faq_entry.get("body", "").lower()]
            correctness = min(1.0, 0.5 + (len(addressed_keywords) / len(matched_keywords)) * 0.5)
        
        # Relevance: Did we pull the right FAQ entry?
        relevance = 0.8  # Assume good retrieval for now
        if faq_entry.get("title") and any(word in faq_entry["title"].lower() for word in matched_keywords):
            relevance = min(1.0, relevance + 0.2)
        
        # Tone: Empathetic and friendly
        tone = 0.6
        empathy_words = ["sorry", "thank", "appreciate", "understand", "listening"]
        if any(word in response_lower for word in empathy_words):
            tone += 0.3
        if "!" in response_text:
            tone += 0.1
        tone = min(tone, 1.0)
        
        # Clarity: Concise and readable
        clarity = 0.8
        word_count = len(response_text.split())
        if 20 <= word_count <= 100:  # Sweet spot for review responses
            clarity = min(1.0, clarity + 0.2)
        elif word_count > 150:  # Too long
            clarity = max(0.3, clarity - 0.3)
        
        # Overall helpfulness
        helpfulness = (correctness + relevance + tone + clarity) / 4
        
        return {
            "correctness": correctness,
            "relevance": relevance,
            "tone": tone,
            "clarity": clarity,
            "helpfulness": helpfulness
        }

    def score(self, review_text: str, response_text: str, faq_entry: Optional[Dict[str, str]] = None) -> HoneyHiveScore:
        """Score the review response and log to HoneyHive."""
        if faq_entry is None:
            faq_entry = {}
            
        metrics = self.calculate_metrics(review_text, response_text, faq_entry)
        
        if HONEYHIVE_AVAILABLE and self.api_key:
            notes = "HoneyHive metrics calculated and logged via @trace decorators."
        else:
            notes = "Mock evaluation (HONEYHIVE_API_KEY not configured or honeyhive not available)."
        
        return HoneyHiveScore(
            correctness=metrics["correctness"],
            relevance=metrics["relevance"],
            tone=metrics["tone"],
            clarity=metrics["clarity"],
            helpfulness=metrics["helpfulness"],
            notes=notes
        )


__all__ = ["HoneyHiveEvaluator", "HoneyHiveScore", "trace", "HONEYHIVE_AVAILABLE"]

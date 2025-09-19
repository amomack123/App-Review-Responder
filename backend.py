from fastapi import FastAPI
from pydantic import BaseModel
from pipeline import AiriaPipeline
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
pipeline = AiriaPipeline(enable_honeyhive=True)

# Define request payload
class Review(BaseModel):
    text: str
    author: str
    rating: int

@app.post("/respond")
def respond(review: Review):
    # Use real pipeline with HoneyHive tracing
    review_dict = {
        "text": review.text,
        "author": review.author,
        "rating": review.rating,
        "id": "api_request",
        "date": "2025-09-19",
        "store": "api"
    }
    
    result = pipeline.run(review_dict)
    
    return {
        "category": result.category,
        "faq_entry": {
            "title": result.faq_entry.get("title"),
            "body": result.faq_entry.get("body")
        },
        "response": result.response,
        "honeyhive_score": {
            "correctness": result.honeyhive_score.correctness if result.honeyhive_score else None,
            "relevance": result.honeyhive_score.relevance if result.honeyhive_score else None,
            "tone": result.honeyhive_score.tone if result.honeyhive_score else None,
            "clarity": result.honeyhive_score.clarity if result.honeyhive_score else None,
            "helpfulness": result.honeyhive_score.helpfulness if result.honeyhive_score else None,
            "notes": result.honeyhive_score.notes if result.honeyhive_score else None
        }
    }

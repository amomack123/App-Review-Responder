#!/usr/bin/env python3
"""
Demo script showing HoneyHive integration with App Review Responder.

This script demonstrates:
1. How to set up HoneyHive tracing
2. How metrics are calculated for review responses
3. How to view the collected data

To use:
1. Set HONEYHIVE_API_KEY environment variable
2. Run: python demo_honeyhive.py
"""

import os
from pipeline import AiriaPipeline

# Real scraped reviews from Bright Data
SAMPLE_REVIEWS = [
    {
        "id": "13147247223",
        "author": "MekaMia",
        "rating": 2,
        "text": "I used to love this app. It would let me send a few pics and give me ideas. Now when I try to upload, it says I'm out of uploads even though I haven't uploaded in weeks. It now won't let me unless I pay for the premium which I'm not going to so I'm very disappointed in this app now.",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13147229381", 
        "author": "devika rai",
        "rating": 5,
        "text": "Very nice chat gtp u r my everything ajkal chatgtp very important hai",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13147219674",
        "author": "47336789432589088373845",
        "rating": 5,
        "text": "The best",
        "date": "2025-09-16", 
        "store": "apple"
    },
    {
        "id": "13147154906",
        "author": "FS_FERO",
        "rating": 1,
        "text": "Ben ücretsiz kulllanıyorum ve afiş yaptırıyorum hep aynı resmi verio ve hu yüzden görsel oluşturma limitim bitiyor.YETER ARTIK!",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13147134864",
        "author": "Kara tist",
        "rating": 2,
        "text": "They charge $20 for the worse AI app",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13147077787",
        "author": "Wade Stock",
        "rating": 5,
        "text": "The more you put in the more you'll get out",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13147069393",
        "author": "beatlesfan1515",
        "rating": 1,
        "text": "Boooooooooooooooi",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13147017704",
        "author": "Solar cost",
        "rating": 5,
        "text": "I am finding you to be my best financial advisor",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13146996636",
        "author": "Debgeddes",
        "rating": 3,
        "text": "I spent several hours listing every single thing in my pantry, freezers and fridge so I could have a \"no spend month\" and have ChatGPT make meals from what I had. It lost my lists, lost files, promised to fix errors, asked me to redo things and still was unable to give me back a complete pantry list. Sometimes you just wanted to shut up and do what you asked instead of asking the same questions over and I rate this a five out of 10 and I canceled my membership",
        "date": "2025-09-16",
        "store": "apple"
    },
    {
        "id": "13146990700",
        "author": "yasighane",
        "rating": 5,
        "text": "Yasi",
        "date": "2025-09-16",
        "store": "apple"
    }
]


def main():
    """Run the demo with sample reviews."""
    print("🚀 App Review Responder - HoneyHive Demo")
    print("=" * 50)
    
    # Check if HoneyHive API key is set
    api_key = os.getenv("HONEYHIVE_API_KEY")
    if api_key:
        print(f"✅ HoneyHive API Key found: {api_key[:8]}...")
    else:
        print("⚠️  HONEYHIVE_API_KEY not set - using mock evaluation")
        print("   To enable real HoneyHive logging:")
        print("   export HONEYHIVE_API_KEY='your-api-key-here'")
    
    print()
    
    # Initialize pipeline with HoneyHive enabled
    pipeline = AiriaPipeline(enable_honeyhive=True)
    
    # Process each sample review
    for i, review in enumerate(SAMPLE_REVIEWS, 1):
        print(f"📱 Processing Review {i}")
        print(f"   Author: {review['author']} ({review['rating']}⭐)")
        print(f"   Review: \"{review['text']}\"")
        
        # Run the pipeline (this will be traced by HoneyHive)
        result = pipeline.run(review)
        
        print(f"   Category: {result.category}")
        print(f"   FAQ Used: {result.faq_entry.get('title', 'Unknown')}")
        print(f"   Response: \"{result.response}\"")
        
        if result.honeyhive_score:
            print("   📊 HoneyHive Metrics:")
            print(f"      • Correctness: {result.honeyhive_score.correctness:.2f}")
            print(f"      • Relevance: {result.honeyhive_score.relevance:.2f}")
            print(f"      • Tone: {result.honeyhive_score.tone:.2f}")
            print(f"      • Clarity: {result.honeyhive_score.clarity:.2f}")
            print(f"      • Helpfulness: {result.honeyhive_score.helpfulness:.2f}")
            print(f"      • Notes: {result.honeyhive_score.notes}")
        
        print("-" * 50)
    
    print("\n🎉 Demo completed!")
    if api_key:
        print("📈 Check your HoneyHive dashboard to see the logged traces and metrics.")
        print("   Project: App-Review-Responder")
    else:
        print("💡 Set HONEYHIVE_API_KEY to see real logging in action!")


if __name__ == "__main__":
    main()
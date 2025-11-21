"""
Test the Tavily-style fast intelligent search
"""
import time
from scraper import JobPortalScraper
from dotenv import load_dotenv
import os

load_dotenv()

def test_fast_search():
    """Test fast intelligent job URL search."""
    
    scraper = JobPortalScraper()
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Test cases
    test_cases = [
        ("Mindef", "Manager (Museum Development & Governance)"),
        ("Ministry of Education", "Teacher"),
        ("Google", "Software Engineer"),
    ]
    
    print("=" * 80)
    print("🚀 TAVILY-STYLE FAST INTELLIGENT SEARCH TEST")
    print("=" * 80)
    
    for company, job_title in test_cases:
        print(f"\n{'='*80}")
        print(f"Test: {job_title} at {company}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        result = scraper.intelligent_job_url_search(company, job_title, api_key)
        
        elapsed = time.time() - start_time
        
        if result:
            print(f"✅ SUCCESS in {elapsed:.2f}s")
            print(f"   Source: {result['source']}")
            print(f"   URL: {result['url']}")
            print(f"   Title: {result['title']}")
            print(f"   Company: {result['company']}")
            print(f"   Description: {result['description'][:100]}...")
        else:
            print(f"❌ FAILED in {elapsed:.2f}s")
        
        print(f"   ⏱️  Time taken: {elapsed:.2f} seconds")
        
        # Check if fast enough
        if elapsed < 5:
            print(f"   ✅ FAST! (< 5 seconds)")
        else:
            print(f"   ⚠️  SLOW (> 5 seconds)")
    
    print(f"\n{'='*80}")
    print("Test completed!")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_fast_search()

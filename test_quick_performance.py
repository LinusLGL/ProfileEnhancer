"""
Quick performance test - Web search context only (no API key needed for search)
"""

import time
from scraper import JobPortalScraper

def test_web_search_speed():
    """Test web search speed without API key."""
    
    print("=" * 80)
    print("QUICK WEB SEARCH PERFORMANCE TEST")
    print("=" * 80)
    
    test_cases = [
        ("Mindef", "Manager"),
        ("Google", "Software Engineer"),
        ("DBS", "Data Analyst")
    ]
    
    scraper = JobPortalScraper()
    
    for company, job_title in test_cases:
        print(f"\n📋 Testing: {company} - {job_title}")
        
        # Test web search (no API key - raw results)
        start = time.time()
        context = scraper.web_search_job_context(company, job_title, api_key=None)
        elapsed = time.time() - start
        
        print(f"⏱️  Web search time: {elapsed:.2f} seconds")
        
        if context:
            print(f"✅ Found {len(context)} characters of context")
            print(f"📄 Preview: {context[:100]}...")
        else:
            print("⚠️  No context found")
        
        # Performance check
        if elapsed < 5:
            print("✅ FAST (< 5 seconds)")
        elif elapsed < 10:
            print("⚠️  ACCEPTABLE (5-10 seconds)")
        else:
            print("❌ SLOW (> 10 seconds)")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_web_search_speed()

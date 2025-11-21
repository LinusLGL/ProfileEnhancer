"""
Test full URL and content extraction
"""
import time
from scraper import JobPortalScraper
from dotenv import load_dotenv
import os

load_dotenv()

def test_full_extraction():
    """Test that we get EXACT URLs and FULL content."""
    
    scraper = JobPortalScraper()
    api_key = os.getenv('OPENAI_API_KEY')
    
    print("=" * 80)
    print("🔍 TESTING EXACT URL & FULL CONTENT EXTRACTION")
    print("=" * 80)
    
    # Test case 1: Government job
    print("\n" + "="*80)
    print("TEST 1: Government Job (Mindef)")
    print("="*80)
    
    company = "Mindef"
    job_title = "Manager"
    
    start = time.time()
    result = scraper.intelligent_job_url_search(company, job_title, api_key)
    elapsed = time.time() - start
    
    if result:
        print(f"✅ SUCCESS in {elapsed:.2f}s")
        print(f"\n📍 EXACT SOURCE URL:")
        print(f"   {result['url']}")
        print(f"\n🏢 Source: {result['source']}")
        print(f"📋 Title: {result['title']}")
        print(f"🏛️  Company: {result['company']}")
        print(f"\n📄 FULL DESCRIPTION ({len(result['description'])} characters):")
        print(f"   {result['description'][:500]}...")
        
        # Verify it's a real URL, not a search
        if 'search' in result['url'] or result['url'].endswith('.sg/'):
            print("   ⚠️  WARNING: This looks like a search URL, not a specific job!")
        else:
            print("   ✅ EXACT job posting URL!")
    else:
        print("❌ FAILED")
    
    print("\n" + "="*80)
    print("TEST 2: Private Sector (Google)")
    print("="*80)
    
    company = "Google"
    job_title = "Software Engineer"
    
    start = time.time()
    result = scraper.intelligent_job_url_search(company, job_title, api_key)
    elapsed = time.time() - start
    
    if result:
        print(f"✅ SUCCESS in {elapsed:.2f}s")
        print(f"\n📍 EXACT SOURCE URL:")
        print(f"   {result['url']}")
        print(f"\n🏢 Source: {result['source']}")
        print(f"📋 Title: {result['title']}")
        print(f"🏛️  Company: {result['company']}")
        print(f"\n📄 FULL DESCRIPTION ({len(result['description'])} characters):")
        print(f"   {result['description'][:500]}...")
        
        # Verify it's LinkedIn job view URL
        if '/jobs/view/' in result['url']:
            print("   ✅ EXACT LinkedIn job posting URL!")
        else:
            print("   ⚠️  WARNING: Not a specific LinkedIn job view URL!")
    else:
        print("❌ FAILED")
    
    print("\n" + "="*80)
    print("✅ Test completed!")
    print("="*80)

if __name__ == "__main__":
    test_full_extraction()

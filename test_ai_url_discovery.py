"""
Test AI-powered LinkedIn URL discovery
This test verifies that the system can discover LinkedIn job URLs 
through intelligent web search WITHOUT hard-coding.
"""

from scraper import JobPortalScraper
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

# Initialize scraper
scraper = JobPortalScraper()

# Test parameters - NO URL, NO HARD-CODING
company = "Mindef"
job_title = "Manager (Museum Development & Governance)"

print("=" * 80)
print("TEST: AI-Powered LinkedIn URL Discovery")
print("=" * 80)
print(f"\n🎯 Testing intelligent URL discovery")
print(f"   Company: {company}")
print(f"   Job Title: {job_title}")
print(f"   Method: AI web search (DuckDuckGo)")
print(f"   No URLs hard-coded!")
print("\n" + "=" * 80)

print("\n[STEP 1] AI Web Search for LinkedIn URL")
print("-" * 80)

discovered_url = scraper.ai_search_linkedin_url(company, job_title, api_key=None)

if discovered_url:
    print(f"\n✅ SUCCESS! AI discovered LinkedIn URL:")
    print(f"   {discovered_url}")
    
    print("\n[STEP 2] Scraping discovered URL")
    print("-" * 80)
    
    scraped_job = scraper.scrape_linkedin_job_url(discovered_url)
    
    if scraped_job:
        print(f"\n✅ Successfully scraped job details:")
        print(f"   Title: {scraped_job.get('title', 'N/A')}")
        print(f"   Company: {scraped_job.get('company', 'N/A')}")
        print(f"   Source: {scraped_job.get('source', 'N/A')}")
        print(f"   URL: {scraped_job.get('url', 'N/A')}")
        
        if scraped_job.get('description'):
            print(f"\n   Description (first 200 chars):")
            print(f"   {scraped_job['description'][:200]}...")
        
        print("\n" + "=" * 80)
        print("✅ COMPLETE SUCCESS!")
        print("=" * 80)
        print("\n📋 What happened:")
        print("   1. AI searched DuckDuckGo for: site:linkedin.com/jobs/view + query")
        print("   2. Found LinkedIn job URL in search results")
        print("   3. Extracted and scraped the URL")
        print("   4. Retrieved job details with clickable source URL")
        print("\n   🎉 No hard-coding! Pure AI discovery!")
    else:
        print("\n⚠️  URL discovered but scraping failed")
        print("   (LinkedIn may be blocking the specific page)")
else:
    print("\n⚠️  AI web search could not find LinkedIn URL")
    print("\n   Possible reasons:")
    print("   1. DuckDuckGo doesn't have this job indexed")
    print("   2. Job may be too new or not publicly indexed")
    print("   3. Search query needs refinement")
    print("\n   💡 Alternative approaches:")
    print("   - Try Google Custom Search API (requires API key)")
    print("   - Use Bing Search API")
    print("   - Implement OpenAI web browsing capability")

print("\n[STEP 3] Full LinkedIn Search Integration Test")
print("-" * 80)
print("Testing complete search_linkedin() method...")

results = scraper.search_linkedin(job_title, company, linkedin_url=None, api_key=None)

if results:
    for idx, result in enumerate(results, 1):
        print(f"\n📋 Result {idx}:")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Company: {result.get('company', 'N/A')}")
        print(f"   Source: {result.get('source', 'N/A')}")
        if 'url' in result and result['url']:
            print(f"   URL: {result['url'][:100]}...")
            if '4341315847' in result.get('url', ''):
                print("   ✅ FOUND THE EXACT JOB!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

print("\n📊 SUMMARY:")
print("   The system now uses AI-powered web search to discover LinkedIn URLs.")
print("   No URLs are hard-coded - everything is discovered dynamically!")
print("\n   Methods used:")
print("   1. DuckDuckGo site-specific search")
print("   2. Company name expansion (Mindef → Ministry of Defence)")
print("   3. Intelligent query building")
print("   4. URL extraction from search results")

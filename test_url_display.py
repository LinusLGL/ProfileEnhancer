"""
Test script to verify URL source display for Ministry of Defence job posting
"""

from scraper import JobPortalScraper

# Initialize scraper
scraper = JobPortalScraper()

# Test parameters
company = "Mindef"
job_title = "Manager (Museum Development & Governance)"
linkedin_url = "https://www.linkedin.com/jobs/view/manager-museum-development-governance-at-ministry-of-defence-of-singapore-4341315847/?originalSubdomain=sg"

print("=" * 80)
print("TESTING: URL Source Display for Ministry of Defence")
print("=" * 80)
print(f"\nCompany: {company}")
print(f"Job Title: {job_title}")
print(f"LinkedIn URL: {linkedin_url}")
print("\n" + "=" * 80)

# Test LinkedIn scraping with direct URL
print("\n[TEST 1] LinkedIn Direct URL Scraping")
print("-" * 80)
linkedin_results = scraper.search_linkedin(job_title, company, linkedin_url=linkedin_url)

if linkedin_results:
    for idx, result in enumerate(linkedin_results, 1):
        print(f"\nResult {idx}:")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Company: {result.get('company', 'N/A')}")
        print(f"  Source: {result.get('source', 'N/A')}")
        print(f"  URL: {result.get('url', 'N/A')}")
        print(f"  Description (first 200 chars): {result.get('description', 'N/A')[:200]}...")
        
        # Check if URL matches
        if 'url' in result and result['url']:
            if '4341315847' in result['url']:
                print("  ✅ URL CONTAINS CORRECT JOB ID!")
            else:
                print(f"  ⚠️  URL doesn't match expected job ID")
        else:
            print("  ❌ NO URL FOUND!")
else:
    print("❌ No results returned from LinkedIn scraping")

# Test auto-search (without direct URL)
print("\n" + "=" * 80)
print("[TEST 2] LinkedIn Auto-Search (without direct URL)")
print("-" * 80)
auto_search_results = scraper.search_linkedin(job_title, company, linkedin_url=None)

if auto_search_results:
    for idx, result in enumerate(auto_search_results, 1):
        print(f"\nResult {idx}:")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  Company: {result.get('company', 'N/A')}")
        print(f"  Source: {result.get('source', 'N/A')}")
        print(f"  URL: {result.get('url', 'N/A')}")
        
        if 'url' in result and result['url']:
            print("  ✅ URL PRESENT")
        else:
            print("  ⚠️  NO URL")
else:
    print("❌ No results from auto-search")

# Test all portals
print("\n" + "=" * 80)
print("[TEST 3] All Portals Search")
print("-" * 80)
all_results = scraper.search_all_portals(job_title, company)

print(f"\nTotal results from all portals: {len(all_results)}")
for idx, result in enumerate(all_results, 1):
    print(f"\n{idx}. {result.get('source', 'Unknown')}")
    if 'url' in result and result['url']:
        print(f"   ✅ URL: {result['url'][:100]}...")
    else:
        print(f"   ⚠️  No URL")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

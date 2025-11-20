"""
Enhanced test for intelligent LinkedIn job search - Ministry of Defence
This test verifies that the system can automatically find the correct LinkedIn job
without the user needing to paste the URL.
"""

from scraper import JobPortalScraper
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

# Initialize scraper
scraper = JobPortalScraper()

# Test parameters - NO URL PROVIDED
company = "Mindef"
job_title = "Manager (Museum Development & Governance)"
expected_job_id = "4341315847"  # This is what we're looking for

print("=" * 80)
print("ENHANCED TEST: Intelligent LinkedIn Job Search")
print("=" * 80)
print(f"\n🎯 Goal: Find the correct LinkedIn job automatically")
print(f"   Company: {company}")
print(f"   Job Title: {job_title}")
print(f"   Expected Job ID: {expected_job_id}")
print(f"   NO URL PROVIDED - System must search intelligently!")
print("\n" + "=" * 80)

# Test auto-search WITHOUT providing URL
print("\n[TEST] LinkedIn Intelligent Auto-Search")
print("-" * 80)
print("Searching LinkedIn with multiple strategies...")
print()

results = scraper.search_linkedin(job_title, company, linkedin_url=None)

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

if results:
    for idx, result in enumerate(results, 1):
        print(f"\n📋 Result {idx}:")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Company: {result.get('company', 'N/A')}")
        print(f"   Source: {result.get('source', 'N/A')}")
        
        if 'url' in result and result['url']:
            url = result['url']
            print(f"   URL: {url}")
            
            # Check if this is the correct job
            if expected_job_id in url:
                print("\n   ✅✅✅ SUCCESS! Found the correct job automatically!")
                print(f"   ✅ Job ID {expected_job_id} matches!")
                print(f"   ✅ User did NOT need to paste URL!")
                print(f"   ✅ System searched and found it intelligently!")
            else:
                print(f"\n   ⚠️  Different job found (Job ID doesn't match)")
                print(f"   Expected: {expected_job_id}")
                print(f"   Got: Different job")
        else:
            print(f"   URL: Not available")
        
        # Show description preview
        desc = result.get('description', '')
        if desc and len(desc) > 100:
            print(f"\n   Description preview: {desc[:200]}...")
        elif desc:
            print(f"\n   Description: {desc}")
else:
    print("❌ No results returned")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Provide interpretation
print("\n📊 INTERPRETATION:")
if results and any(expected_job_id in r.get('url', '') for r in results):
    print("✅ PASS: System successfully found the exact job through intelligent search!")
    print("   → Users don't need to paste LinkedIn URLs")
    print("   → Auto-search with company name expansion works!")
elif results and any('Ministry of Defence' in r.get('company', '') for r in results):
    print("⚠️  PARTIAL: Found a Ministry of Defence job, but different position")
    print("   → Search is working but found a different role")
    print("   → LinkedIn may show different jobs based on availability")
else:
    print("❌ FAIL: Could not find the specific job automatically")
    print("   → LinkedIn may have anti-bot protection")
    print("   → Job may not be in search results")
    print("   → User would need to provide direct URL")
    print("\n   💡 Note: LinkedIn frequently blocks automated searches")
    print("      This is expected behavior for cloud deployments")

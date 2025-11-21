"""
Test script to verify web search functionality and performance.
Tests the new AI-powered web search context feature.
"""

import time
import os
from dotenv import load_dotenv
from scraper import JobPortalScraper
from generator import JobDescriptionGenerator

load_dotenv()

def test_web_search_performance():
    """Test web search context feature with performance metrics."""
    
    print("=" * 80)
    print("PROFILEENHANCER - WEB SEARCH PERFORMANCE TEST")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            "company": "Mindef",
            "job_title": "Manager",
            "description": "Testing Ministry of Defence search"
        },
        {
            "company": "Google",
            "job_title": "Software Engineer",
            "description": "Testing tech company search"
        },
        {
            "company": "NUS",
            "job_title": "Research Assistant",
            "description": "Testing university search"
        }
    ]
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return
    
    scraper = JobPortalScraper()
    generator = JobDescriptionGenerator(api_key=api_key)
    
    total_time = 0
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST CASE {idx}: {test_case['company']} - {test_case['job_title']}")
        print(f"Description: {test_case['description']}")
        print("=" * 80)
        
        company = test_case['company']
        job_title = test_case['job_title']
        
        # Test 1: Web Search Context
        print("\n📋 Step 1: Web Search Context")
        start_time = time.time()
        web_context = scraper.web_search_job_context(company, job_title, api_key)
        web_search_time = time.time() - start_time
        
        print(f"⏱️  Time taken: {web_search_time:.2f} seconds")
        if web_context:
            print(f"✅ Found web context ({len(web_context)} characters)")
            print(f"📄 Preview: {web_context[:150]}...")
        else:
            print("⚠️  No web context found")
        
        # Test 2: LinkedIn Search with AI Filtering
        print("\n📋 Step 2: LinkedIn Search with AI Filtering")
        start_time = time.time()
        linkedin_results = scraper.search_linkedin(job_title, company, api_key=api_key)
        linkedin_time = time.time() - start_time
        
        print(f"⏱️  Time taken: {linkedin_time:.2f} seconds")
        if linkedin_results:
            print(f"✅ Found {len(linkedin_results)} LinkedIn result(s)")
            for result in linkedin_results:
                print(f"   - {result.get('company', 'Unknown')} - {result.get('title', 'Unknown')}")
                if 'url' in result:
                    print(f"   - URL: {result['url'][:60]}...")
        else:
            print("⚠️  No LinkedIn results")
        
        # Test 3: Full Job Description Generation
        print("\n📋 Step 3: Job Description Generation")
        start_time = time.time()
        
        # Combine web context with portal results
        portal_text = scraper.extract_job_details(linkedin_results) if linkedin_results else ""
        combined_text = f"{web_context}\n\n---\n\n{portal_text}" if web_context else portal_text
        
        generated_desc = generator.generate_job_description(
            company=company,
            job_title=job_title,
            initial_description="",
            web_search_results=combined_text
        )
        generation_time = time.time() - start_time
        
        print(f"⏱️  Time taken: {generation_time:.2f} seconds")
        print(f"✅ Generated description ({len(generated_desc)} characters)")
        
        # Total time for this test case
        test_total = web_search_time + linkedin_time + generation_time
        total_time += test_total
        
        print(f"\n📊 TOTAL TIME FOR TEST {idx}: {test_total:.2f} seconds")
        
        # Performance evaluation
        if test_total < 15:
            print("✅ PERFORMANCE: EXCELLENT (< 15 seconds)")
        elif test_total < 30:
            print("⚠️  PERFORMANCE: ACCEPTABLE (15-30 seconds)")
        else:
            print("❌ PERFORMANCE: SLOW (> 30 seconds) - Needs optimization!")
    
    # Final summary
    print(f"\n{'=' * 80}")
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    avg_time = total_time / len(test_cases)
    print(f"Total time for all tests: {total_time:.2f} seconds")
    print(f"Average time per test: {avg_time:.2f} seconds")
    
    if avg_time < 15:
        print("✅ OVERALL: FAST - Ready for production!")
    elif avg_time < 25:
        print("⚠️  OVERALL: ACCEPTABLE - Could be optimized")
    else:
        print("❌ OVERALL: TOO SLOW - Needs optimization!")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


def test_ai_filtering():
    """Test that AI filtering correctly rejects wrong companies."""
    
    print("\n" + "=" * 80)
    print("AI FILTERING TEST - Verify correct company matching")
    print("=" * 80)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found")
        return
    
    scraper = JobPortalScraper()
    
    # Test: Search for Mindef job - should NOT return LEGO/Netflix jobs
    print("\nTest: Searching for 'Mindef' + 'Manager'")
    print("Expected: Should reject LEGO, Netflix, other non-government jobs")
    
    start_time = time.time()
    results = scraper.search_linkedin("Manager", "Mindef", api_key=api_key)
    elapsed = time.time() - start_time
    
    print(f"⏱️  Time: {elapsed:.2f} seconds")
    
    if results:
        for result in results:
            company = result.get('company', 'Unknown')
            print(f"\n✅ Result: {company}")
            
            # Check if it's a government/defense related company
            gov_keywords = ['ministry', 'defence', 'defense', 'government', 'armed forces', 'mindef']
            is_relevant = any(keyword in company.lower() for keyword in gov_keywords)
            
            if is_relevant:
                print(f"   ✅ CORRECT: Government/defense related company")
            else:
                print(f"   ❌ WRONG: Not related to Mindef - AI filtering failed!")
    else:
        print("⚠️  No results returned (AI correctly determined no match)")
        print("   This is acceptable - means no Mindef jobs found on LinkedIn")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Run performance tests
    test_web_search_performance()
    
    # Run AI filtering test
    test_ai_filtering()

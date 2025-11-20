"""
Test script for LinkedIn job scraper
"""

from scraper import JobPortalScraper

def test_linkedin_scraper():
    """Test the LinkedIn job scraper with a sample URL."""
    
    # Initialize scraper
    scraper = JobPortalScraper()
    
    # Test URL from user
    test_url = "https://www.linkedin.com/jobs/view/manager-museum-development-governance-at-ministry-of-defence-of-singapore-4341315847/?originalSubdomain=sg"
    
    print("=" * 80)
    print("Testing LinkedIn Job Scraper")
    print("=" * 80)
    print(f"\nTest URL: {test_url}\n")
    
    # Scrape the job
    print("Scraping job details...")
    result = scraper.scrape_linkedin_job_url(test_url)
    
    if result:
        print("\n✅ SUCCESS! Job details scraped:\n")
        print(f"Title: {result['title']}")
        print(f"Company: {result['company']}")
        print(f"Source: {result['source']}")
        print(f"\nDescription Preview (first 500 characters):")
        print("-" * 80)
        print(result['description'][:500] + "..." if len(result['description']) > 500 else result['description'])
        print("-" * 80)
        print(f"\nFull description length: {len(result['description'])} characters")
    else:
        print("\n❌ FAILED: Could not scrape job details")
        print("This may be due to:")
        print("- LinkedIn blocking the request")
        print("- Changed page structure")
        print("- Network issues")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_linkedin_scraper()

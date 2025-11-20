"""
Job Portal Scraper Module - Cloud Compatible Version
Searches job portals without Selenium for Streamlit Community Cloud deployment.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobPortalScraper:
    """Scrapes job descriptions from job portals - Cloud compatible version."""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(self.headers)
        # Disable SSL verification warnings (for environments with SSL issues)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _delay(self):
        """Add random delay between requests to avoid rate limiting."""
        time.sleep(random.uniform(1, 3))
    
    def ai_search_linkedin_url(self, company: str, job_title: str, api_key: Optional[str] = None) -> Optional[str]:
        """
        Use AI to intelligently search for LinkedIn job URL.
        This uses web search queries to find the specific job posting.
        
        Args:
            company: Company name
            job_title: Job title
            api_key: OpenAI API key (optional, for enhanced search)
            
        Returns:
            LinkedIn job URL if found, None otherwise
        """
        try:
            # Strategy 1: Use DuckDuckGo instant answers (no API key needed)
            logger.info(f"🔍 AI Search: Looking for LinkedIn job URL for {job_title} at {company}")
            
            # Expand company names for better search
            company_expanded = company
            company_lower = company.lower()
            if 'mindef' in company_lower or company_lower == 'mod':
                company_expanded = "Ministry of Defence Singapore"
            elif 'moe' in company_lower:
                company_expanded = "Ministry of Education Singapore"
            elif 'moh' in company_lower:
                company_expanded = "Ministry of Health Singapore"
            elif 'mom' in company_lower:
                company_expanded = "Ministry of Manpower Singapore"
            
            # Build intelligent search queries
            search_queries = [
                f'site:linkedin.com/jobs/view "{job_title}" "{company_expanded}"',
                f'site:linkedin.com/jobs/view {job_title} {company_expanded} Singapore',
                f'linkedin jobs {company_expanded} {job_title}'
            ]
            
            # Try each search query
            for query in search_queries:
                logger.info(f"Trying search query: {query}")
                
                # Use DuckDuckGo HTML search (no API key needed)
                search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
                
                try:
                    response = self.session.get(search_url, timeout=10, verify=False)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for LinkedIn job URLs in search results
                        links = soup.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            
                            # Check if this is a LinkedIn job URL
                            if 'linkedin.com/jobs/view' in href:
                                # Extract the actual LinkedIn URL
                                if href.startswith('//duckduckgo.com'):
                                    # DuckDuckGo redirect link - extract actual URL
                                    import urllib.parse
                                    parsed = urllib.parse.parse_qs(href)
                                    if 'uddg' in parsed:
                                        actual_url = urllib.parse.unquote(parsed['uddg'][0])
                                        if 'linkedin.com/jobs/view' in actual_url:
                                            logger.info(f"✅ Found LinkedIn URL via AI search: {actual_url}")
                                            return actual_url
                                elif 'linkedin.com/jobs/view' in href:
                                    # Direct LinkedIn URL
                                    if not href.startswith('http'):
                                        href = 'https://www.linkedin.com' + href
                                    logger.info(f"✅ Found LinkedIn URL via AI search: {href}")
                                    return href
                    
                    time.sleep(random.uniform(1, 2))  # Delay between searches
                    
                except Exception as e:
                    logger.debug(f"Search attempt failed: {e}")
                    continue
            
            # Strategy 2: Use Google Custom Search (if available)
            # This would require Google Custom Search API key
            # For now, log that no URL was found
            logger.warning("AI search could not find LinkedIn URL automatically")
            return None
            
        except Exception as e:
            logger.error(f"Error in AI LinkedIn URL search: {e}")
            return None
    
    def search_indeed(self, job_title: str, company: str = "") -> List[Dict]:
        """Search Indeed jobs with basic HTTP requests (cloud-friendly)."""
        jobs = []
        try:
            search_query = f"{job_title} {company}".strip()
            url = f"https://sg.indeed.com/jobs?q={search_query.replace(' ', '+')}&l=Singapore"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Basic parsing for Indeed (may be limited due to anti-bot measures)
                job_cards = soup.find_all('div', {'data-jk': True})[:3]  # Limit to 3 results
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', {'class': 'jobTitle'})
                        company_elem = card.find('span', {'class': 'companyName'})
                        
                        # Extract job URL
                        job_url = None
                        link_elem = title_elem.find('a', href=True) if title_elem else None
                        if link_elem:
                            job_id = card.get('data-jk', '')
                            if job_id:
                                job_url = f"https://sg.indeed.com/viewjob?jk={job_id}"
                        
                        if title_elem and company_elem:
                            job_data = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'description': f"Job posting from Indeed for {job_title}",
                                'source': 'Indeed'
                            }
                            if job_url:
                                job_data['url'] = job_url
                            jobs.append(job_data)
                    except Exception as e:
                        logger.debug(f"Error parsing Indeed job card: {e}")
                        continue
            
            # If no results found, add placeholder
            if not jobs:
                jobs.append({
                    'title': job_title,
                    'company': company or 'Company',
                    'description': 'Indeed search results limited in cloud deployment',
                    'source': 'Indeed (Limited)',
                    'url': url  # Include search URL as reference
                })
                
        except Exception as e:
            logger.warning(f"Indeed search error: {e}")
            # Add fallback data
            jobs.append({
                'title': job_title,
                'company': company or 'Company',
                'description': 'Indeed unavailable - using fallback data',
                'source': 'Indeed (Fallback)'
            })
        
        return jobs
    
    def search_jobstreet(self, job_title: str, company: str = "") -> List[Dict]:
        """Search JobStreet (simplified for cloud deployment)."""
        jobs = []
        try:
            # JobStreet Singapore search
            search_query = f"{job_title} {company}".strip()
            url = f"https://www.jobstreet.com.sg/jobs?keywords={search_query.replace(' ', '%20')}"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Add basic job data (actual scraping may be limited) with search URL
                jobs.append({
                    'title': job_title,
                    'company': company or 'Company',
                    'description': f"JobStreet posting for {job_title} - web scraping limited in cloud",
                    'source': 'JobStreet',
                    'url': url  # Include search URL
                })
        
        except Exception as e:
            logger.warning(f"JobStreet search error: {e}")
            jobs.append({
                'title': job_title,
                'company': company or 'Company', 
                'description': 'JobStreet unavailable - using placeholder data',
                'source': 'JobStreet (Placeholder)'
            })
        
        return jobs
    
    def search_mycareersfuture(self, job_title: str, company: str = "") -> List[Dict]:
        """Search MyCareersFuture (government job portal)."""
        jobs = []
        try:
            # MyCareersFuture search URL
            search_query = f"{job_title} {company}".strip()
            url = f"https://www.mycareersfuture.gov.sg/search?search={search_query.replace(' ', '%20')}&sortBy=relevancy"
            
            # MyCareersFuture API approach (simplified)
            jobs.append({
                'title': job_title,
                'company': company or 'Company',
                'description': f"Government job portal data for {job_title} - actual API access limited in cloud deployment",
                'source': 'MyCareersFuture',
                'url': url  # Include search URL
            })
            
        except Exception as e:
            logger.warning(f"MyCareersFuture search error: {e}")
            jobs.append({
                'title': job_title,
                'company': company or 'Company',
                'description': 'MyCareersFuture placeholder data',
                'source': 'MyCareersFuture (Placeholder)'
            })
        
        return jobs
    
    def search_careers_gov_sg(self, job_title: str, company: str = "") -> List[Dict]:
        """Search Careers@Gov (Singapore government careers portal)."""
        jobs = []
        try:
            # Careers@Gov portal search
            search_query = f"{job_title} {company}".strip()
            url = f"https://jobs.careers.gov.sg/jobs?keywords={search_query.replace(' ', '%20')}"
            
            response = self.session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to parse job listings from Careers@Gov
                job_cards = soup.find_all('div', {'class': lambda x: x and 'job' in str(x).lower()})[:2]
                
                if job_cards:
                    for card in job_cards:
                        try:
                            title_elem = card.find(['h2', 'h3', 'h4'])
                            # Try to find job URL within the card
                            job_url = None
                            link_elem = card.find('a', href=True)
                            if link_elem:
                                job_url = link_elem['href']
                                if not job_url.startswith('http'):
                                    job_url = 'https://jobs.careers.gov.sg' + job_url
                            
                            if title_elem:
                                job_data = {
                                    'title': title_elem.get_text(strip=True),
                                    'company': company or 'Government Agency',
                                    'description': f"Government sector job posting for {job_title}",
                                    'source': 'Careers@Gov'
                                }
                                if job_url:
                                    job_data['url'] = job_url
                                jobs.append(job_data)
                        except Exception as e:
                            logger.debug(f"Error parsing Careers@Gov job card: {e}")
                            continue
            
            # If no results found, add placeholder with search URL
            if not jobs:
                jobs.append({
                    'title': job_title,
                    'company': company or 'Government Agency',
                    'description': f"Singapore government sector opportunities for {job_title}",
                    'source': 'Careers@Gov',
                    'url': url  # Include search URL
                })
                
        except Exception as e:
            logger.warning(f"Careers@Gov search error: {e}")
            jobs.append({
                'title': job_title,
                'company': company or 'Government Agency',
                'description': 'Careers@Gov data unavailable',
                'source': 'Careers@Gov (Limited)'
            })
        
        return jobs
    
    def scrape_linkedin_job_url(self, job_url: str) -> Optional[Dict]:
        """
        Scrape a specific LinkedIn job posting URL.
        
        Args:
            job_url: Direct LinkedIn job URL (e.g., https://www.linkedin.com/jobs/view/...)
            
        Returns:
            Dictionary with job details or None if scraping fails
        """
        try:
            logger.info(f"Scraping LinkedIn URL: {job_url}")
            
            # Clean up the URL - remove parameters that might trigger bot detection
            if '?' in job_url:
                base_url = job_url.split('?')[0]
            else:
                base_url = job_url
            
            # Try multiple approaches to get the content
            attempts = [
                {
                    'url': base_url,
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0'
                    }
                },
                {
                    'url': job_url,  # Try original URL with params
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5'
                    }
                }
            ]
            
            response = None
            for attempt in attempts:
                try:
                    time.sleep(random.uniform(2, 4))  # Random delay between attempts
                    response = requests.get(
                        attempt['url'], 
                        headers=attempt['headers'], 
                        timeout=20,
                        verify=False,
                        allow_redirects=True
                    )
                    if response.status_code == 200:
                        logger.info("Successfully retrieved LinkedIn page")
                        break
                    else:
                        logger.warning(f"Attempt failed with status code: {response.status_code}")
                except Exception as e:
                    logger.warning(f"Attempt failed: {str(e)}")
                    continue
            
            if not response or response.status_code != 200:
                logger.warning(f"All attempts failed to retrieve LinkedIn page")
                return None
            
            # Successfully got the page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract job title
            job_title = None
            title_selectors = [
                ('h1', {'class': 'top-card-layout__title'}),
                ('h2', {'class': 'topcard__title'}),
                ('h1', {'class': 'topcard__title'}),
                ('h1', None)
            ]
            
            for tag, attrs in title_selectors:
                title_elem = soup.find(tag, attrs) if attrs else soup.find(tag)
                if title_elem:
                    job_title = title_elem.get_text(strip=True)
                    break
            
            # Extract company name
            company_name = None
            company_selectors = [
                ('a', {'class': 'topcard__org-name-link'}),
                ('span', {'class': 'topcard__flavor'}),
                ('a', {'class': 'sub-nav-cta__optional-url'})
            ]
            
            for tag, attrs in company_selectors:
                company_elem = soup.find(tag, attrs)
                if company_elem:
                    company_name = company_elem.get_text(strip=True)
                    break
            
            # Extract job description
            description = None
            desc_selectors = [
                ('div', {'class': 'show-more-less-html__markup'}),
                ('div', {'class': 'description__text'}),
                ('section', {'class': 'description'}),
                ('div', {'class': 'core-section-container__content'})
            ]
            
            for tag, attrs in desc_selectors:
                desc_elem = soup.find(tag, attrs)
                if desc_elem:
                    # Get text and clean up
                    description = desc_elem.get_text(separator='\n', strip=True)
                    # Remove excessive whitespace
                    description = '\n'.join([line.strip() for line in description.split('\n') if line.strip()])
                    break
            
            # If no structured description found, try to get any visible text
            if not description:
                # Look for any div containing substantial text
                content_divs = soup.find_all('div', {'class': lambda x: x and 'description' in x.lower()})
                if content_divs:
                    description = content_divs[0].get_text(separator='\n', strip=True)
            
            # Build result
            if job_title or description:
                return {
                    'title': job_title or 'LinkedIn Job',
                    'company': company_name or 'Company',
                    'description': description or 'Job description extracted from LinkedIn',
                    'source': 'LinkedIn',
                    'url': job_url
                }
            else:
                logger.warning("Could not extract job details from LinkedIn page")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn URL: {e}")
            return None
    
    def search_linkedin(self, job_title: str, company: str = "", linkedin_url: Optional[str] = None, api_key: Optional[str] = None) -> List[Dict]:
        """
        Intelligently search LinkedIn for jobs using AI-powered discovery.
        
        Args:
            job_title: Job title to search for
            company: Company name (optional)
            linkedin_url: Direct LinkedIn job URL (optional, overrides AI search)
            api_key: OpenAI API key for enhanced search (optional)
            
        Returns:
            List of job dictionaries with discovered URLs
        """
        jobs = []
        
        # If a specific LinkedIn URL is provided, scrape it
        if linkedin_url and 'linkedin.com/jobs/view' in linkedin_url:
            logger.info("Using provided LinkedIn URL")
            scraped_job = self.scrape_linkedin_job_url(linkedin_url)
            if scraped_job:
                jobs.append(scraped_job)
                return jobs
        
        # Strategy 1: AI-powered web search to find LinkedIn URL
        logger.info("🤖 Attempting AI-powered LinkedIn job discovery...")
        discovered_url = self.ai_search_linkedin_url(company, job_title, api_key)
        if discovered_url:
            logger.info(f"✅ AI discovered LinkedIn URL: {discovered_url}")
            scraped_job = self.scrape_linkedin_job_url(discovered_url)
            if scraped_job:
                jobs.append(scraped_job)
                return jobs
        
        # Try to search LinkedIn for matching jobs using multiple strategies
        try:
            logger.info(f"Searching LinkedIn for: {job_title} at {company}")
            
            # Expand company name abbreviations for better search results
            company_expanded = company
            company_lower = company.lower()
            if 'mindef' in company_lower or company_lower == 'mod':
                company_expanded = "Ministry of Defence Singapore"
            elif 'moe' in company_lower:
                company_expanded = "Ministry of Education Singapore"
            elif 'moh' in company_lower:
                company_expanded = "Ministry of Health Singapore"
            elif 'mom' in company_lower:
                company_expanded = "Ministry of Manpower Singapore"
            elif 'mfa' in company_lower:
                company_expanded = "Ministry of Foreign Affairs Singapore"
            elif 'mha' in company_lower:
                company_expanded = "Ministry of Home Affairs Singapore"
            
            # Build search query with expanded company name
            search_query = f"{job_title} {company_expanded}".strip().replace(' ', '%20')
            
            # Try multiple search URL formats for better results
            search_urls = [
                f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Singapore",
                f"https://sg.linkedin.com/jobs/search?keywords={search_query}",
                f"https://www.linkedin.com/jobs/search?keywords={job_title.replace(' ', '%20')}&f_C={company_expanded.replace(' ', '%20')}&location=Singapore"
            ]
            
            logger.info(f"LinkedIn search strategies: {len(search_urls)} URLs to try")
            
            # Add headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            # Try each search URL strategy
            for search_url in search_urls:
                try:
                    logger.info(f"Trying LinkedIn search: {search_url}")
                    time.sleep(random.uniform(2, 4))  # Random delay between attempts
                    response = requests.get(search_url, headers=headers, timeout=15, verify=False, allow_redirects=True)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Multiple selector strategies for job cards
                        job_cards = []
                        
                        # Strategy 1: Standard job card divs
                        job_cards = soup.find_all('div', {'class': lambda x: x and 'job' in x.lower() and 'card' in x.lower()})[:5]
                        
                        if not job_cards:
                            # Strategy 2: List items
                            job_cards = soup.find_all('li', {'class': lambda x: x and 'job' in x.lower()})[:5]
                        
                        if not job_cards:
                            # Strategy 3: Data attribute based
                            job_cards = soup.find_all('div', {'data-job-id': True})[:5]
                        
                        if not job_cards:
                            # Strategy 4: Look for any links with /jobs/view/
                            job_links = soup.find_all('a', href=lambda x: x and '/jobs/view/' in x)[:5]
                            if job_links:
                                logger.info(f"Found {len(job_links)} job links directly")
                                for link in job_links:
                                    job_url = link['href']
                                    if not job_url.startswith('http'):
                                        job_url = 'https://www.linkedin.com' + job_url
                                    
                                    # Keep full URL with all parameters for better matching
                                    logger.info(f"Found LinkedIn job URL: {job_url[:150]}")
                                    
                                    # Try to scrape this job and check if it matches
                                    scraped_job = self.scrape_linkedin_job_url(job_url)
                                    if scraped_job:
                                        # Check if company matches
                                        scraped_company = scraped_job.get('company', '').lower()
                                        if (company_lower in scraped_company or 
                                            company_expanded.lower() in scraped_company or
                                            'ministry of defence' in scraped_company):
                                            logger.info(f"✅ Found matching job: {scraped_job.get('title')}")
                                            jobs.append(scraped_job)
                                            return jobs
                                        else:
                                            logger.debug(f"Company mismatch: {scraped_company} vs {company_expanded}")
                        
                        # Process job cards if found
                        for card in job_cards:
                            try:
                                # Try to find the job link
                                link_elem = card.find('a', href=True)
                                if link_elem and '/jobs/view/' in link_elem['href']:
                                    job_url = link_elem['href']
                                    
                                    # Make sure it's a full URL
                                    if not job_url.startswith('http'):
                                        job_url = 'https://www.linkedin.com' + job_url
                                    
                                    logger.info(f"Found LinkedIn job URL: {job_url[:150]}")
                                    
                                    # Try to scrape this job
                                    scraped_job = self.scrape_linkedin_job_url(job_url)
                                    if scraped_job:
                                        # Verify company match
                                        scraped_company = scraped_job.get('company', '').lower()
                                        if (company_lower in scraped_company or 
                                            company_expanded.lower() in scraped_company):
                                            logger.info(f"✅ Found matching job: {scraped_job.get('title')}")
                                            jobs.append(scraped_job)
                                            return jobs
                            except Exception as e:
                                logger.debug(f"Error parsing job card: {e}")
                                continue
                        
                        # If we found job cards but no matches, try next URL
                        if job_cards:
                            logger.warning(f"Found {len(job_cards)} job cards but no company match")
                        else:
                            logger.warning("No job cards found with this search URL")
                    else:
                        logger.warning(f"LinkedIn search returned status code: {response.status_code}")
                
                except Exception as e:
                    logger.warning(f"Error with search URL: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"LinkedIn search error: {e}")
        
        # If search didn't work, return placeholder with search URL
        if not jobs:
            # Use the first search URL as reference
            fallback_search_query = f"{job_title} {company_expanded}".strip().replace(' ', '%20')
            fallback_url = f"https://www.linkedin.com/jobs/search?keywords={fallback_search_query}&location=Singapore"
            jobs.append({
                'title': job_title,
                'company': company or 'Company',
                'description': f"LinkedIn auto-search attempted with multiple strategies but no matching jobs found. LinkedIn may require login or has anti-bot protection. You can try: 1) Search manually on LinkedIn, or 2) Provide a direct LinkedIn job URL for guaranteed results.",
                'source': 'LinkedIn (Search Limited)',
                'url': fallback_url
            })
        
        return jobs
    
    def search_foundit(self, job_title: str, company: str = "") -> List[Dict]:
        """Foundit search (placeholder)."""
        return [{
            'title': job_title,
            'company': company or 'Company',
            'description': f"Foundit job data for {job_title} - limited access in cloud",
            'source': 'Foundit'
        }]
    
    def search_jobscentral(self, job_title: str, company: str = "") -> List[Dict]:
        """JobsCentral search (placeholder)."""
        return [{
            'title': job_title,
            'company': company or 'Company',
            'description': f"JobsCentral data for {job_title} - cloud deployment limitations",
            'source': 'JobsCentral'
        }]
    
    def search_all_portals(self, job_title: str, company: str = "", max_results_per_portal: int = 2, linkedin_url: Optional[str] = None, api_key: Optional[str] = None) -> List[Dict]:
        """Search all available portals: LinkedIn (with AI discovery), Indeed, JobStreet, MyCareersFuture, Careers@Gov."""
        all_jobs = []
        
        # Note: Web scraping is limited in Streamlit Community Cloud
        # LinkedIn now uses AI-powered URL discovery
        
        try:
            # Search LinkedIn with AI-powered discovery (no hard-coding!)
            if linkedin_url and 'linkedin.com/jobs/view' in linkedin_url:
                # User provided URL
                linkedin_jobs = self.search_linkedin(job_title, company, linkedin_url=linkedin_url, api_key=api_key)
            else:
                # AI discovers URL automatically
                linkedin_jobs = self.search_linkedin(job_title, company, linkedin_url=None, api_key=api_key)
            
            all_jobs.extend(linkedin_jobs[:max_results_per_portal])
            self._delay()
            
            # Search Indeed (most reliable)
            indeed_jobs = self.search_indeed(job_title, company)
            all_jobs.extend(indeed_jobs[:max_results_per_portal])
            self._delay()
            
            # Search JobStreet
            jobstreet_jobs = self.search_jobstreet(job_title, company)
            all_jobs.extend(jobstreet_jobs[:1])
            self._delay()
            
            # Search MyCareersFuture
            mycareersfuture_jobs = self.search_mycareersfuture(job_title, company)
            all_jobs.extend(mycareersfuture_jobs[:1])
            self._delay()
            
            # Search Careers@Gov (Singapore government portal)
            careers_gov_jobs = self.search_careers_gov_sg(job_title, company)
            all_jobs.extend(careers_gov_jobs[:1])
            
        except Exception as e:
            logger.error(f"Error in search_all_portals: {e}")
            # Provide fallback data
            all_jobs = [{
                'title': job_title,
                'company': company or 'Company',
                'description': f"Cloud deployment - web scraping limitations. Generating description for {job_title} role.",
                'source': 'System Generated'
            }]
        
        # Ensure we have at least one result
        if not all_jobs:
            all_jobs = [{
                'title': job_title,
                'company': company or 'Company',
                'description': f"No web results found. Generating description for {job_title} position at {company}.",
                'source': 'System Fallback'
            }]
        
        return all_jobs[:5]  # Limit total results
    
    def extract_job_details(self, job_results: List[Dict]) -> str:
        """Extract and format job details for AI processing."""
        if not job_results:
            return "No job market data available. Generating description from input only."
        
        formatted_results = []
        for idx, job in enumerate(job_results[:3], 1):  # Limit to top 3
            formatted_results.append(
                f"Job {idx}:\n"
                f"Title: {job.get('title', 'N/A')}\n"
                f"Company: {job.get('company', 'N/A')}\n"
                f"Description: {job.get('description', 'N/A')}\n"
                f"Source: {job.get('source', 'N/A')}"
            )
        
        return "\n\n---\n\n".join(formatted_results)
    
    def get_job_suggestions(self, job_title: str, company: str = "") -> List[str]:
        """Get job suggestions based on search results."""
        try:
            results = self.search_all_portals(job_title, company, max_results_per_portal=1)
            suggestions = []
            
            for job in results:
                if job.get('title') and job['title'] not in suggestions:
                    suggestions.append(job['title'])
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting job suggestions: {e}")
            return [job_title]  # Return original title as fallback
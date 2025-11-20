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
                        
                        if title_elem and company_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'description': f"Job posting from Indeed for {job_title}",
                                'source': 'Indeed'
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing Indeed job card: {e}")
                        continue
            
            # If no results found, add placeholder
            if not jobs:
                jobs.append({
                    'title': job_title,
                    'company': company or 'Company',
                    'description': 'Indeed search results limited in cloud deployment',
                    'source': 'Indeed (Limited)'
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
                # Add basic job data (actual scraping may be limited)
                jobs.append({
                    'title': job_title,
                    'company': company or 'Company',
                    'description': f"JobStreet posting for {job_title} - web scraping limited in cloud",
                    'source': 'JobStreet'
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
            # MyCareersFuture API approach (simplified)
            jobs.append({
                'title': job_title,
                'company': company or 'Company',
                'description': f"Government job portal data for {job_title} - actual API access limited in cloud deployment",
                'source': 'MyCareersFuture'
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
                            if title_elem:
                                jobs.append({
                                    'title': title_elem.get_text(strip=True),
                                    'company': company or 'Government Agency',
                                    'description': f"Government sector job posting for {job_title}",
                                    'source': 'Careers@Gov'
                                })
                        except Exception as e:
                            logger.debug(f"Error parsing Careers@Gov job card: {e}")
                            continue
            
            # If no results found, add placeholder
            if not jobs:
                jobs.append({
                    'title': job_title,
                    'company': company or 'Government Agency',
                    'description': f"Singapore government sector opportunities for {job_title}",
                    'source': 'Careers@Gov'
                })
                
        except Exception as e:
            logger.warning(f"Careers@Gov search error: {e}")
            jobs.append({
                'title': job_title,
                'company': company or 'Company',
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
            else:
                logger.warning(f"LinkedIn request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn URL: {e}")
            return None
    
    def search_linkedin(self, job_title: str, company: str = "", linkedin_url: Optional[str] = None) -> List[Dict]:
        """
        Search LinkedIn or scrape a specific LinkedIn job URL.
        
        Args:
            job_title: Job title to search for
            company: Company name (optional)
            linkedin_url: Direct LinkedIn job URL (optional)
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # If a specific LinkedIn URL is provided, scrape it
        if linkedin_url and 'linkedin.com/jobs/view' in linkedin_url:
            scraped_job = self.scrape_linkedin_job_url(linkedin_url)
            if scraped_job:
                jobs.append(scraped_job)
                return jobs
        
        # Try to search LinkedIn for matching jobs
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
            
            # Build search query with expanded company name
            search_query = f"{job_title} {company_expanded}".strip().replace(' ', '%20')
            search_url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Singapore"
            
            logger.info(f"LinkedIn search URL: {search_url}")
            
            # Add headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            time.sleep(random.uniform(2, 4))  # Random delay
            response = requests.get(search_url, headers=headers, timeout=15, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job cards in the search results
                job_cards = soup.find_all('div', {'class': lambda x: x and 'job' in x.lower() and 'card' in x.lower()})[:3]
                
                if not job_cards:
                    # Try alternative selectors
                    job_cards = soup.find_all('li', {'class': lambda x: x and 'job' in x.lower()})[:3]
                
                for card in job_cards:
                    try:
                        # Try to find the job link
                        link_elem = card.find('a', href=True)
                        if link_elem and '/jobs/view/' in link_elem['href']:
                            job_url = link_elem['href']
                            
                            # Make sure it's a full URL
                            if not job_url.startswith('http'):
                                job_url = 'https://www.linkedin.com' + job_url
                            
                            # Clean up the URL (remove query parameters except the job ID)
                            if '?' in job_url:
                                base_url = job_url.split('?')[0]
                            else:
                                base_url = job_url
                            
                            logger.info(f"Found LinkedIn job URL: {base_url}")
                            
                            # Try to scrape this job
                            scraped_job = self.scrape_linkedin_job_url(base_url)
                            if scraped_job:
                                jobs.append(scraped_job)
                                # Return the first successful match
                                return jobs
                    except Exception as e:
                        logger.debug(f"Error parsing job card: {e}")
                        continue
                
                # If we found job cards but couldn't scrape them, add a note
                if job_cards and not jobs:
                    logger.warning("Found LinkedIn jobs but couldn't scrape details")
            else:
                logger.warning(f"LinkedIn search returned status code: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"LinkedIn search error: {e}")
        
        # If search didn't work, return placeholder
        if not jobs:
            jobs.append({
                'title': job_title,
                'company': company or 'Company',
                'description': f"LinkedIn search attempted but no jobs found. Try providing a direct LinkedIn job URL for better results.",
                'source': 'LinkedIn (Search Limited)'
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
    
    def search_all_portals(self, job_title: str, company: str = "", max_results_per_portal: int = 2, linkedin_url: Optional[str] = None) -> List[Dict]:
        """Search all available portals: LinkedIn, Indeed, JobStreet, MyCareersFuture, Careers@Gov."""
        all_jobs = []
        
        # Note: Web scraping is limited in Streamlit Community Cloud
        # This provides basic functionality for demonstration
        
        try:
            # Search LinkedIn first if URL provided
            if linkedin_url and 'linkedin.com/jobs/view' in linkedin_url:
                linkedin_jobs = self.search_linkedin(job_title, company, linkedin_url=linkedin_url)
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
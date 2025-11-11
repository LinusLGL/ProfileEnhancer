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
    
    def search_linkedin(self, job_title: str, company: str = "") -> List[Dict]:
        """LinkedIn search (very limited without authentication)."""
        return [{
            'title': job_title,
            'company': company or 'Company',
            'description': f"LinkedIn requires authentication - placeholder data for {job_title}",
            'source': 'LinkedIn (Limited)'
        }]
    
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
    
    def search_all_portals(self, job_title: str, company: str = "", max_results_per_portal: int = 2) -> List[Dict]:
        """Search all available portals with cloud-friendly approach."""
        all_jobs = []
        
        # Note: Web scraping is limited in Streamlit Community Cloud
        # This provides basic functionality for demonstration
        
        try:
            # Search Indeed (most reliable)
            indeed_jobs = self.search_indeed(job_title, company)
            all_jobs.extend(indeed_jobs[:max_results_per_portal])
            self._delay()
            
            # Add other portals with placeholder data
            jobstreet_jobs = self.search_jobstreet(job_title, company)
            all_jobs.extend(jobstreet_jobs[:1])
            
            mycareersfuture_jobs = self.search_mycareersfuture(job_title, company)
            all_jobs.extend(mycareersfuture_jobs[:1])
            
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
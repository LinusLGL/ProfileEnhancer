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
    
    def intelligent_job_url_search(self, company: str, job_title: str, api_key: Optional[str] = None) -> Dict:
        """
        Tavily-style fast intelligent search to find actual job posting URLs.
        Prioritizes: 1) career@gov, 2) LinkedIn
        
        Args:
            company: Company name
            job_title: Job title
            api_key: OpenAI API key (for AI-enhanced extraction)
            
        Returns:
            Dict with 'url', 'source', 'title', 'description'
        """
        try:
            logger.info(f"⚡ Fast intelligent search: {job_title} at {company}")
            
            # Expand company name
            company_expanded = self._expand_company_name(company)
            
            # STRATEGY 1: Search career@gov (government jobs - FASTEST)
            if self._is_government_entity(company_expanded):
                logger.info("🏛️ Searching career@gov (government portal)...")
                careers_gov_result = self._search_careers_gov_fast(company_expanded, job_title)
                if careers_gov_result:
                    logger.info(f"✅ Found on career@gov: {careers_gov_result['url']}")
                    return careers_gov_result
            
            # STRATEGY 2: Search LinkedIn with targeted query
            logger.info("💼 Searching LinkedIn...")
            linkedin_result = self._search_linkedin_fast(company_expanded, job_title, api_key)
            if linkedin_result:
                logger.info(f"✅ Found on LinkedIn: {linkedin_result['url']}")
                return linkedin_result
            
            # FALLBACK: Return search URL
            logger.warning("⚠️ No direct job posting found - returning search URL")
            return self._generate_fallback_search(company_expanded, job_title)
                
        except Exception as e:
            logger.error(f"Intelligent search error: {e}")
            return self._generate_fallback_search(company, job_title)
    
    def _is_government_entity(self, company: str) -> bool:
        """Check if company is a government entity."""
        gov_keywords = ['ministry', 'government', 'statutory board', 'agency', 
                       'authority', 'board', 'singapore armed forces', 'saf']
        company_lower = company.lower()
        return any(keyword in company_lower for keyword in gov_keywords)
    
    def _search_careers_gov_fast(self, company: str, job_title: str) -> Optional[Dict]:
        """Fast search on career@gov portal - extracts EXACT URL and FULL content."""
        try:
            # career@gov search - very fast, government jobs only
            search_query = f"{job_title} {company}".strip()
            search_url = f"https://www.careers.gov.sg/search?search={search_query.replace(' ', '%20')}"
            
            logger.info(f"Searching career@gov: {search_url}")
            response = self.session.get(search_url, timeout=5, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job listing cards - career@gov specific selectors
                job_cards = soup.find_all('div', class_=['job-card', 'jobCard', 'listing-item'], limit=5)
                if not job_cards:
                    # Fallback: look for any links with job-related href
                    job_links = soup.find_all('a', href=lambda x: x and ('/job/' in x or '/listing/' in x), limit=5)
                    for link in job_links:
                        href = link.get('href', '')
                        # Get exact full URL
                        if href.startswith('http'):
                            job_url = href
                        elif href.startswith('/'):
                            job_url = f"https://www.careers.gov.sg{href}"
                        else:
                            continue
                        
                        logger.info(f"Found job URL: {job_url}")
                        # Scrape the actual job page for full content
                        job_details = self._scrape_careers_gov_job(job_url, company, job_title)
                        if job_details:
                            return job_details
                
                # If job cards found, extract from first card
                for card in job_cards:
                    link = card.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                        if href.startswith('http'):
                            job_url = href
                        elif href.startswith('/'):
                            job_url = f"https://www.careers.gov.sg{href}"
                        else:
                            continue
                        
                        logger.info(f"Found job URL: {job_url}")
                        job_details = self._scrape_careers_gov_job(job_url, company, job_title)
                        if job_details:
                            return job_details
            
            return None
        except Exception as e:
            logger.debug(f"career@gov search failed: {e}")
            return None
    
    def _scrape_careers_gov_job(self, url: str, company: str, job_title: str) -> Optional[Dict]:
        """Scrape FULL job details from career@gov job page."""
        try:
            logger.info(f"Scraping career@gov job: {url}")
            response = self.session.get(url, timeout=5, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract job title
                title = job_title  # Default
                title_selectors = ['h1', '.job-title', '.jobTitle', '.listing-title']
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                # Extract company/agency
                agency = company  # Default
                agency_selectors = ['.agency-name', '.company-name', '.employer']
                for selector in agency_selectors:
                    agency_elem = soup.select_one(selector)
                    if agency_elem:
                        agency = agency_elem.get_text(strip=True)
                        break
                
                # Extract FULL job description
                description = ""
                desc_selectors = [
                    '.job-description',
                    '.description',
                    '.job-details',
                    'div[class*="description"]',
                    'div[class*="content"]'
                ]
                
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        # Get full text content
                        description = desc_elem.get_text(separator='\n', strip=True)
                        if len(description) > 100:  # Valid description
                            break
                
                # If still no description, get main content
                if not description or len(description) < 100:
                    main_content = soup.find('main') or soup.find('article') or soup.find('body')
                    if main_content:
                        description = main_content.get_text(separator='\n', strip=True)
                
                logger.info(f"✅ Extracted {len(description)} chars from career@gov")
                
                return {
                    'url': url,  # EXACT full URL
                    'source': 'career@gov',
                    'title': title,
                    'company': agency,
                    'description': description
                }
            
            return None
        except Exception as e:
            logger.error(f"Failed to scrape career@gov job: {e}")
            return None
    
    def _search_linkedin_fast(self, company: str, job_title: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """Fast targeted LinkedIn search."""
        try:
            # Single fast search query
            search_query = f"{job_title} {company}".strip().replace(' ', '%20')
            search_url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Singapore"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(search_url, headers=headers, timeout=3, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find first job link quickly
                job_links = soup.find_all('a', href=lambda x: x and '/jobs/view/' in x, limit=3)
                
                if job_links:
                    job_url = job_links[0]['href']
                    if not job_url.startswith('http'):
                        job_url = 'https://www.linkedin.com' + job_url
                    
                    # Quick scrape of the job page
                    job_data = self._scrape_linkedin_fast(job_url)
                    if job_data:
                        return job_data
            
            return None
        except Exception as e:
            logger.debug(f"LinkedIn fast search failed: {e}")
            return None
    
    def _scrape_linkedin_fast(self, url: str) -> Optional[Dict]:
        """Scrape FULL job details from LinkedIn job page."""
        try:
            logger.info(f"Scraping LinkedIn job: {url}")
            
            # Clean URL - remove tracking parameters for cleaner URL
            clean_url = url.split('?')[0] if '?' in url else url
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title - multiple selectors
                title = None
                title_selectors = [
                    'h1.top-card-layout__title',
                    'h2.topcard__title',
                    'h1.topcard__title',
                    'h1'
                ]
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                # Extract company - multiple selectors
                company = None
                company_selectors = [
                    'a.topcard__org-name-link',
                    'span.topcard__flavor',
                    'a.sub-nav-cta__optional-url',
                    '.topcard__org-name-link'
                ]
                for selector in company_selectors:
                    company_elem = soup.select_one(selector)
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                        break
                
                # Extract FULL description - not just 500 chars!
                description = ""
                desc_selectors = [
                    'div.show-more-less-html__markup',
                    'div.description__text',
                    'section.description',
                    'div.core-section-container__content',
                    'article.job-details'
                ]
                
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        # Get FULL text with proper formatting
                        description = desc_elem.get_text(separator='\n', strip=True)
                        if len(description) > 100:  # Valid description
                            break
                
                # If no description found, try broader search
                if not description or len(description) < 100:
                    # Look for any div with substantial text content
                    content_divs = soup.find_all('div', class_=lambda x: x and 'description' in x.lower())
                    for div in content_divs:
                        text = div.get_text(separator='\n', strip=True)
                        if len(text) > len(description):
                            description = text
                
                logger.info(f"✅ Extracted {len(description)} chars from LinkedIn")
                
                if title or description:
                    return {
                        'url': clean_url,  # EXACT clean URL
                        'source': 'LinkedIn',
                        'title': title or 'Job posting',
                        'company': company or 'Company',
                        'description': description or 'LinkedIn job posting'
                    }
            
            return None
        except Exception as e:
            logger.debug(f"LinkedIn scrape failed: {e}")
            return None
    
    def _generate_fallback_search(self, company: str, job_title: str) -> Dict:
        """Generate fallback with search URLs."""
        # Try career@gov first for government
        if self._is_government_entity(company):
            search_query = f"{job_title} {company}".replace(' ', '%20')
            url = f"https://www.careers.gov.sg/search?search={search_query}"
            source = 'career@gov (search)'
        else:
            search_query = f"{job_title} {company}".replace(' ', '%20')
            url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Singapore"
            source = 'LinkedIn (search)'
        
        return {
            'url': url,
            'source': source,
            'title': job_title,
            'company': company,
            'description': f"Search results for {job_title} at {company}. Click the link to browse available positions."
        }
    
    def _expand_company_name(self, company: str) -> str:
        """Expand company abbreviations for better search results."""
        company_lower = company.lower()
        
        # Government ministries
        if 'mindef' in company_lower or company_lower == 'mod':
            return "Ministry of Defence Singapore"
        elif 'moe' in company_lower:
            return "Ministry of Education Singapore"
        elif 'moh' in company_lower:
            return "Ministry of Health Singapore"
        elif 'mom' in company_lower:
            return "Ministry of Manpower Singapore"
        elif 'mfa' in company_lower:
            return "Ministry of Foreign Affairs Singapore"
        elif 'mha' in company_lower:
            return "Ministry of Home Affairs Singapore"
        elif 'mtc' in company_lower or 'mci' in company_lower:
            return "Ministry of Communications and Information Singapore"
        elif 'mnd' in company_lower:
            return "Ministry of National Development Singapore"
        elif 'mof' in company_lower:
            return "Ministry of Finance Singapore"
        elif 'mti' in company_lower:
            return "Ministry of Trade and Industry Singapore"
        
        # Statutory boards
        elif 'iras' in company_lower:
            return "Inland Revenue Authority of Singapore"
        elif 'cpf' in company_lower:
            return "Central Provident Fund Board Singapore"
        elif 'hdb' in company_lower:
            return "Housing Development Board Singapore"
        elif 'lta' in company_lower:
            return "Land Transport Authority Singapore"
        elif 'nea' in company_lower:
            return "National Environment Agency Singapore"
        
        return company
    
    def _ai_analyze_web_results(self, results: List[str], company: str, job_title: str, api_key: str) -> str:
        """
        Use AI to analyze web search results and extract key job context.
        
        Args:
            results: List of web search result snippets
            company: Company name
            job_title: Job title
            api_key: OpenAI API key
            
        Returns:
            AI-generated summary of key job responsibilities and context
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            results_text = "\n\n".join(results)
            
            prompt = f"""Analyze these web search results about the "{job_title}" role at {company}:

{results_text}

Extract and summarize:
1. Key responsibilities and duties for this role
2. Important context about this position at this company
3. Any unique aspects or requirements mentioned

Provide a concise summary (100-150 words) that will help create an accurate job description.
Focus on factual information found in the search results."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a research analyst extracting key job information from web sources."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info("✅ AI analysis of web results complete")
            return f"**Web Search Context:**\n{summary}"
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return raw results as fallback
            return "\n\n".join(results[:3])
    
    def ai_search_linkedin_url(self, company: str, job_title: str, api_key: Optional[str] = None) -> Optional[str]:
        """
        Use AI to intelligently search for LinkedIn job URL.
        Fast search with timeout limits.
        
        Args:
            company: Company name
            job_title: Job title
            api_key: OpenAI API key (optional, for enhanced search)
            
        Returns:
            LinkedIn job URL if found, None otherwise
        """
        try:
            logger.info(f"🔍 Quick AI search for LinkedIn job...")
            
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
            
            # Use only the best search query (don't try multiple)
            query = f'site:linkedin.com/jobs/view "{job_title}" "{company_expanded}"'
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            try:
                # Quick search with short timeout
                response = self.session.get(search_url, timeout=3, verify=False)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for first LinkedIn job URL only
                    links = soup.find_all('a', href=True, limit=20)  # Limit to first 20 links
                    for link in links:
                        href = link.get('href', '')
                        
                        # Check if this is a LinkedIn job URL
                        if 'linkedin.com/jobs/view' in href:
                            # Extract the actual LinkedIn URL
                            if href.startswith('//duckduckgo.com'):
                                # DuckDuckGo redirect link - extract actual URL
                                import urllib.parse
                                try:
                                    parsed = urllib.parse.parse_qs(href)
                                    if 'uddg' in parsed:
                                        actual_url = urllib.parse.unquote(parsed['uddg'][0])
                                        if 'linkedin.com/jobs/view' in actual_url:
                                            logger.info(f"✅ Found LinkedIn URL via AI search")
                                            return actual_url
                                except:
                                    continue
                            elif 'linkedin.com/jobs/view' in href:
                                # Direct LinkedIn URL
                                if not href.startswith('http'):
                                    href = 'https://www.linkedin.com' + href
                                logger.info(f"✅ Found LinkedIn URL via AI search")
                                return href
                
            except Exception as e:
                logger.debug(f"Quick search timed out: {e}")
            
            logger.info("AI search completed (no specific job found)")
            return None
            
        except Exception as e:
            logger.debug(f"AI search error: {e}")
            return None
    
    def _ai_select_best_job_match(self, jobs: List[Dict], target_company: str, company_expanded: str, job_title: str, api_key: str) -> Optional[Dict]:
        """
        Use AI to intelligently select the best matching job from search results.
        
        Args:
            jobs: List of scraped job dictionaries
            target_company: Original company name from user (e.g., "Mindef")
            company_expanded: Expanded company name (e.g., "Ministry of Defence Singapore")
            job_title: Job title being searched for
            api_key: OpenAI API key
            
        Returns:
            Best matching job dictionary or None
        """
        try:
            if not api_key:
                logger.warning("No API key provided for AI filtering")
                return jobs[0] if jobs else None
            
            # Prepare job summaries for AI analysis
            job_summaries = []
            for idx, job in enumerate(jobs):
                summary = f"Job {idx+1}:\n"
                summary += f"  Company: {job.get('company', 'Unknown')}\n"
                summary += f"  Title: {job.get('title', 'Unknown')}\n"
                summary += f"  Description: {job.get('description', 'No description')[:200]}...\n"
                job_summaries.append(summary)
            
            # AI prompt for intelligent matching
            prompt = f"""You are an expert job search assistant. Analyze these LinkedIn job search results and select the one that BEST matches the target company.

TARGET SEARCH:
- Company: {target_company}
- Full Company Name: {company_expanded}
- Job Title: {job_title}

SEARCH RESULTS:
{chr(10).join(job_summaries)}

INSTRUCTIONS:
1. Identify which job listing is from the target company ({target_company} / {company_expanded})
2. If no exact match, identify jobs from RELATED organizations (subsidiaries, departments, government agencies)
3. IMPORTANT: Reject jobs from completely unrelated companies (e.g., LEGO, Netflix when searching for Ministry of Defence)
4. Consider name variations (Mindef = Ministry of Defence = Singapore Armed Forces)

Respond with ONLY the job number (1, 2, 3, etc.) of the best match.
If NO jobs match the target company at all, respond with "NONE".

Your response (just the number or NONE):"""

            # Call OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise job matching assistant. Return only job numbers or 'NONE'."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=10,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip().upper()
            logger.info(f"AI job selection result: {result}")
            
            # Parse AI response
            if result == "NONE":
                logger.warning(f"AI determined none of the jobs match {target_company}")
                return None
            
            # Extract job number
            import re
            match = re.search(r'\d+', result)
            if match:
                job_num = int(match.group()) - 1  # Convert to 0-indexed
                if 0 <= job_num < len(jobs):
                    logger.info(f"✅ AI selected job {job_num+1} as best match for {target_company}")
                    return jobs[job_num]
            
            # Fallback: return first job if AI response unclear
            logger.warning("Could not parse AI response, using first job")
            return jobs[0]
            
        except Exception as e:
            logger.error(f"AI job filtering error: {e}")
            return jobs[0] if jobs else None
    
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
            
            # Use centralized company name expansion
            company_expanded = self._expand_company_name(company)
            
            # Build search query with expanded company name
            search_query = f"{job_title} {company_expanded}".strip().replace(' ', '%20')
            
            # Use single best search URL (don't try multiple to save time)
            search_url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Singapore"
            
            logger.info(f"Quick LinkedIn HTML search...")
            
            # Add headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Try once with shorter timeout (fast!)
            try:
                response = requests.get(search_url, headers=headers, timeout=5, verify=False, allow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for LinkedIn job links quickly - get up to 5 to check
                    job_links = soup.find_all('a', href=lambda x: x and '/jobs/view/' in x, limit=5)
                    
                    if job_links and api_key:
                        logger.info(f"Found {len(job_links)} potential job links - using AI to filter by company")
                        
                        # Scrape all found jobs
                        potential_jobs = []
                        for link in job_links:
                            job_url = link['href']
                            if not job_url.startswith('http'):
                                job_url = 'https://www.linkedin.com' + job_url
                            
                            scraped_job = self.scrape_linkedin_job_url(job_url)
                            if scraped_job:
                                potential_jobs.append(scraped_job)
                        
                        if potential_jobs:
                            # Use AI to select the best matching job
                            logger.info(f"🤖 Using AI to select best match for {company}...")
                            best_job = self._ai_select_best_job_match(potential_jobs, company, company_expanded, job_title, api_key)
                            if best_job:
                                jobs.append(best_job)
                                return jobs
                    
                    elif job_links:
                        logger.info(f"Found {len(job_links)} potential job links")
                        # Fallback: just take first one if no API key
                        for link in job_links[:1]:
                            job_url = link['href']
                            if not job_url.startswith('http'):
                                job_url = 'https://www.linkedin.com' + job_url
                            
                            logger.info(f"Scraping first LinkedIn result...")
                            scraped_job = self.scrape_linkedin_job_url(job_url)
                            if scraped_job:
                                jobs.append(scraped_job)
                                return jobs
                    else:
                        logger.info("No job links found in HTML")
                else:
                    logger.warning(f"LinkedIn returned status: {response.status_code}")
                
            except Exception as e:
                logger.debug(f"LinkedIn HTML search failed: {e}")
        
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
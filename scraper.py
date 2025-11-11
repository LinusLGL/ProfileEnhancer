"""
Job Portal Scraper Module
Searches multiple job portals for job descriptions based on company and job title.
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobPortalScraper:
    """Scrapes job descriptions from various job portals."""
    
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def _setup_selenium(self) -> webdriver.Chrome:
        """Setup Selenium WebDriver with Chrome."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={self.ua.random}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def search_indeed(self, job_title: str, company: str = "") -> List[Dict[str, str]]:
        """Search Indeed for job descriptions."""
        results = []
        try:
            query = f"{job_title} {company}".strip()
            url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards[:5]:  # Limit to 5 results
                    title_elem = card.find('h2', class_='jobTitle')
                    company_elem = card.find('span', class_='companyName')
                    description_elem = card.find('div', class_='job-snippet')
                    
                    if title_elem and description_elem:
                        results.append({
                            'source': 'Indeed',
                            'title': title_elem.get_text(strip=True),
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'description': description_elem.get_text(strip=True)
                        })
            
            logger.info(f"Indeed: Found {len(results)} results")
        except Exception as e:
            logger.error(f"Error scraping Indeed: {str(e)}")
        
        return results
    
    def search_linkedin(self, job_title: str, company: str = "") -> List[Dict[str, str]]:
        """Search LinkedIn for job descriptions (requires authentication in real scenario)."""
        results = []
        try:
            # Note: LinkedIn heavily restricts scraping and requires authentication
            # This is a simplified version - in production, you'd need LinkedIn API access
            query = f"{job_title} {company}".strip()
            url = f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}"
            
            driver = self._setup_selenium()
            driver.get(url)
            time.sleep(3)
            
            # LinkedIn shows limited content without login
            job_cards = driver.find_elements(By.CLASS_NAME, 'base-card')
            
            for card in job_cards[:3]:  # Limit results
                try:
                    title = card.find_element(By.CLASS_NAME, 'base-search-card__title').text
                    company_name = card.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text
                    
                    results.append({
                        'source': 'LinkedIn',
                        'title': title,
                        'company': company_name,
                        'description': 'Limited access without authentication'
                    })
                except Exception as e:
                    continue
            
            driver.quit()
            logger.info(f"LinkedIn: Found {len(results)} results")
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {str(e)}")
        
        return results
    
    def search_jobstreet(self, job_title: str, company: str = "") -> List[Dict[str, str]]:
        """Search JobStreet for job descriptions."""
        results = []
        try:
            query = f"{job_title} {company}".strip()
            # JobStreet Singapore
            url = f"https://www.jobstreet.com.sg/jobs?keywords={query.replace(' ', '-')}"
            
            driver = self._setup_selenium()
            driver.get(url)
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_cards = soup.find_all('article', {'data-testid': 'job-card'})
            
            for card in job_cards[:5]:
                try:
                    title_elem = card.find('a', {'data-automation': 'jobTitle'})
                    company_elem = card.find('a', {'data-automation': 'jobCompany'})
                    desc_elem = card.find('span', {'data-automation': 'jobShortDescription'})
                    
                    if title_elem:
                        results.append({
                            'source': 'JobStreet',
                            'title': title_elem.get_text(strip=True),
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'description': desc_elem.get_text(strip=True) if desc_elem else 'No description'
                        })
                except Exception as e:
                    continue
            
            driver.quit()
            logger.info(f"JobStreet: Found {len(results)} results")
        except Exception as e:
            logger.error(f"Error scraping JobStreet: {str(e)}")
        
        return results
    
    def search_mycareersfuture(self, job_title: str, company: str = "") -> List[Dict[str, str]]:
        """Search MyCareersFuture (Singapore) for job descriptions."""
        results = []
        try:
            query = f"{job_title} {company}".strip()
            url = f"https://www.mycareersfuture.gov.sg/search?search={query.replace(' ', '%20')}"
            
            driver = self._setup_selenium()
            driver.get(url)
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # MyCareersFuture uses dynamic loading
            job_cards = soup.find_all('div', {'data-testid': 'job-card'})
            
            for card in job_cards[:5]:
                try:
                    title_elem = card.find('h3')
                    company_elem = card.find('p')
                    
                    if title_elem:
                        results.append({
                            'source': 'MyCareersFuture',
                            'title': title_elem.get_text(strip=True),
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'description': 'Available on detail page'
                        })
                except Exception as e:
                    continue
            
            driver.quit()
            logger.info(f"MyCareersFuture: Found {len(results)} results")
        except Exception as e:
            logger.error(f"Error scraping MyCareersFuture: {str(e)}")
        
        return results
    
    def search_all_portals(self, job_title: str, company: str = "") -> List[Dict[str, str]]:
        """Search all supported job portals and aggregate results."""
        all_results = []
        
        logger.info(f"Searching for: {job_title} at {company if company else 'any company'}")
        
        # Search each portal
        portals = [
            ('Indeed', self.search_indeed),
            ('JobStreet', self.search_jobstreet),
            ('MyCareersFuture', self.search_mycareersfuture),
            # LinkedIn requires authentication, can be enabled if credentials are provided
            # ('LinkedIn', self.search_linkedin),
        ]
        
        for portal_name, search_func in portals:
            try:
                logger.info(f"Searching {portal_name}...")
                results = search_func(job_title, company)
                all_results.extend(results)
                time.sleep(2)  # Be respectful with rate limiting
            except Exception as e:
                logger.error(f"Failed to search {portal_name}: {str(e)}")
        
        logger.info(f"Total results found: {len(all_results)}")
        return all_results
    
    def extract_job_details(self, results: List[Dict[str, str]]) -> str:
        """Extract and format job details from search results."""
        if not results:
            return "No job descriptions found from web search."
        
        formatted_text = "=== Job Descriptions Found from Web Search ===\n\n"
        
        for idx, result in enumerate(results, 1):
            formatted_text += f"{idx}. {result['title']} at {result['company']} (Source: {result['source']})\n"
            formatted_text += f"   Description: {result['description']}\n\n"
        
        return formatted_text


if __name__ == "__main__":
    # Test the scraper
    scraper = JobPortalScraper()
    results = scraper.search_all_portals("Software Engineer", "Google")
    print(scraper.extract_job_details(results))

"""
Job Description Generator Module
Uses OpenAI to generate comprehensive job descriptions based on user input and web-scraped data.
"""

import os
from typing import Optional, Dict, List
import logging
from openai import OpenAI
from dotenv import load_dotenv
from classifier import SingaporeClassifier

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobDescriptionGenerator:
    """Generates detailed job descriptions using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the generator with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file or pass it directly.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize classifier
        try:
            self.classifier = SingaporeClassifier()
            logger.info("Singapore classifier initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize classifier: {str(e)}")
            self.classifier = None
        
    def generate_job_description(
        self,
        company: str,
        job_title: str,
        initial_description: str = "",
        web_search_results: str = "",
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Generate a comprehensive job description using AI.
        
        Args:
            company: Company name
            job_title: Job title/position
            initial_description: User-provided initial description (optional)
            web_search_results: Scraped job descriptions from web (optional)
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            
        Returns:
            Generated detailed job description
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(company, job_title, initial_description, web_search_results)
            
            logger.info(f"Generating job description for {job_title} at {company}")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert HR professional and job description writer. 
                        Your task is to create concise, professional job descriptions that focus 
                        only on the job overview and key responsibilities. Keep descriptions 
                        brief and focused, avoiding lengthy requirements or benefits sections."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            generated_description = response.choices[0].message.content.strip()
            logger.info("Job description generated successfully")
            
            # Add SSIC and SSO classification using the FULL generated description and AI company description
            classification_text = ""
            if self.classifier:
                try:
                    # Use the complete generated description for classification
                    full_description = f"{initial_description} {generated_description}".strip()
                    # Pass the API key to enable AI-generated company description
                    classification = self.classifier.classify_job(
                        company, job_title, full_description, api_key=self.api_key
                    )
                    classification_summary = self.classifier.get_classification_summary(classification)
                    classification_text = f"\n\n---\n\n{classification_summary}"
                    logger.info("Classification completed successfully with AI company analysis")
                except Exception as e:
                    logger.warning(f"Classification failed: {str(e)}")
            
            return generated_description + classification_text
            
        except Exception as e:
            logger.error(f"Error generating job description: {str(e)}")
            raise
    
    def _build_prompt(
        self,
        company: str,
        job_title: str,
        initial_description: str,
        web_search_results: str
    ) -> str:
        """Build the prompt for OpenAI based on available information."""
        
        prompt = f"""Create a comprehensive and professional job description for the following position:

**Company:** {company}
**Job Title:** {job_title}
"""
        
        if initial_description:
            prompt += f"""
**Initial Description Provided:**
{initial_description}
"""
        
        if web_search_results and web_search_results != "No job descriptions found from web search.":
            prompt += f"""
**Reference Job Descriptions from Similar Positions:**
{web_search_results}
"""
        
        prompt += """

Please create a concise job description that includes ONLY:

1. **Job Overview/Summary**: A brief, compelling summary of the role (2-3 sentences)
2. **Key Responsibilities**: List of 5-8 primary duties and responsibilities (bullet points)

Make the description:
- Concise and focused
- Professional but not overly detailed
- Clear and specific
- Between 150-300 words total

Do not include qualifications, requirements, benefits, or other sections - just the overview and responsibilities.
"""
        
        return prompt
    
    def generate_batch_descriptions(
        self,
        job_data: List[Dict[str, str]],
        include_web_search: bool = True,
        scraper = None
    ) -> List[Dict[str, str]]:
        """
        Generate job descriptions for multiple jobs (batch processing).
        
        Args:
            job_data: List of dicts with 'company', 'job_title', 'job_description' keys
            include_web_search: Whether to include web search results
            scraper: JobPortalScraper instance (required if include_web_search is True)
            
        Returns:
            List of dicts with original data plus 'generated_description' key
        """
        results = []
        
        for idx, job in enumerate(job_data, 1):
            logger.info(f"Processing job {idx}/{len(job_data)}: {job.get('job_title')} at {job.get('company')}")
            
            try:
                web_results = ""
                if include_web_search and scraper:
                    search_results = scraper.search_all_portals(
                        job.get('job_title', ''),
                        job.get('company', '')
                    )
                    web_results = scraper.extract_job_details(search_results)
                
                generated_desc = self.generate_job_description(
                    company=job.get('company', ''),
                    job_title=job.get('job_title', ''),
                    initial_description=job.get('job_description', ''),
                    web_search_results=web_results
                )
                
                result = job.copy()
                result['generated_description'] = generated_desc
                result['status'] = 'Success'
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing job {idx}: {str(e)}")
                result = job.copy()
                result['generated_description'] = f"Error: {str(e)}"
                result['status'] = 'Failed'
                results.append(result)
        
        return results
    
    def enhance_existing_description(
        self,
        company: str,
        job_title: str,
        existing_description: str,
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Enhance an existing job description to make it more comprehensive.
        
        Args:
            company: Company name
            job_title: Job title
            existing_description: Existing job description to enhance
            model: OpenAI model to use
            
        Returns:
            Enhanced job description
        """
        try:
            prompt = f"""Please enhance and expand the following job description to make it more 
comprehensive, professional, and appealing to candidates.

**Company:** {company}
**Job Title:** {job_title}

**Current Job Description:**
{existing_description}

Please improve it by:
1. Adding more detail where needed
2. Structuring it with clear sections (Overview, Responsibilities, Requirements, etc.)
3. Making it more engaging and professional
4. Ensuring it's comprehensive but concise
5. Adding any missing standard elements

Maintain the core information but enhance the presentation and completeness.
"""
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR professional specializing in job description optimization."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error enhancing job description: {str(e)}")
            raise


if __name__ == "__main__":
    # Test the generator
    try:
        generator = JobDescriptionGenerator()
        description = generator.generate_job_description(
            company="TechCorp",
            job_title="Senior Software Engineer",
            initial_description="Looking for an experienced developer to work on our cloud platform."
        )
        print(description)
    except Exception as e:
        print(f"Error: {e}")

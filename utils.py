"""
Utility functions for validation, error handling, and helper operations.
"""

import re
from typing import Tuple, Optional
import pandas as pd


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_company_name(company: str) -> Tuple[bool, Optional[str]]:
    """
    Validate company name input.
    
    Args:
        company: Company name string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not company or not company.strip():
        return False, "Company name cannot be empty"
    
    if len(company.strip()) < 2:
        return False, "Company name must be at least 2 characters"
    
    if len(company.strip()) > 100:
        return False, "Company name must be less than 100 characters"
    
    return True, None


def validate_job_title(job_title: str) -> Tuple[bool, Optional[str]]:
    """
    Validate job title input.
    
    Args:
        job_title: Job title string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not job_title or not job_title.strip():
        return False, "Job title cannot be empty"
    
    if len(job_title.strip()) < 2:
        return False, "Job title must be at least 2 characters"
    
    if len(job_title.strip()) > 150:
        return False, "Job title must be less than 150 characters"
    
    return True, None


def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate OpenAI API key format.
    
    Args:
        api_key: API key string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key or not api_key.strip():
        return False, "API key cannot be empty"
    
    if not api_key.startswith('sk-'):
        return False, "Invalid API key format. OpenAI keys start with 'sk-'"
    
    if len(api_key) < 20:
        return False, "API key appears to be too short"
    
    return True, None


def validate_excel_structure(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validate Excel file structure.
    
    Args:
        df: Pandas DataFrame from Excel file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "Excel file is empty"
    
    required_columns = ['Company', 'Job Title']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for empty required fields
    for col in required_columns:
        empty_count = df[col].isna().sum() + (df[col] == '').sum()
        if empty_count > 0:
            return False, f"Column '{col}' has {empty_count} empty rows. Please fill all required fields."
    
    if len(df) > 100:
        return False, "Excel file contains more than 100 rows. Please process in smaller batches."
    
    return True, None


def sanitize_text(text: str) -> str:
    """
    Sanitize text input by removing potentially harmful characters.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Trim excessive whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def format_error_message(error: Exception) -> str:
    """
    Format error message for user display.
    
    Args:
        error: Exception object
        
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Common error mappings
    error_mappings = {
        'AuthenticationError': 'Invalid API key. Please check your OpenAI API key.',
        'RateLimitError': 'API rate limit exceeded. Please wait a moment and try again.',
        'APIConnectionError': 'Cannot connect to OpenAI API. Please check your internet connection.',
        'Timeout': 'Request timed out. Please try again.',
        'InvalidRequestError': 'Invalid request to API. Please check your inputs.',
    }
    
    if error_type in error_mappings:
        return error_mappings[error_type]
    
    # Return generic message for unknown errors
    if error_msg:
        return f"{error_type}: {error_msg}"
    
    return "An unexpected error occurred. Please try again."


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def estimate_processing_time(num_jobs: int, use_web_search: bool = True) -> str:
    """
    Estimate processing time for batch jobs.
    
    Args:
        num_jobs: Number of jobs to process
        use_web_search: Whether web search is enabled
        
    Returns:
        Estimated time as string
    """
    # Rough estimates: 10 seconds per job with web search, 5 without
    time_per_job = 10 if use_web_search else 5
    total_seconds = num_jobs * time_per_job
    
    if total_seconds < 60:
        return f"~{total_seconds} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"~{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"~{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"


def create_sample_excel() -> pd.DataFrame:
    """
    Create a sample Excel DataFrame with example data.
    
    Returns:
        Sample DataFrame
    """
    data = {
        'Company': [
            'Google',
            'Microsoft',
            'Amazon',
            'Apple',
            'Meta'
        ],
        'Job Title': [
            'Senior Software Engineer',
            'Data Scientist',
            'Product Manager',
            'UX Designer',
            'Machine Learning Engineer'
        ],
        'Job Description': [
            'Develop scalable cloud applications',
            'Analyze data and build ML models',
            'Lead product strategy and development',
            'Design user-centered interfaces',
            'Build and deploy ML systems'
        ]
    }
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    # Test validation functions
    print("Testing validation functions...")
    
    # Test company name validation
    print("\nCompany name validation:")
    print(validate_company_name("Google"))  # Should be valid
    print(validate_company_name("A"))  # Should be invalid
    print(validate_company_name(""))  # Should be invalid
    
    # Test job title validation
    print("\nJob title validation:")
    print(validate_job_title("Software Engineer"))  # Should be valid
    print(validate_job_title(""))  # Should be invalid
    
    # Test API key validation
    print("\nAPI key validation:")
    print(validate_api_key("sk-1234567890abcdefghij"))  # Should be valid
    print(validate_api_key("invalid"))  # Should be invalid
    
    # Test text sanitization
    print("\nText sanitization:")
    print(sanitize_text("Hello   World  \n  Test"))
    
    # Test time estimation
    print("\nTime estimation:")
    print(f"5 jobs with web search: {estimate_processing_time(5, True)}")
    print(f"20 jobs without web search: {estimate_processing_time(20, False)}")

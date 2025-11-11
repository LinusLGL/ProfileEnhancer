# Configuration Template file for default settings
# Copy this file to config.py and add your actual API key

# Default OpenAI API Key (for backend use)
DEFAULT_OPENAI_API_KEY = "your_backend_api_key_here"

# Application settings
APP_TITLE = "SS-Finder: Singapore Job Description Generator"
MAX_BATCH_SIZE = 100
DEFAULT_WEB_SEARCH = True

# Instructions:
# 1. For local development: Copy this file to config.py and add your API key
# 2. For Streamlit Cloud: The app includes built-in fallback configuration
# 3. The config.py file will be ignored by git for security
# 4. Users can also provide their own API keys through the UI or Streamlit secrets

# Deployment Note: 
# The actual backend API key is configured in the deployment environment
# This template serves as a guide for the configuration structure
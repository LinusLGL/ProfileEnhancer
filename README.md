# Job Description Generator

A Streamlit application that generates detailed job descriptions based on user input by web scraping job portals and using AI to create comprehensive job descriptions.

## Features

- 🔍 **Web Scraping**: Searches multiple job portals (LinkedIn, Indeed, JobStreet, MyCareersFuture, foundit, JobsCentral)
- 🤖 **AI-Powered Generation**: Uses OpenAI to generate detailed job descriptions
- 📝 **Manual Input**: Enter company, job title, and initial job description
- 📊 **Excel Processing**: Batch process multiple job descriptions from Excel files
- 📥 **Export Results**: Download results as Excel files with generated descriptions

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_KEY=your_serpapi_key_here (optional, for enhanced search)
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Choose between:
   - **Manual Input**: Enter individual job details
   - **Excel Upload**: Process multiple jobs at once

3. The app will:
   - Search job portals for similar positions
   - Analyze existing job descriptions
   - Generate a comprehensive job description

## Excel Format

Your Excel file should have these columns:
- `Company`: Company name
- `Job Title`: Position title
- `Job Description`: Initial/brief description (optional)

The app will add a new column:
- `Generated Job Description`: Detailed, comprehensive job description

## Dependencies

- Streamlit: Web interface
- Selenium: Web scraping
- BeautifulSoup4: HTML parsing
- OpenAI: AI-powered text generation
- Pandas: Excel file processing

## Notes

- Web scraping may be limited by website rate limits and anti-bot measures
- Some job portals may require authentication or have restrictions
- Results depend on availability of similar job postings online

## License

MIT License

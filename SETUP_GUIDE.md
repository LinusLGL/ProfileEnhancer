# Job Description Generator - Setup Guide

## Quick Start Guide

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### 2. Installation Steps

#### Step 1: Open PowerShell/Command Prompt
Navigate to the project directory:
```powershell
cd C:\job-description-generator
```

#### Step 2: Create Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Or enter your API key directly in the Streamlit interface.

#### Step 5: Run the Application
```powershell
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### 3. Using the Application

#### Single Job Entry
1. Enter **Company Name** (required)
2. Enter **Job Title** (required)
3. Optionally provide an initial **Job Description**
4. Enable **Web Search** to search job portals (recommended)
5. Click **Generate Job Description**
6. View and download the generated description

#### Batch Processing (Excel)
1. Prepare an Excel file with these columns:
   - **Company** (required)
   - **Job Title** (required)
   - **Job Description** (optional)

2. Upload the Excel file
3. Review the preview
4. Click **Process All Jobs**
5. Wait for processing to complete
6. Download the results as Excel

### 4. Excel File Format Example

| Company | Job Title | Job Description |
|---------|-----------|----------------|
| Google | Senior Software Engineer | Develop scalable cloud applications |
| Microsoft | Data Scientist | Analyze data and build ML models |
| Amazon | Product Manager | Lead product strategy |

### 5. Create Sample Excel File

Run this command to generate a sample Excel file:
```powershell
python create_sample_excel.py
```

This will create `sample_input.xlsx` with example data.

### 6. Features

✅ **Single Job Description Generation**
- Input company and job title
- Optional initial description
- AI-powered comprehensive output

✅ **Web Search Integration**
- Searches Indeed, JobStreet, MyCareersFuture
- Analyzes similar job postings
- Enhances description quality

✅ **Batch Processing**
- Process multiple jobs from Excel
- Progress tracking
- Export results to Excel

✅ **Download Options**
- Single descriptions as text files
- Batch results as Excel files
- Preserves original data

### 7. API Costs

The application uses OpenAI's API. Estimated costs:
- Single job: ~$0.01 - $0.05 per generation
- Model used: GPT-5 mini (cost-efficient)
- Web search is free but may be rate-limited

### 8. Troubleshooting

#### Issue: "Cannot connect to OpenAI API"
- Check your internet connection
- Verify your API key is valid
- Check OpenAI service status

#### Issue: "Web scraping returns no results"
- Some job portals may block automated access
- Try without web search
- Results depend on availability of similar jobs

#### Issue: "Excel upload fails"
- Ensure file has required columns (Company, Job Title)
- Check for empty rows in required fields
- Limit file to 100 rows per batch

#### Issue: "Selenium/ChromeDriver error"
- ChromeDriver will be auto-downloaded on first run
- Ensure you have Chrome browser installed
- Check firewall/antivirus settings

### 9. Advanced Configuration

#### Change OpenAI Model
Edit `app.py` and modify the model parameter in the generator calls:
```python
generated_desc = generator.generate_job_description(
    ...,
    model="gpt-4o"  # or "gpt-4-turbo", "gpt-3.5-turbo"
)
```

#### Adjust Web Search Sources
Edit `scraper.py` and modify the `search_all_portals` method to enable/disable specific job portals.

#### Customize Generation Prompt
Edit `generator.py` and modify the `_build_prompt` method to change how job descriptions are generated.

### 10. Best Practices

1. **For Best Results:**
   - Provide initial job description with key details
   - Enable web search for similar positions
   - Be specific with company and job title

2. **For Batch Processing:**
   - Process in batches of 20-30 jobs
   - Monitor API usage and costs
   - Review generated descriptions before using

3. **Cost Management:**
   - Use GPT-5 mini for cost efficiency
   - Disable web search if not needed
   - Process during off-peak hours

### 11. File Structure

```
job-description-generator/
├── app.py                    # Main Streamlit application
├── scraper.py               # Web scraping module
├── generator.py             # AI generation module
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
├── SETUP_GUIDE.md          # This file
├── create_sample_excel.py  # Sample Excel generator
├── .gitignore              # Git ignore rules
└── .env                    # Environment variables (create this)
```

### 12. Support & Resources

- **OpenAI Documentation:** https://platform.openai.com/docs
- **Streamlit Documentation:** https://docs.streamlit.io
- **Report Issues:** Check error messages in the app

### 13. Updates & Maintenance

To update dependencies:
```powershell
pip install --upgrade -r requirements.txt
```

To update ChromeDriver:
```powershell
pip install --upgrade webdriver-manager
```

---

## Quick Command Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run application
streamlit run app.py

# Create sample Excel
python create_sample_excel.py

# Deactivate virtual environment
deactivate
```

## Need Help?

If you encounter any issues:
1. Check this guide's troubleshooting section
2. Review error messages in the application
3. Verify all dependencies are installed
4. Check your OpenAI API key is valid

Happy job description generating! 🚀

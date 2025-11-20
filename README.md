# ProfileEnhancer: AI-Powered Job Description Generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://profileenhancer.streamlit.app)

An AI-powered job description generator with Singapore Standard Industrial Classification (SSIC 2025) and Singapore Standard Occupational Classification (SSO 2024) codes.

## 🚀 Live Demo

**Try the app**: [https://profileenhancer.streamlit.app](https://profileenhancer.streamlit.app)

## ✨ Key Features

- **🤖 AI Company Analysis**: Automatically generates company description to determine accurate 5-digit SSIC codes
- **🎯 Industry-Based SSIC**: Classification based on company's business activities, not job titles
- **🔗 SSIC-SSO Compatibility**: Validates that industry and occupation codes match logically
- **📊 Excel Batch Processing**: Upload files and get enhanced output with 4 new columns
- **🌐 Web Scraping**: Integrates data from LinkedIn, Indeed, JobStreet, MyCareersFuture
- **🇸🇬 Singapore Standards**: SSIC 2025 (1,694 codes) + SSO 2024 (1,617 codes)
- **⚡ GPT-5 Mini**: Fast, accurate, and cost-effective (~$0.01-$0.02 per job)

## 📋 How It Works

### Single Job Processing
1. Enter company name and job title
2. Add job description (optional)
3. Paste LinkedIn job URL (optional) - automatically scrapes job details from LinkedIn
4. Get AI-generated job description with classification codes

### Batch Excel Processing
1. Upload Excel file with columns: `Company`, `Job Title`, `Job Description` (optional)
2. Get your original data back with 4 additional columns:
   - � **Generated Job Description**
   - **Company Analysis** 
   - **SSIC 5 digit**
   - **SSOC 5 digit**

## 🛠️ Classification Method

### SSIC (Industry Classification) - AI-Powered
1. **🤖 AI Company Analysis**: Automatically generates industry-focused company description
   - Identifies primary industry sector (Technology, Finance, Healthcare, etc.)
   - Analyzes core business activities and services
   - Focuses on WHAT the company does, not WHO they hire
2. **📊 5-Digit SSIC Determination**: AI uses company analysis to find matching SSIC code
   - Searches 1,694 SSIC codes for best match
   - Ensures maximum classification specificity
   - Typical confidence: 90%+
3. **🔗 SSO Compatibility**: Validates industry-occupation pairing
   - Technology company (62011) ↔ Software Developer (25121) ✅
   - Bank (64191) ↔ Financial Analyst (24131) ✅
   - Government (84220) ↔ Public Sector Manager (11201) ✅

**Example**: "DBS Bank" → AI analyzes → "Financial services institution providing banking services" → SSIC 64191 (Commercial banks)

### SSO (Occupation Classification) - AI-Enhanced
1. **Job Role Analysis**: Uses job title + job description
2. **AI Enhancement**: Contextual understanding of job functions
3. **5-Digit Precision**: Specific occupation codes from 1,617 SSO codes

📖 **Learn More**: See [SSIC_AI_CLASSIFICATION.md](SSIC_AI_CLASSIFICATION.md) for detailed documentation

## 🔧 Local Development

### Prerequisites
- Python 3.8+
- OpenAI API key

### Setup
```bash
git clone https://github.com/LinusLGL/ProfileEnhancer.git
cd ProfileEnhancer
pip install -r requirements.txt
```

### Configuration
1. Copy `.streamlit/secrets.template.toml` to `.streamlit/secrets.toml`
2. Add your OpenAI API key to the secrets file:
```toml
[openai]
api_key = "your_actual_api_key_here"
```

### Run Locally
```bash
streamlit run app.py
```

## 📦 Dependencies

```
streamlit>=1.28.0
openai>=1.0.0
pandas>=1.5.0
beautifulsoup4>=4.12.0
selenium>=4.0.0
webdriver-manager>=3.8.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

## 🌟 Advanced Features

### AI-Powered Company Analysis for SSIC
ProfileEnhancer uses **AI to analyze your company** and generate an industry-focused description that determines the most accurate 5-digit SSIC code:

**How it works**:
1. You provide: Company name + Job title + Job description
2. AI generates: "DBS Bank is a financial services institution providing banking services..."
3. System determines: SSIC 64191 (Commercial banks) - 5 digits, 90% confidence

**Benefits**:
- ✅ **Accurate**: Based on actual business activities
- ✅ **Consistent**: Same company → Same SSIC code regardless of job role
- ✅ **Specific**: Always 5-digit SSIC codes for maximum detail
- ✅ **Compatible**: Validates SSIC-SSO pairings automatically

See [SSIC_AI_CLASSIFICATION.md](SSIC_AI_CLASSIFICATION.md) for detailed documentation and examples.

### Web Scraping Integration  
- **Multiple Sources**: LinkedIn, Indeed, JobStreet, MyCareersFuture, Careers@Gov (Singapore government portal)
- **LinkedIn Integration**: Paste any LinkedIn job URL to extract job description automatically
- **Context Enhancement**: Real job market data improves descriptions
- **Source Attribution**: Each scraped result shows its source for transparency
- **Error Handling**: Robust fallback mechanisms with multiple retry attempts

### Excel Batch Processing
- **Original Data Preserved**: All input columns maintained
- **4 Enhanced Columns**: Job description, company analysis, SSIC, SSO
- **Progress Tracking**: Real-time processing updates
- **Error Reporting**: Clear success/failure indicators

## 📊 Classification Examples

| Company | Job Title | SSIC Code | Industry | SSO Code | Occupation |
|---------|-----------|-----------|-----------|----------|------------|
| Google | Software Engineer | 62011 | Software Development | 25121 | Software Developer |
| DBS Bank | Financial Analyst | 64191 | Banking Services | 24131 | Financial Analyst |
| Ministry of Health | Consultant | 84120 | Government Health | 24211 | Management Consultant |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Singapore Department of Statistics for SSIC 2025 and SSO 2024 standards
- OpenAI for GPT-5 mini API
- Streamlit for the amazing framework

## 📞 Support

For questions or support:
- Create an issue on GitHub
- Email: LGLLiang22.13@gmail.com

---

**Built with ❤️ using Streamlit | Powered by OpenAI**

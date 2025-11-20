# ProfileEnhancer: AI-Powered Job Description Generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://profileenhancer.streamlit.app)

An AI-powered job description generator with Singapore Standard Industrial Classification (SSIC 2025) and Singapore Standard Occupational Classification (SSO 2024) codes.

## 🚀 Live Demo

**Try the app**: [https://profileenhancer.streamlit.app](https://profileenhancer.streamlit.app)

## ✨ Key Features

- **🤖 AI-Enhanced Classification**: Uses OpenAI GPT-4o-mini for intelligent business analysis
- **🎯 5-Digit SSIC Codes**: Maximum specificity for industry classification  
- **🔗 SSIC-SSO Compatibility**: Prevents incompatible industry-occupation pairings
- **📊 Excel Batch Processing**: Upload files and get enhanced output with 4 new columns
- **🌐 Web Scraping**: Integrates data from Indeed, JobStreet, MyCareersFuture
- **🇸🇬 Singapore Standards**: SSIC 2025 (1,694 codes) + SSO 2024 (1,617 codes)

## 📋 How It Works

### Single Job Processing
1. Enter company name and job title
2. Add job description (optional)
3. Get AI-generated job description with classification codes

### Batch Excel Processing
1. Upload Excel file with columns: `Company`, `Job Title`, `Job Description` (optional)
2. Get your original data back with 4 additional columns:
   - � **Generated Job Description**
   - **Company Analysis** 
   - **SSIC 5 digit**
   - **SSOC 5 digit**

## 🛠️ Classification Method

### SSIC (Industry Classification)
1. **Company Analysis**: AI generates industry-focused company description
2. **5-Digit Specificity**: Ensures maximum classification detail
3. **SSO Compatibility**: Checks logical industry-occupation pairing

### SSO (Occupation Classification)  
1. **Job Role Analysis**: Uses job title + job description
2. **AI Enhancement**: Contextual understanding of job functions
3. **5-Digit Precision**: Specific occupation codes

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

### AI-Enhanced Classification
- **Company Analysis**: Understands business context for accurate SSIC
- **Compatibility Matrix**: Technology ↔ Tech roles, Finance ↔ Finance roles
- **Confidence Boosting**: Enhanced algorithms with 60-100% accuracy

### Web Scraping Integration  
- **Multiple Sources**: Indeed, JobStreet, MyCareersFuture
- **Context Enhancement**: Real job market data improves descriptions
- **Error Handling**: Robust fallback mechanisms

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
- OpenAI for GPT-4o-mini API
- Streamlit for the amazing framework

## 📞 Support

For questions or support:
- Create an issue on GitHub
- Email: LGLLiang22.13@gmail.com

---

**Built with ❤️ using Streamlit | Powered by OpenAI**

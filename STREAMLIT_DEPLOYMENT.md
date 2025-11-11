# Streamlit Community Cloud Deployment Guide

## 🚀 Quick Deploy to Streamlit Community Cloud

Your SS-Finder app is ready for deployment! Here's how to set it up:

### 1. Deploy the App
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select repository: `LinusLGL/SS-Finder`
5. Set main file: `app.py`
6. Set branch: `main`
7. Choose app name: `ss-finder` (or your preference)
8. Click "Deploy"

### 2. Configure API Key (IMPORTANT!)

#### Option A: Streamlit Secrets (Recommended)
1. After deployment, go to your app settings
2. Click "Secrets" in the left sidebar
3. Add the following configuration:
```toml
[openai]
api_key = "your_openai_api_key_here"
```
4. Replace with your actual OpenAI API key
5. Save the secrets configuration
6. Your app will restart automatically

#### Option B: Environment Variables
1. In app settings, go to "Advanced settings"
2. Add environment variable:
   - Name: `OPENAI_API_KEY`
   - Value: `your_openai_api_key_here`

### 3. Expected App URL
Once deployed, your app will be available at:
`https://ss-finder.streamlit.app` (or your chosen name)

### 4. Features Ready for Use
✅ Job description generation with AI
✅ 5-digit SSIC industry classification  
✅ 5-digit SSO occupation classification
✅ Company analysis for accurate SSIC codes
✅ Excel batch processing with 4 enhanced columns
✅ Web scraping integration (limited in cloud)
✅ Backend API key fallback system

### 5. User Experience
- Users can start using immediately (backend fallback available)
- Optional API key input for users with their own OpenAI accounts
- All core SSIC/SSO classification features work perfectly
- Excel upload/download functionality included

## 🔧 Troubleshooting

### If deployment fails:
1. Check the logs in Streamlit Cloud dashboard
2. Ensure all required files are in the repository
3. Verify requirements.txt compatibility

### If API key errors occur:
1. Double-check the API key format in secrets
2. Ensure the key starts with "sk-proj-" or "sk-"
3. Verify the key has sufficient credits/permissions

## 📞 Support
- Repository: https://github.com/LinusLGL/SS-Finder
- Issues: Create a GitHub issue for bugs or questions

Your SS-Finder app is ready to help users generate job descriptions with Singapore SSIC and SSO classifications! 🇸🇬

## 📧 Contact
For API key configuration assistance, contact: LGLLiang22.13@gmail.com
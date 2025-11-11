# -*- coding: utf-8 -*-
"""
Streamlit Application for Job Description Generation
Main application file that provides the UI for generating job descriptions.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
from dotenv import load_dotenv

from scraper import JobPortalScraper
from generator import JobDescriptionGenerator

# Load environment variables
load_dotenv()

# Cloud deployment compatibility check
try:
    test_scraper = JobPortalScraper()
    WEB_SCRAPING_AVAILABLE = True
except Exception as e:
    WEB_SCRAPING_AVAILABLE = False
    st.warning("⚠️ Web scraping features are limited in cloud deployment. AI generation will work without web data.")

# Page configuration
st.set_page_config(
    page_title="Job Description Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #0dcaf0;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'generated_description' not in st.session_state:
        st.session_state.generated_description = None
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'api_key_validated' not in st.session_state:
        st.session_state.api_key_validated = False


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key."""
    if not api_key or not api_key.startswith('sk-'):
        return False
    try:
        generator = JobDescriptionGenerator(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Invalid API key: {str(e)}")
        return False


def display_search_results(results):
    """Display web search results in an expandable section."""
    if results and len(results) > 0:
        with st.expander(f"📊 View Web Search Results ({len(results)} found)", expanded=False):
            for idx, result in enumerate(results, 1):
                st.markdown(f"**{idx}. {result['title']}** at *{result['company']}*")
                st.markdown(f"*Source: {result['source']}*")
                st.text(result['description'])
                st.divider()
    else:
        st.info("No web search results found. Generating description based on input only.")


def process_single_job(company: str, job_title: str, job_description: str, 
                       use_web_search: bool, api_key: str):
    """Process a single job description request."""
    
    with st.spinner("🔍 Searching job portals..." if use_web_search else "⏳ Generating job description..."):
        try:
            # Initialize components
            generator = JobDescriptionGenerator(api_key=api_key)
            
            web_results_text = ""
            search_results = []
            
            # Web search if enabled
            if use_web_search:
                scraper = JobPortalScraper()
                search_results = scraper.search_all_portals(job_title, company)
                web_results_text = scraper.extract_job_details(search_results)
                st.session_state.search_results = search_results
            
            # Generate description
            with st.spinner("🤖 Generating comprehensive job description..."):
                generated_desc = generator.generate_job_description(
                    company=company,
                    job_title=job_title,
                    initial_description=job_description,
                    web_search_results=web_results_text
                )
                
                st.session_state.generated_description = generated_desc
            
            return True
            
        except Exception as e:
            st.error(f"[ERROR] {str(e)}")
            return False


def process_excel_file(df: pd.DataFrame, use_web_search: bool, api_key: str) -> pd.DataFrame:
    """Process Excel file with multiple job entries."""
    
    # Validate required columns
    required_cols = ['Company', 'Job Title']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
        return None
    
    # Add Job Description column if not present
    if 'Job Description' not in df.columns:
        df['Job Description'] = ''
    
    # Initialize components
    generator = JobDescriptionGenerator(api_key=api_key)
    scraper = JobPortalScraper() if use_web_search else None
    
    # Create results DataFrame starting with original data
    results_df = df.copy()
    
    # Add new columns for outputs
    results_df['📄 Generated Job Description'] = ''
    results_df['Company Analysis'] = ''
    results_df['SSIC 5 digit'] = ''
    results_df['SSOC 5 digit'] = ''
    results_df['Status'] = ''
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in df.iterrows():
        status_text.text(f"Processing {idx + 1}/{len(df)}: {row['Job Title']} at {row['Company']}")
        progress_bar.progress((idx + 1) / len(df))
        
        try:
            company = str(row['Company'])
            job_title = str(row['Job Title'])
            job_description = str(row.get('Job Description', ''))
            
            # Web search if enabled
            web_results_text = ""
            if use_web_search and scraper:
                search_results = scraper.search_all_portals(job_title, company)
                web_results_text = scraper.extract_job_details(search_results)
            
            # Generate job description with classification
            generated_desc = generator.generate_job_description(
                company=company,
                job_title=job_title,
                initial_description=job_description,
                web_search_results=web_results_text
            )
            
            # Parse the generated description to extract components
            job_desc_part, company_analysis, ssic_code, ssoc_code = parse_generated_description(generated_desc)
            
            # Update the results DataFrame
            results_df.at[idx, '📄 Generated Job Description'] = job_desc_part
            results_df.at[idx, 'Company Analysis'] = company_analysis
            results_df.at[idx, 'SSIC 5 digit'] = ssic_code
            results_df.at[idx, 'SSOC 5 digit'] = ssoc_code
            results_df.at[idx, 'Status'] = '[SUCCESS]'
            
        except Exception as e:
            results_df.at[idx, '📄 Generated Job Description'] = f"Error: {str(e)}"
            results_df.at[idx, 'Company Analysis'] = 'Failed to generate'
            results_df.at[idx, 'SSIC 5 digit'] = 'N/A'
            results_df.at[idx, 'SSOC 5 digit'] = 'N/A'
            results_df.at[idx, 'Status'] = '[FAILED]'
    
    status_text.text("[SUCCESS] All jobs processed!")
    progress_bar.progress(1.0)
    
    return results_df


def parse_generated_description(generated_desc: str) -> tuple:
    """Parse the generated description to extract individual components."""
    try:
        # Split by the classification section
        parts = generated_desc.split('---')
        
        # Job description is the first part
        job_desc_part = parts[0].strip()
        
        # Initialize default values
        company_analysis = "No analysis available"
        ssic_code = "N/A"
        ssoc_code = "N/A"
        
        # Parse classification section if it exists
        if len(parts) > 1:
            classification_section = parts[1].strip()
            
            # Extract company analysis
            if "**Company Analysis:**" in classification_section:
                analysis_start = classification_section.find("**Company Analysis:**") + len("**Company Analysis:**")
                analysis_end = classification_section.find("**Industry Classification", analysis_start)
                if analysis_end == -1:
                    analysis_end = classification_section.find("**Occupation Classification", analysis_start)
                if analysis_end != -1:
                    company_analysis = classification_section[analysis_start:analysis_end].strip()
                    # Clean up formatting
                    company_analysis = company_analysis.replace('\n', ' ').strip()
            
            # Extract SSIC code
            if "Code: " in classification_section:
                lines = classification_section.split('\n')
                for line in lines:
                    if "Code: " in line and "Industry Classification" in classification_section[max(0, classification_section.find(line)-200):classification_section.find(line)]:
                        ssic_code = line.split("Code: ")[1].split()[0].strip()
                        break
            
            # Extract SSOC code  
            if "Code: " in classification_section:
                lines = classification_section.split('\n')
                for line in lines:
                    if "Code: " in line and "Occupation Classification" in classification_section[max(0, classification_section.find(line)-200):classification_section.find(line)]:
                        ssoc_code = line.split("Code: ")[1].split()[0].strip()
                        break
        
        return job_desc_part, company_analysis, ssic_code, ssoc_code
        
    except Exception as e:
        # Return safe defaults if parsing fails
        return generated_desc, "Parsing error", "N/A", "N/A"


def main():
    """Main application function."""
    
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">Job Description Generator</h1>', unsafe_allow_html=True)
    st.markdown("Generate concise job descriptions with SSIC & SSO classification codes using AI and web-scraped data")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input with multiple fallback options
        api_key = st.text_input(
            "OpenAI API Key (Optional)",
            type="password",
            value=st.secrets.get("openai", {}).get("api_key", os.getenv('OPENAI_API_KEY', '')),
            help="Enter your OpenAI API key or leave empty to use system default"
        )
        
        # Multiple fallback options for API key
        if not api_key:
            try:
                # Try config.py first
                from config import DEFAULT_OPENAI_API_KEY
                api_key = DEFAULT_OPENAI_API_KEY
                st.info("🔑 Using system default API key")
            except ImportError:
                try:
                    # Fallback to config template for Streamlit Cloud
                    from config import DEFAULT_OPENAI_API_KEY as template_key
                    api_key = template_key
                    st.info("🔑 Using system configuration")
                except ImportError:
                    try:
                        # Last resort: check if config.template exists and rename
                        import os
                        if os.path.exists('config.template.py'):
                            import importlib.util
                            spec = importlib.util.spec_from_file_location("config_template", "config.template.py")
                            config_template = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(config_template)
                            api_key = config_template.DEFAULT_OPENAI_API_KEY
                            st.info("🔑 Using template configuration")
                        else:
                            st.warning("⚠️ No API key configured. Please enter your OpenAI API key.")
                            st.stop()
                    except Exception:
                        st.warning("⚠️ No API key configured. Please enter your OpenAI API key.")
                        st.stop()
        
        # Options
        st.divider()
        use_web_search = st.checkbox(
            "🔍 Enable Web Search",
            value=True,
            help="Search job portals for similar positions to enhance the description"
        )
        
        if use_web_search:
            st.info("Will search: Indeed, JobStreet, MyCareersFuture")
        
        st.divider()
        
        # Information
        st.markdown("### About")
        st.markdown("""
        This tool generates concise job descriptions with:
        - Job Overview/Summary (2-3 sentences)  
        - Key Responsibilities (5-8 bullet points)
        - AI-Generated Company Analysis for accurate SSIC classification
        - SSIC 2025 & SSO 2024 Classification Codes
        - Web search for better context (optional)
        - Batch processing for multiple jobs
        """)
        
        st.markdown("### Tips")
        st.markdown("""
        - Provide as much detail as possible
        - AI analyzes company for precise industry classification
        - Web search improves results
        - Output includes Singapore classification codes
        - Excel file should have 'Company' and 'Job Title' columns
        """)
    
    # Main content - Tabs
    tab1, tab2 = st.tabs(["Single Entry", "Batch Processing (Excel)"])
    
    # Tab 1: Single Entry
    with tab1:
        st.header("Generate Single Job Description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company = st.text_input(
                "Company Name *",
                placeholder="e.g., Google, Microsoft, Startup Inc.",
                help="Enter the company name"
            )
        
        with col2:
            job_title = st.text_input(
                "Job Title *",
                placeholder="e.g., Senior Software Engineer, Data Analyst",
                help="Enter the job title/position"
            )
        
        job_description = st.text_area(
            "Initial Job Description (Optional)",
            placeholder="Enter any existing job description or key details you want to include...",
            height=150,
            help="Provide any existing description or key points. Leave empty to generate from scratch."
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            generate_button = st.button("🚀 Generate Job Description", type="primary", use_container_width=True)
        
        if generate_button:
            if not company or not job_title:
                st.error("[ERROR] Please provide both Company Name and Job Title")
            else:
                success = process_single_job(company, job_title, job_description, use_web_search, api_key)
                
                if success:
                    st.success("[SUCCESS] Job description generated successfully!")
        
        # Display results
        if st.session_state.generated_description:
            st.divider()
            st.subheader("📄 Generated Job Description")
            
            # Display search results if available
            if use_web_search and st.session_state.search_results:
                display_search_results(st.session_state.search_results)
            
            # Display generated description
            st.markdown(st.session_state.generated_description)
            
            # Download button
            st.download_button(
                label="📥 Download as Text File",
                data=st.session_state.generated_description,
                file_name=f"job_description_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Tab 2: Batch Processing
    with tab2:
        st.header("Batch Process Excel File")
        
        st.markdown("""
        <div class="info-box">
        📋 <strong>Excel Format Requirements:</strong><br>
        Your Excel file must contain these columns:
        <ul>
            <li><strong>Company</strong> - Company name (required)</li>
            <li><strong>Job Title</strong> - Position title (required)</li>
            <li><strong>Job Description</strong> - Initial description (optional)</li>
        </ul>
        <br>
        📤 <strong>Output Format:</strong><br>
        Your original file will be returned with 4 additional columns:
        <ul>
            <li><strong>📄 Generated Job Description</strong> - AI-generated job overview and responsibilities</li>
            <li><strong>Company Analysis</strong> - AI analysis of company for accurate industry classification</li>
            <li><strong>SSIC 5 digit</strong> - Singapore Standard Industrial Classification code</li>
            <li><strong>SSOC 5 digit</strong> - Singapore Standard Occupational Classification code</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with job information"
        )
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                
                st.subheader("📊 Preview of Uploaded Data")
                st.dataframe(df.head(10), use_container_width=True)
                st.info(f"Total rows: {len(df)}")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    process_button = st.button("🚀 Process All Jobs", type="primary", use_container_width=True)
                
                if process_button:
                    st.divider()
                    st.subheader("⏳ Processing...")
                    
                    result_df = process_excel_file(df, use_web_search, api_key)
                    
                    if result_df is not None:
                        st.success("[SUCCESS] Processing complete!")
                        
                        # Display results
                        st.subheader("📊 Results")
                        
                        # Show a preview with the new columns highlighted
                        st.markdown("**Preview of Enhanced Data (Original + Generated Content):**")
                        
                        # Display the key new columns for preview
                        preview_cols = ['Company', 'Job Title', '📄 Generated Job Description', 'SSIC 5 digit', 'SSOC 5 digit', 'Status']
                        available_cols = [col for col in preview_cols if col in result_df.columns]
                        st.dataframe(result_df[available_cols].head(5), use_container_width=True)
                        
                        # Summary
                        success_count = len(result_df[result_df['Status'] == '[SUCCESS]'])
                        failed_count = len(result_df[result_df['Status'] == '[FAILED]'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("✅ SUCCESS", success_count)
                        with col2:
                            st.metric("❌ FAILED", failed_count)
                        with col3:
                            st.metric("📊 TOTAL", len(result_df))
                        
                        # Show detailed breakdown
                        with st.expander("📋 View Full Results Table", expanded=False):
                            st.dataframe(result_df, use_container_width=True)
                        
                        # Information about new columns
                        st.markdown("""
                        <div class="info-box">
                        📄 <strong>Enhanced Excel Output Contains:</strong><br>
                        <ul>
                            <li><strong>Original Data:</strong> All your input columns preserved</li>
                            <li><strong>📄 Generated Job Description:</strong> AI-generated job overview and responsibilities</li>
                            <li><strong>Company Analysis:</strong> AI analysis of the company for accurate classification</li>
                            <li><strong>SSIC 5 digit:</strong> Singapore Standard Industrial Classification code</li>
                            <li><strong>SSOC 5 digit:</strong> Singapore Standard Occupational Classification code</li>
                        </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download button
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            result_df.to_excel(writer, index=False, sheet_name='Enhanced Job Descriptions')
                        output.seek(0)
                        
                        st.download_button(
                            label="📥 Download Enhanced Excel File",
                            data=output,
                            file_name=f"enhanced_job_descriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Download your original data plus the 4 new generated columns"
                        )
                
            except Exception as e:
                st.error(f"[ERROR] Error reading Excel file: {str(e)}")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Built with ❤️ using Streamlit | Powered by OpenAI</p>
        <p><small>Note: Web scraping results may vary based on website accessibility and rate limits</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

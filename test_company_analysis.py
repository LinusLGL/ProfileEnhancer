"""
Test script to verify AI-powered company analysis for SSIC classification
"""

from classifier import SingaporeClassifier
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize classifier
classifier = SingaporeClassifier()

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("❌ No API key found. Please set OPENAI_API_KEY environment variable.")
    exit(1)

print("=" * 80)
print("TESTING AI-POWERED COMPANY ANALYSIS FOR SSIC CLASSIFICATION")
print("=" * 80)

# Test Case 1: Technology Company
print("\n📝 TEST CASE 1: Technology Company")
print("-" * 80)
result1 = classifier.classify_job(
    company="Google Singapore",
    job_title="Software Engineer",
    job_description="Develop and maintain web applications using Python and React. Work with cloud infrastructure and APIs.",
    api_key=api_key
)

print(f"Company: Google Singapore")
print(f"Job Title: Software Engineer")
print("\n🏢 AI-Generated Company Analysis:")
print(result1.get('company_description', 'No company description generated'))
print(f"\n📊 SSIC Classification:")
print(f"   Code: {result1['ssic']['code']} (5-digit)")
print(f"   Title: {result1['ssic']['title']}")
print(f"   Confidence: {result1['ssic']['confidence']}%")

# Test Case 2: Financial Institution
print("\n" + "=" * 80)
print("📝 TEST CASE 2: Financial Institution")
print("-" * 80)
result2 = classifier.classify_job(
    company="DBS Bank",
    job_title="Financial Analyst",
    job_description="Analyze market trends, prepare financial reports, and provide investment recommendations.",
    api_key=api_key
)

print(f"Company: DBS Bank")
print(f"Job Title: Financial Analyst")
print("\n🏢 AI-Generated Company Analysis:")
print(result2.get('company_description', 'No company description generated'))
print(f"\n📊 SSIC Classification:")
print(f"   Code: {result2['ssic']['code']} (5-digit)")
print(f"   Title: {result2['ssic']['title']}")
print(f"   Confidence: {result2['ssic']['confidence']}%")

# Test Case 3: Government Agency
print("\n" + "=" * 80)
print("📝 TEST CASE 3: Government Agency")
print("-" * 80)
result3 = classifier.classify_job(
    company="Ministry of Defence of Singapore",
    job_title="Manager (Museum Development & Governance)",
    job_description="Oversee museum operations, curate exhibitions, manage heritage collections, and ensure compliance with governance standards.",
    api_key=api_key
)

print(f"Company: Ministry of Defence of Singapore")
print(f"Job Title: Manager (Museum Development & Governance)")
print("\n🏢 AI-Generated Company Analysis:")
print(result3.get('company_description', 'No company description generated'))
print(f"\n📊 SSIC Classification:")
print(f"   Code: {result3['ssic']['code']} (5-digit)")
print(f"   Title: {result3['ssic']['title']}")
print(f"   Confidence: {result3['ssic']['confidence']}%")

print("\n" + "=" * 80)
print("✅ VERIFICATION COMPLETE")
print("=" * 80)
print("\n🎯 KEY POINTS:")
print("1. AI generates company analysis based on company name and job info")
print("2. Company analysis focuses on INDUSTRY SECTOR and BUSINESS ACTIVITIES")
print("3. SSIC 5-digit code is determined FROM the company analysis")
print("4. This ensures accurate industry classification")
print("\n📋 FLOW: Company Name + Job Info → AI Company Analysis → SSIC 5-digit Code")

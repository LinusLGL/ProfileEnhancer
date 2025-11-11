"""
Create sample Excel file for batch processing demonstration
"""
import pandas as pd

# Sample data for testing batch processing
sample_data = [
    {
        'Company': 'Google',
        'Job Title': 'Senior Software Engineer',
        'Job Description': 'Develop and maintain scalable software solutions for cloud platforms.'
    },
    {
        'Company': 'DBS Bank',
        'Job Title': 'Financial Analyst',
        'Job Description': 'Analyze market trends and prepare investment reports.'
    },
    {
        'Company': 'Shopee',
        'Job Title': 'Product Manager',
        'Job Description': 'Lead product development and strategy for e-commerce platform.'
    },
    {
        'Company': 'McKinsey & Company',
        'Job Title': 'Management Consultant',
        'Job Description': 'Provide strategic consulting to Fortune 500 clients.'
    },
    {
        'Company': 'Grab',
        'Job Title': 'Data Scientist',
        'Job Description': 'Build machine learning models for ride-sharing optimization.'
    }
]

# Create DataFrame
df = pd.DataFrame(sample_data)

# Save to Excel
output_file = 'sample_batch_input.xlsx'
df.to_excel(output_file, index=False, sheet_name='Job Input Data')

print(f"✅ Sample Excel file created: {output_file}")
print(f"📊 Contains {len(df)} sample job entries")
print("\nColumns created:")
for col in df.columns:
    print(f"  - {col}")

print(f"\nPreview of data:")
print(df.to_string(index=False))
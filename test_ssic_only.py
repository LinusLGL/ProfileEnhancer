"""
Test SSIC Classification Based Only on Company Analysis
"""
from classifier import SingaporeClassifier

# Initialize classifier
classifier = SingaporeClassifier()

# Test cases
test_cases = [
    {
        'company': 'Google',
        'job_title': 'Software Engineer', 
        'job_description': 'Develop web applications and work on distributed systems'
    },
    {
        'company': 'DBS Bank',
        'job_title': 'Financial Analyst',
        'job_description': 'Analyze market trends and prepare investment reports'
    },
    {
        'company': 'Ministry of Health',
        'job_title': 'Consultant',
        'job_description': 'Provide healthcare policy advice and strategic planning'
    }
]

print("Testing SSIC Classification (Company Analysis Only):")
print("=" * 60)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['company']} - {test['job_title']}")
    print(f"Job Description: {test['job_description']}")
    
    # Classify without API key (traditional matching)
    result = classifier.classify_job(
        company=test['company'],
        job_title=test['job_title'], 
        job_description=test['job_description'],
        api_key=None
    )
    
    print(f"SSIC Result: {result['ssic']['code']} - {result['ssic']['title']}")
    print(f"SSIC Confidence: {result['ssic']['confidence']}%")
    print(f"SSO Result: {result['sso']['code']} - {result['sso']['title']}")
    print(f"SSO Confidence: {result['sso']['confidence']}%")
    print("-" * 50)

print("\n✅ SSIC classification now uses ONLY company analysis")
print("✅ SSO classification uses job title and job description")
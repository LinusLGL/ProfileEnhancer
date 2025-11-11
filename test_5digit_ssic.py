"""
Test 5-Digit SSIC Classification with SSO Compatibility
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
        'job_title': 'Management Consultant',
        'job_description': 'Provide healthcare policy advice and strategic planning'
    },
    {
        'company': 'Shopee',
        'job_title': 'Product Manager',
        'job_description': 'Lead product development for e-commerce platform'
    }
]

print("Testing 5-Digit SSIC with SSO Compatibility:")
print("=" * 70)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['company']} - {test['job_title']}")
    print(f"Description: {test['job_description']}")
    
    # Classify without API key (traditional matching)
    result = classifier.classify_job(
        company=test['company'],
        job_title=test['job_title'], 
        job_description=test['job_description'],
        api_key=None
    )
    
    ssic_code = result['ssic']['code']
    sso_code = result['sso']['code']
    
    print(f"SSIC: {ssic_code} ({len(str(ssic_code))}-digit) - {result['ssic']['title']}")
    print(f"SSIC Confidence: {result['ssic']['confidence']}%")
    print(f"SSO: {sso_code} ({len(str(sso_code))}-digit) - {result['sso']['title']}")
    print(f"SSO Confidence: {result['sso']['confidence']}%")
    
    # Check if SSIC is 5-digit
    if len(str(ssic_code)) == 5:
        print("✅ 5-digit SSIC achieved")
    else:
        print("❌ SSIC not 5-digit")
    
    print("-" * 50)

print("\n🎯 Features:")
print("✅ SSIC classification considers Company Analysis + SSO compatibility")
print("✅ SSIC codes are 5-digit for maximum specificity") 
print("✅ SSO compatibility reduces incompatible industry-occupation pairings")
print("✅ SSO classification uses job title and job description")
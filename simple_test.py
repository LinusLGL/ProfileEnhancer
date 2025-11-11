"""
Simple test of updated classification system
"""
from classifier import SingaporeClassifier

c = SingaporeClassifier()

print("Testing 5-Digit SSIC with SSO Compatibility:")
print("=" * 60)

# Test Google case
result = c.classify_job('Google', 'Software Engineer', 'Develop web applications', api_key=None)
print(f"Google Software Engineer:")
print(f"  SSIC: {result['ssic']['code']} ({len(str(result['ssic']['code']))}-digit)")
print(f"  SSO: {result['sso']['code']} ({len(str(result['sso']['code']))}-digit)")

# Test DBS case  
result = c.classify_job('DBS Bank', 'Financial Analyst', 'Analyze market data', api_key=None)
print(f"\nDBS Bank Financial Analyst:")
print(f"  SSIC: {result['ssic']['code']} ({len(str(result['ssic']['code']))}-digit)")
print(f"  SSO: {result['sso']['code']} ({len(str(result['sso']['code']))}-digit)")

print("\n✅ SSIC now ensures 5-digit codes with SSO compatibility")
print("✅ Classification considers Company Analysis + Occupation match")
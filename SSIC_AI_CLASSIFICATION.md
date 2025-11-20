# AI-Powered SSIC Classification with Company Analysis

## Overview

The ProfileEnhancer application uses **AI to generate company analysis** which is then used to determine the most accurate **5-digit SSIC code** for industry classification. This ensures that the SSIC classification is based on the company's actual business activities, not just the job title.

## How It Works

### Step-by-Step Process

```
1. User Input
   ↓
2. AI Generates Company Analysis
   ↓
3. AI Determines 5-Digit SSIC Code
   ↓
4. Result: Accurate Industry Classification
```

### Detailed Flow

#### Step 1: User Provides Information
- **Company Name**: e.g., "Ministry of Defence of Singapore"
- **Job Title**: e.g., "Manager (Museum Development & Governance)"
- **Job Description**: e.g., "Oversee museum operations..."

#### Step 2: AI Generates Company Analysis
The system calls `generate_company_description()` which:

1. **Analyzes** the company name and job context
2. **Identifies** the primary industry sector
3. **Describes** core business activities
4. **Focuses** on classification keywords

**Example Output:**
```
"Ministry of Defence of Singapore is a government agency responsible 
for national defense and security operations. The ministry provides 
defense services, military operations, and public administration 
activities related to national security and defense matters."
```

**Key Focus Areas:**
- ✅ Industry sector (Government, Defense)
- ✅ Business activities (Defense services, Public administration)
- ✅ Business model (Government agency, B2G)
- ❌ NOT job-specific details

#### Step 3: SSIC Classification from Company Analysis
The system uses the company analysis to determine the **5-digit SSIC code**:

1. **Searches** SSIC database for matching industries
2. **Uses AI reasoning** to find best match
3. **Validates** compatibility with occupation (SSO)
4. **Returns** 5-digit SSIC code with high confidence

**Example Result:**
```
SSIC Code: 84220 (5-digit)
Title: Defence
Confidence: 90.0%
```

## Code Implementation

### Where It Happens

**File**: `classifier.py`

**Method**: `classify_job()`

```python
def classify_job(self, company: str, job_title: str, job_description: str, 
                api_key: Optional[str] = None) -> Dict[str, any]:
    """
    Classify a job with both SSIC and SSO codes.
    SSIC is 5-digit and considers Company Analysis + SSO compatibility.
    """
    # Step 1: Generate company description using AI for SSIC classification
    company_description = ""
    if api_key:
        company_description = self.generate_company_description(
            company, job_title, job_description, api_key
        )
    
    # Step 2: Determine SSO classification (job role)
    if api_key:
        sso_code, sso_title, sso_score = self._ai_enhanced_sso_classification(
            company, job_title, job_description, api_key
        )
    
    # Step 3: SSIC classification based on company analysis + SSO compatibility
    if api_key and company_description:
        ssic_code, ssic_title, ssic_score = self._ai_enhanced_ssic_classification(
            company, company_description, sso_code, sso_title, api_key
        )
    
    # Return results with company description
    return {
        'ssic': {'code': ssic_code, 'title': ssic_title, 'confidence': ssic_score},
        'sso': {'code': sso_code, 'title': sso_title, 'confidence': sso_score},
        'company_description': company_description  # <-- AI-generated analysis
    }
```

### Key Methods

#### 1. `generate_company_description()`
**Purpose**: Generate AI-powered company analysis for SSIC classification

**Input**:
- Company name
- Job title (for context)
- Job description (for context)
- OpenAI API key

**Output**: 
- 2-3 sentence company description focusing on:
  - Primary industry sector
  - Core business activities
  - Primary business model

**AI Prompt Strategy**:
```
"Generate a brief company description that focuses EXCLUSIVELY on the 
company's industry sector and primary business activities. This will be 
used specifically for Singapore Standard Industrial Classification (SSIC) 
purposes.

Focus on WHAT the company does (industry) not WHO they hire (jobs)."
```

#### 2. `_ai_enhanced_ssic_classification()`
**Purpose**: Use AI to determine 5-digit SSIC code from company analysis

**Input**:
- Company name
- **Company description** (AI-generated)
- SSO code (for compatibility)
- SSO title
- OpenAI API key

**Output**:
- 5-digit SSIC code
- SSIC title
- Confidence score (typically 90%+)

**AI Reasoning**:
```
"You are an expert in Singapore Standard Industrial Classification (SSIC 2025). 
Determine the most appropriate 5-DIGIT SSIC code based on the company analysis.

IMPORTANT:
1. Must be 5-DIGIT for maximum specificity
2. Based primarily on Company Analysis (business activities)
3. Must be logically compatible with the SSO occupation code"
```

## Examples

### Example 1: Technology Company

**Input**:
- Company: "Google Singapore"
- Job Title: "Software Engineer"
- Description: "Develop web applications..."

**AI Company Analysis**:
```
"Google Singapore is a technology company specializing in software 
development, cloud computing services, and digital advertising platforms. 
The company provides internet-related services including search engines, 
online advertising technologies, and cloud computing solutions."
```

**SSIC Result**:
- Code: `62011` (5-digit)
- Title: Software development
- Confidence: 90%

### Example 2: Financial Institution

**Input**:
- Company: "DBS Bank"
- Job Title: "Financial Analyst"
- Description: "Analyze market trends..."

**AI Company Analysis**:
```
"DBS Bank is a financial services institution providing comprehensive 
banking and financial services. The company offers retail banking, 
corporate banking, investment banking, and wealth management services 
to individuals, businesses, and institutional clients."
```

**SSIC Result**:
- Code: `64191` (5-digit)
- Title: Commercial banks
- Confidence: 90%

### Example 3: Government Agency

**Input**:
- Company: "Ministry of Defence"
- Job Title: "Manager (Museum Development)"
- Description: "Oversee museum operations..."

**AI Company Analysis**:
```
"Ministry of Defence of Singapore is a government agency responsible 
for national defense and security operations. The ministry provides 
defense services, military operations, and public administration 
activities related to national security."
```

**SSIC Result**:
- Code: `84220` (5-digit)
- Title: Defence
- Confidence: 90%

## Benefits

### 1. **Accuracy**
- AI understands company's actual business activities
- Not confused by job titles that could apply to multiple industries
- Example: "Data Analyst" at a bank → Financial Services (not Technology)

### 2. **Consistency**
- Same company always gets same industry classification
- Regardless of different job titles posted
- Example: DBS Bank → Always classified as Financial Services

### 3. **Specificity**
- Always returns **5-digit SSIC codes**
- Maximum level of detail in classification
- Follows Singapore SSIC 2025 standards

### 4. **Compatibility**
- Validates SSIC-SSO pairings
- Ensures industry and occupation codes match logically
- Example: Software Developer (SSO 25121) at Tech Company (SSIC 62011) ✅

## Testing

Run the test script to verify AI-powered company analysis:

```bash
python test_company_analysis.py
```

This will test 3 different scenarios:
1. Technology company (Google)
2. Financial institution (DBS Bank)
3. Government agency (Ministry of Defence)

## Configuration

The AI-powered company analysis requires an **OpenAI API key** to work.

**Without API Key**:
- Falls back to basic text matching
- Lower accuracy
- No company analysis generated

**With API Key**:
- AI generates company analysis
- High accuracy (90%+ confidence)
- 5-digit SSIC codes guaranteed

**To Enable**:
1. Set `OPENAI_API_KEY` environment variable
2. Or configure in Streamlit secrets
3. Or add to `config.py`

## API Calls

Each classification makes **3 AI calls**:

1. **Company Analysis** (~250 tokens)
2. **SSO Classification** (~50 tokens)
3. **SSIC Classification** (~50 tokens)

**Total Cost**: ~$0.01-$0.02 per job using GPT-5 mini

## Summary

✅ **AI generates company analysis** from company name and job info  
✅ **Company analysis focuses** on industry sector and business activities  
✅ **SSIC code is determined** from the company analysis  
✅ **Always returns 5-digit** SSIC codes for maximum specificity  
✅ **Validates compatibility** between SSIC industry and SSO occupation  

**Result**: Accurate, consistent, and reliable SSIC classification based on actual business activities, not job titles.

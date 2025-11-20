# Source URL Display - Visual Examples

## What Users Will See

### Example 1: Ministry of Defence Manager Position

#### Input Screen
```
Company Name: Mindef
Job Title: Manager (Museum Development & Governance)
LinkedIn URL: https://www.linkedin.com/jobs/view/4341315847/
☑ Enable Web Search
```

#### Output Display

**📊 View Web Search Results (5 found)** _(Click to expand)_

---

**1. Manager (Museum Development & Governance)** at *Ministry of Defence of Singapore*  
*Source: [LinkedIn](https://www.linkedin.com/jobs/view/4341315847/)*

```
About the Role
The Ministry of Defence is seeking a Manager for Museum Development & Governance 
to oversee the strategic planning and operational management of defence heritage 
museums...

Key Responsibilities:
- Develop and implement museum governance frameworks
- Lead strategic planning for museum development
- Manage stakeholder relationships and partnerships
...
```

---

**2. Museum Manager** at *Mindef*  
*Source: [Indeed](https://sg.indeed.com/jobs?q=Manager+Museum+Mindef&l=Singapore)*

```
Indeed search results limited in cloud deployment
```

---

**3. Manager positions** at *Government Agency*  
*Source: [Careers@Gov](https://jobs.careers.gov.sg/jobs?keywords=Manager+Museum+Mindef)*

```
Singapore government sector opportunities for Manager (Museum Development & Governance)
```

---

### Example 2: Software Engineer at Tech Company

#### Input Screen
```
Company Name: Google
Job Title: Software Engineer
☑ Enable Web Search
```

#### Output Display

**📊 View Web Search Results (5 found)** _(Click to expand)_

---

**1. Software Engineer** at *Google Singapore*  
*Source: [LinkedIn](https://www.linkedin.com/jobs/view/xyz789/)*

```
Google is looking for a Software Engineer to join our Singapore engineering team.
You'll work on cutting-edge projects that impact billions of users worldwide...

Qualifications:
- Bachelor's degree in Computer Science or equivalent
- 3+ years of software development experience
- Strong coding skills in C++, Java, or Python
...
```

---

**2. Software Engineer - Backend** at *Google*  
*Source: [Indeed](https://sg.indeed.com/viewjob?jk=abc123)*

```
Job posting from Indeed for Software Engineer
```

---

**3. Software Engineer** at *Google*  
*Source: [JobStreet](https://www.jobstreet.com.sg/jobs?keywords=Software+Engineer+Google)*

```
JobStreet posting for Software Engineer - web scraping limited in cloud
```

---

## UI Comparison

### Before This Feature
```
Source: LinkedIn
```
❌ No way to verify or access the original posting

### After This Feature
```
Source: LinkedIn (https://www.linkedin.com/jobs/view/4341315847/)
```
✅ Clickable link to original job posting

**In Markdown Rendering (Streamlit):**
```
Source: LinkedIn
```
→ Becomes clickable hyperlink: **[LinkedIn](https://www.linkedin.com/jobs/view/4341315847/)**

## Browser Display

When rendered in the Streamlit app, it looks like:

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 View Web Search Results (5 found)                  ▼     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ 1. Manager (Museum Development & Governance) at Ministry     │
│    of Defence of Singapore                                   │
│                                                               │
│ Source: LinkedIn  ← Clickable blue hyperlink                │
│         ^^^^^^^^                                              │
│                                                               │
│ About the Role                                               │
│ The Ministry of Defence is seeking a Manager for Museum      │
│ Development & Governance...                                  │
│                                                               │
│ ───────────────────────────────────────────────────────────  │
│                                                               │
│ 2. Museum Manager at Mindef                                  │
│                                                               │
│ Source: Indeed  ← Clickable blue hyperlink                   │
│         ^^^^^^                                                │
│                                                               │
│ Indeed search results limited in cloud deployment            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Mobile View

On mobile devices, the links remain clickable:

```
╔═══════════════════════════════════╗
║ 📊 Web Search Results        ▼   ║
╠═══════════════════════════════════╣
║                                   ║
║ 1. Manager (Museum Development)   ║
║    at Ministry of Defence          ║
║                                   ║
║ Source: LinkedIn                  ║
║         ^^^^^^^^ (tap to open)    ║
║                                   ║
║ About the Role                    ║
║ The Ministry of Defence is        ║
║ seeking a Manager...              ║
║                                   ║
║ ─────────────────────────────     ║
║                                   ║
║ 2. Museum Manager at Mindef       ║
║                                   ║
║ Source: Indeed                    ║
║         ^^^^^^ (tap to open)      ║
║                                   ║
╚═══════════════════════════════════╝
```

## Interaction Flow

### User Journey

1. **User enters job details**
   ```
   Company: Mindef
   Job Title: Manager (Museum Development & Governance)
   ```

2. **System searches multiple portals**
   ```
   🔍 Searching job portals...
   ✓ LinkedIn
   ✓ Indeed
   ✓ JobStreet
   ✓ MyCareersFuture
   ✓ Careers@Gov
   ```

3. **Results displayed with clickable sources**
   ```
   📊 View Web Search Results (5 found)
   
   Source: [LinkedIn](url) ← User can click here
   Source: [Indeed](url)   ← Or click here
   Source: [Careers@Gov](url) ← Or here
   ```

4. **User clicks source link**
   ```
   → Opens in new browser tab
   → Shows original job posting
   → User can verify information
   → User can apply directly
   ```

## Code Behind the Display

### Markdown Hyperlink Format
```python
# In app.py - display_web_search_results()

if 'url' in result and result['url']:
    # Creates clickable link
    st.markdown(f"*Source: [{result['source']}]({result['url']})*")
    # Renders as: Source: [LinkedIn](https://linkedin.com/...)
else:
    # Falls back to plain text
    st.markdown(f"*Source: {result['source']}*")
    # Renders as: Source: LinkedIn (Limited)
```

### URL Construction Examples

**LinkedIn Job:**
```python
url = "https://www.linkedin.com/jobs/view/4341315847/"
# User sees: Source: LinkedIn (with hyperlink to this URL)
```

**Indeed Job:**
```python
job_id = "abc123def456"
url = f"https://sg.indeed.com/viewjob?jk={job_id}"
# User sees: Source: Indeed (with hyperlink to job posting)
```

**Search Fallback:**
```python
query = "Manager Museum Mindef"
url = f"https://jobs.careers.gov.sg/jobs?keywords={query}"
# User sees: Source: Careers@Gov (with hyperlink to search results)
```

## Benefits Visualization

### Information Flow

```
┌──────────────┐
│ User Input   │
│ (Company +   │
│  Job Title)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  AI Search   │
│  (Multiple   │
│   Portals)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ URL Capture  │ ← Intelligent extraction, NO hard-coding
│ (Dynamic     │
│  Discovery)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Display with │
│  Clickable   │
│  Hyperlinks  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ User Clicks  │
│ → Verifies   │
│ → Applies    │
└──────────────┘
```

### Trust & Transparency

**Without URL Sources:**
```
❌ Where did this information come from?
❌ Can I verify this is accurate?
❌ How do I apply for this job?
❌ Is this job still available?
```

**With URL Sources:**
```
✅ Click source to see original posting
✅ Verify information directly
✅ Apply on the original platform
✅ Check if job is still open
```

## Real-World Use Cases

### Case 1: Job Seeker
```
Scenario: Looking for Ministry of Defence positions

1. Enters: "Mindef" + "Manager"
2. Sees results from 5 portals
3. Clicks LinkedIn source link
4. Views full job details
5. Applies directly on LinkedIn
```

### Case 2: HR Professional
```
Scenario: Researching competitor job postings

1. Enters: "Google" + "Product Manager"
2. Sees how competitors describe the role
3. Clicks Indeed source link
4. Studies salary ranges
5. Benchmarks against own listings
```

### Case 3: Career Advisor
```
Scenario: Helping client prepare for interviews

1. Enters: Client's target company + role
2. Shows client the results
3. Client clicks Careers@Gov link
4. Reviews actual job requirements
5. Prepares targeted resume
```

## Summary

The URL source display provides:

1. **Transparency** - Users know where information comes from
2. **Verification** - Users can check original postings
3. **Convenience** - One-click access to apply
4. **Trust** - Builds confidence in AI-generated content
5. **Flexibility** - Works across multiple job portals

All achieved through **intelligent URL discovery**, not hard-coding! 🎯

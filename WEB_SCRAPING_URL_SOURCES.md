# Web Scraping URL Source Display

## Feature Overview
The ProfileEnhancer application now displays the source URL for each web scraping result, making it easy for users to verify information and access the original job postings.

## Implementation Details

### How URLs are Captured

#### 1. **LinkedIn Jobs** (Primary Source)
When scraping LinkedIn jobs, the system captures URLs in two ways:

**A. Direct URL Scraping:**
```python
# When user provides a LinkedIn URL directly
linkedin_url = "https://www.linkedin.com/jobs/view/4341315847/"
result = {
    'title': 'Manager (Museum Development & Governance)',
    'company': 'Ministry of Defence of Singapore',
    'description': '...',
    'source': 'LinkedIn',
    'url': 'https://www.linkedin.com/jobs/view/4341315847/'
}
```

**B. Auto-Search Discovery:**
```python
# When searching LinkedIn for jobs
# System finds job cards with URLs
job_url = card.find('a')['href']
# Returns the actual job posting URL found
```

**C. Search Fallback:**
```python
# If no specific jobs found, returns search URL
url = "https://www.linkedin.com/jobs/search?keywords=Manager+Museum&location=Singapore"
```

#### 2. **Indeed Jobs**
```python
# Extracts job ID from card
job_id = card.get('data-jk', '')
# Constructs direct job URL
url = f"https://sg.indeed.com/viewjob?jk={job_id}"

# Or returns search URL as fallback
url = "https://sg.indeed.com/jobs?q=Manager+Museum&l=Singapore"
```

#### 3. **JobStreet**
```python
# Returns search URL (scraping limited in cloud)
url = "https://www.jobstreet.com.sg/jobs?keywords=Manager+Museum"
```

#### 4. **MyCareersFuture** (Government Portal)
```python
# Returns search URL for government job portal
url = "https://www.mycareersfuture.gov.sg/search?search=Manager+Museum&sortBy=relevancy"
```

#### 5. **Careers@Gov** (Government Portal)
```python
# When job cards found, extracts actual job URLs
job_url = card.find('a')['href']
if not job_url.startswith('http'):
    job_url = 'https://jobs.careers.gov.sg' + job_url

# Or returns search URL as fallback
url = "https://jobs.careers.gov.sg/jobs?keywords=Manager+Museum"
```

### Display Implementation

#### UI Display (app.py)
```python
def display_web_search_results(results: List[Dict]):
    """Display web search results with clickable URLs."""
    for idx, result in enumerate(results, 1):
        st.markdown(f"**{idx}. {result['title']}** at *{result['company']}*")
        
        # Display source with URL if available
        if 'url' in result and result['url']:
            st.markdown(f"*Source: [{result['source']}]({result['url']})*")
        else:
            st.markdown(f"*Source: {result['source']}*")
        
        st.text(result['description'])
        st.divider()
```

**Result in UI:**
- **Clickable Link**: `Source: [LinkedIn](https://www.linkedin.com/jobs/view/4341315847/)`
- **Plain Text**: `Source: Indeed (Limited)` (when URL not available)

## User Experience

### Example Output

**When LinkedIn URL is scraped successfully:**
```
1. Manager (Museum Development & Governance) at Ministry of Defence of Singapore
Source: LinkedIn (https://www.linkedin.com/jobs/view/4341315847/)
[Job description here...]
```

**When Indeed job is found:**
```
2. Museum Manager at Ministry of Defence
Source: Indeed (https://sg.indeed.com/viewjob?jk=abc123def456)
[Job description here...]
```

**When search URL is provided:**
```
3. Manager (Museum Development & Governance) at Mindef
Source: MyCareersFuture (https://www.mycareersfuture.gov.sg/search?search=Manager+Museum&sortBy=relevancy)
[Job description here...]
```

## Technical Architecture

### Data Flow
```
1. User Input
   ↓
2. Scraper Functions (scraper.py)
   - search_linkedin()
   - search_indeed()
   - search_jobstreet()
   - search_mycareersfuture()
   - search_careers_gov_sg()
   ↓
3. Job Dictionary Created
   {
     'title': str,
     'company': str,
     'description': str,
     'source': str,
     'url': str (optional)  ← URL captured here
   }
   ↓
4. Display Function (app.py)
   - display_web_search_results()
   - Checks for 'url' key
   - Renders as hyperlink if available
   ↓
5. User sees clickable source
```

### URL Extraction Logic

**Priority System:**
1. **Best**: Actual job posting URL (LinkedIn, Indeed, Careers@Gov)
2. **Good**: Search results URL with query parameters
3. **Fallback**: No URL (shows plain text source)

**Code Pattern:**
```python
# All scrapers follow this pattern
job_data = {
    'title': title,
    'company': company,
    'description': description,
    'source': source_name
}

# Add URL if available
if job_url:
    job_data['url'] = job_url

return job_data
```

## AI-Assisted URL Discovery

The system does NOT hard-code specific URLs. Instead:

### Intelligent Search
```python
# Company name expansion for better search
if 'mindef' in company_lower:
    company_expanded = "Ministry of Defence Singapore"

# Builds search query
search_query = f"{job_title} {company_expanded}".strip()
search_url = f"https://www.linkedin.com/jobs/search?keywords={search_query}"
```

### Dynamic URL Construction
```python
# Extracts job ID from HTML
job_id = card.get('data-jk')

# Constructs URL dynamically
if job_id:
    url = f"https://sg.indeed.com/viewjob?jk={job_id}"
```

### HTML Parsing
```python
# Finds links in job cards
link_elem = card.find('a', href=True)
if link_elem and '/jobs/view/' in link_elem['href']:
    job_url = link_elem['href']
    
    # Makes it absolute if needed
    if not job_url.startswith('http'):
        job_url = 'https://www.linkedin.com' + job_url
```

## Benefits

### For Users
1. **Verification**: Can click to verify the original job posting
2. **Direct Access**: Quick access to apply on the original platform
3. **Trust**: Transparency about where information came from
4. **Bookmarking**: Can save the URL for later reference

### For Developers
1. **No Hard-Coding**: URLs discovered dynamically through scraping
2. **Flexible**: Works with any company or job title
3. **Maintainable**: URL patterns centralized in scraper functions
4. **Testable**: Easy to verify URL construction logic

## Example Use Cases

### Case 1: Ministry of Defence Manager Position
**Input:**
- Company: "Mindef"
- Job Title: "Manager (Museum Development & Governance)"
- LinkedIn URL: "https://www.linkedin.com/jobs/view/4341315847/"

**Output:**
```
📊 View Web Search Results (5 found)

1. Manager (Museum Development & Governance) at Ministry of Defence of Singapore
   Source: LinkedIn (https://www.linkedin.com/jobs/view/4341315847/)
   [Full job description from LinkedIn...]

2. Similar positions at Ministry of Defence
   Source: Indeed (https://sg.indeed.com/jobs?q=Manager+Museum+Mindef&l=Singapore)
   [Search results from Indeed...]

3. Government sector opportunities
   Source: Careers@Gov (https://jobs.careers.gov.sg/jobs?keywords=Manager+Museum)
   [Government job portal listings...]
```

### Case 2: Tech Position Search
**Input:**
- Company: "Google"
- Job Title: "Software Engineer"
- Web Search: Enabled

**Output:**
```
📊 View Web Search Results (5 found)

1. Software Engineer at Google
   Source: LinkedIn (https://www.linkedin.com/jobs/view/xyz123/)
   [LinkedIn job details...]

2. Software Engineer - Google Singapore
   Source: Indeed (https://sg.indeed.com/viewjob?jk=abc456)
   [Indeed job details...]

3. Software Engineer positions
   Source: MyCareersFuture (https://www.mycareersfuture.gov.sg/search?search=Software+Engineer+Google)
   [Government portal search...]
```

## URL Formats by Portal

### LinkedIn
- **Job Posting**: `https://www.linkedin.com/jobs/view/{job_id}/`
- **Search**: `https://www.linkedin.com/jobs/search?keywords={query}&location=Singapore`

### Indeed
- **Job Posting**: `https://sg.indeed.com/viewjob?jk={job_id}`
- **Search**: `https://sg.indeed.com/jobs?q={query}&l=Singapore`

### JobStreet
- **Search**: `https://www.jobstreet.com.sg/jobs?keywords={query}`

### MyCareersFuture
- **Search**: `https://www.mycareersfuture.gov.sg/search?search={query}&sortBy=relevancy`

### Careers@Gov
- **Job Posting**: `https://jobs.careers.gov.sg/job/{job_id}`
- **Search**: `https://jobs.careers.gov.sg/jobs?keywords={query}`

## Future Enhancements

### Potential Improvements
1. **URL Validation**: Check if URLs are still active
2. **Deep Linking**: Open URLs in specific sections (job description, apply button)
3. **Caching**: Store URLs to avoid repeated scraping
4. **Analytics**: Track which sources provide the most useful URLs
5. **QR Codes**: Generate QR codes for mobile access to job postings

### Advanced Features
1. **URL Shortening**: Shorten long URLs for cleaner display
2. **Archive Links**: Save job postings before they expire
3. **Multi-Language**: Support job URLs in different languages
4. **API Integration**: Use official APIs when available for better URL extraction

## Troubleshooting

### No URL Displayed
**Possible Reasons:**
1. Portal blocking scraper access
2. Job posting removed/expired
3. HTML structure changed
4. Network connectivity issues

**Solution:**
- Source name still displayed (e.g., "Source: LinkedIn (Search Limited)")
- User can manually search on the portal

### Incorrect URL
**Possible Reasons:**
1. Job ID extraction failed
2. URL construction logic outdated
3. Portal changed URL format

**Solution:**
- Update scraper URL patterns in `scraper.py`
- Test with known working URLs
- Check portal documentation for URL format changes

### Broken Links
**Possible Reasons:**
1. Job posting expired
2. Company removed listing
3. Portal changed URL structure

**Solution:**
- System still provides job information
- User can search manually using company + job title
- Fall back to search URLs which are more stable

## Code Locations

### Scraper Functions
- **File**: `scraper.py`
- **Functions**:
  - `search_linkedin()` - Lines 350+
  - `scrape_linkedin_job_url()` - Lines 193+
  - `search_indeed()` - Lines 42+
  - `search_jobstreet()` - Lines 103+
  - `search_mycareersfuture()` - Lines 132+
  - `search_careers_gov_sg()` - Lines 154+

### Display Function
- **File**: `app.py`
- **Function**: `display_web_search_results()` - Lines 87+

### Imports
- **File**: `app.py`
- **Line**: 8 - `from typing import List, Dict`

## Summary

This feature enhances transparency and usability by:
1. ✅ **Capturing URLs dynamically** through intelligent scraping
2. ✅ **Displaying sources as clickable hyperlinks** in the UI
3. ✅ **No hard-coding** - URLs discovered through AI-assisted search
4. ✅ **Graceful fallback** when URLs unavailable
5. ✅ **User-friendly** - Easy access to original job postings

The implementation follows the principle of **intelligent discovery over hard-coding**, aligning with the application's AI-first approach.

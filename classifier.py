# -*- coding: utf-8 -*-
"""
SSIC and SSO Classification Module
Determines appropriate Singapore Standard Industrial Classification (SSIC) and 
Singapore Standard Occupational Classification (SSO) codes based on job descriptions,
company names, and job titles.
"""

import pandas as pd
import re
from typing import Tuple, Optional, Dict, List
import logging
from difflib import SequenceMatcher
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SingaporeClassifier:
    """Classifier for SSIC and SSO codes based on job and company information."""
    
    def __init__(self, ssic_file: str = "ssic2025-classification-structure.xlsx", 
                 ssoc_file: str = "ssoc2024-classification-structure.xlsx"):
        """Initialize the classifier with classification data."""
        self.ssic_df = None
        self.ssoc_df = None
        self.load_classification_data(ssic_file, ssoc_file)
    
    def load_classification_data(self, ssic_file: str, ssoc_file: str) -> None:
        """Load SSIC and SSO classification data from Excel files."""
        try:
            # Load SSIC data
            self.ssic_df = pd.read_excel(ssic_file, skiprows=4)
            self.ssic_df.columns = ['SSIC_Code', 'SSIC_Title']
            self.ssic_df = self.ssic_df.dropna()
            
            # Load SSO data
            self.ssoc_df = pd.read_excel(ssoc_file, skiprows=4)
            self.ssoc_df.columns = ['SSO_Code', 'SSO_Title']
            self.ssoc_df = self.ssoc_df.dropna()
            
            logger.info(f"Loaded {len(self.ssic_df)} SSIC codes and {len(self.ssoc_df)} SSO codes")
            
        except Exception as e:
            logger.error(f"Error loading classification data: {str(e)}")
            raise
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate enhanced similarity score between two text strings."""
        # Basic sequence matcher
        basic_score = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # Word-level matching
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return basic_score
        
        # Jaccard similarity for word overlap
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard_score = len(intersection) / len(union) if union else 0
        
        # Weighted combination - emphasize word matching
        combined_score = (basic_score * 0.4) + (jaccard_score * 0.6)
        
        return combined_score
    
    def enhanced_text_matching(self, search_text: str, target_text: str) -> float:
        """Enhanced text matching with multiple algorithms."""
        search_words = set(search_text.lower().split())
        target_words = set(target_text.lower().split())
        
        if not search_words or not target_words:
            return 0.0
        
        # 1. Exact word matches
        exact_matches = search_words.intersection(target_words)
        exact_score = len(exact_matches) / len(search_words) if search_words else 0
        
        # 2. Partial word matches (substring)
        partial_matches = 0
        for search_word in search_words:
            for target_word in target_words:
                if len(search_word) >= 4 and (search_word in target_word or target_word in search_word):
                    partial_matches += 1
                    break
        partial_score = partial_matches / len(search_words) if search_words else 0
        
        # 3. Semantic similarity boost for related terms
        semantic_score = self._calculate_semantic_similarity(search_text, target_text)
        
        # Weighted combination
        final_score = (exact_score * 0.5) + (partial_score * 0.3) + (semantic_score * 0.2)
        
        return min(final_score, 1.0)
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using domain-specific synonyms."""
        # Technology synonyms
        tech_synonyms = {
            'software': ['application', 'program', 'system', 'platform', 'solution'],
            'development': ['programming', 'coding', 'engineering', 'building'],
            'data': ['information', 'analytics', 'intelligence', 'statistics'],
            'digital': ['electronic', 'online', 'technology', 'cyber'],
            'web': ['internet', 'online', 'website', 'portal'],
            'mobile': ['smartphone', 'app', 'cellular', 'wireless'],
            'cloud': ['distributed', 'remote', 'virtual', 'hosted'],
            'ai': ['artificial intelligence', 'machine learning', 'automation'],
        }
        
        # Business synonyms
        business_synonyms = {
            'management': ['administration', 'supervision', 'leadership', 'oversight'],
            'consulting': ['advisory', 'guidance', 'expertise', 'professional services'],
            'sales': ['marketing', 'business development', 'revenue', 'commercial'],
            'finance': ['financial', 'banking', 'investment', 'monetary'],
            'operations': ['production', 'manufacturing', 'processing', 'workflow'],
        }
        
        all_synonyms = {**tech_synonyms, **business_synonyms}
        
        score = 0.0
        text1_words = set(text1.lower().split())
        text2_words = set(text2.lower().split())
        
        for word1 in text1_words:
            for word2 in text2_words:
                # Direct match
                if word1 == word2:
                    score += 0.1
                # Synonym match
                else:
                    for key, synonyms in all_synonyms.items():
                        if word1 in synonyms and word2 in synonyms:
                            score += 0.08
                        elif word1 == key and word2 in synonyms:
                            score += 0.08
                        elif word2 == key and word1 in synonyms:
                            score += 0.08
        
        return min(score, 1.0)
    
    def find_best_ssic_match(self, company: str, job_description: str) -> Tuple[str, str, float]:
        """Find the best SSIC code match based on company and job description."""
        best_match = None
        best_score = 0.0
        best_code = ""
        best_title = ""
        
        # Create search text from company and job description
        search_text = f"{company} {job_description}".lower()
        
        # Prioritize 5-digit codes for highest specificity
        five_digit_codes = self.ssic_df[self.ssic_df['SSIC_Code'].astype(str).str.len() == 5].copy()
        
        # First try 5-digit codes with enhanced matching
        for _, row in five_digit_codes.iterrows():
            ssic_title = str(row['SSIC_Title']).lower()
            
            # Enhanced text matching
            text_score = self.enhanced_text_matching(search_text, ssic_title)
            
            # Extract and match industry keywords
            keywords = self._extract_industry_keywords(search_text)
            keyword_score = self._calculate_enhanced_keyword_score(keywords, ssic_title)
            
            # Check for specific industry terms in company name
            company_score = self._calculate_company_industry_score(company.lower(), ssic_title)
            
            # Boost score for high-confidence matches
            confidence_boost = 0.0
            if text_score > 0.7 or keyword_score > 0.8:
                confidence_boost = 0.2
            
            # Weighted combined score with confidence boost
            combined_score = (text_score * 0.4) + (keyword_score * 0.4) + (company_score * 0.2) + confidence_boost
            
            # Normalize to ensure it doesn't exceed 1.0
            combined_score = min(combined_score, 1.0)
            
            if combined_score > best_score:
                best_score = combined_score
                best_code = str(row['SSIC_Code'])
                best_title = str(row['SSIC_Title'])
        
        # If no good 5-digit match found (threshold lowered), try 4-digit codes
        if best_score < 0.4:  # Lowered threshold from 0.3
            four_digit_codes = self.ssic_df[self.ssic_df['SSIC_Code'].astype(str).str.len() == 4].copy()
            for _, row in four_digit_codes.iterrows():
                ssic_title = str(row['SSIC_Title']).lower()
                
                text_score = self.enhanced_text_matching(search_text, ssic_title)
                keywords = self._extract_industry_keywords(search_text)
                keyword_score = self._calculate_enhanced_keyword_score(keywords, ssic_title)
                company_score = self._calculate_company_industry_score(company.lower(), ssic_title)
                
                # Slightly lower confidence boost for 4-digit codes
                confidence_boost = 0.0
                if text_score > 0.6 or keyword_score > 0.7:
                    confidence_boost = 0.15
                
                combined_score = (text_score * 0.4) + (keyword_score * 0.4) + (company_score * 0.2) + confidence_boost
                combined_score = min(combined_score, 1.0)
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_code = str(row['SSIC_Code'])
                    best_title = str(row['SSIC_Title'])
        
        # Apply final confidence boost if we have a reasonable match
        if best_score > 0.5:
            best_score = min(best_score * 1.2, 1.0)  # 20% boost for good matches
        
        return best_code, best_title, best_score
    
    def find_best_sso_match(self, company: str, job_title: str, job_description: str) -> Tuple[str, str, float]:
        """Find the best SSO code match based on company, job title and FULL job description."""
        best_match = None
        best_score = 0.0
        best_code = ""
        best_title = ""
        
        # Create comprehensive search text from all available information
        search_text = f"{company} {job_title} {job_description}".lower()
        
        # Prioritize 5-digit codes for highest specificity
        five_digit_codes = self.ssoc_df[self.ssoc_df['SSO_Code'].astype(str).str.len() == 5].copy()
        
        # First try 5-digit codes with enhanced matching
        for _, row in five_digit_codes.iterrows():
            sso_title = str(row['SSO_Title']).lower()
            
            # Enhanced similarity scores
            title_score = self.enhanced_text_matching(job_title.lower(), sso_title)
            desc_score = self.enhanced_text_matching(job_description.lower(), sso_title)
            
            # Extract and match job-specific keywords
            job_keywords = self._extract_job_keywords(search_text)
            keyword_score = self._calculate_enhanced_keyword_score(job_keywords, sso_title)
            
            # Enhanced exact job title matching
            exact_match_score = self._calculate_enhanced_job_match(job_title.lower(), sso_title)
            
            # Boost score for high-confidence job matches
            confidence_boost = 0.0
            if title_score > 0.7 or exact_match_score > 0.8:
                confidence_boost = 0.25
            elif keyword_score > 0.7:
                confidence_boost = 0.15
            
            # Weighted combined score emphasizing job title and exact matches
            combined_score = (title_score * 0.35) + (desc_score * 0.15) + (keyword_score * 0.25) + (exact_match_score * 0.25) + confidence_boost
            
            # Normalize to ensure it doesn't exceed 1.0
            combined_score = min(combined_score, 1.0)
            
            if combined_score > best_score:
                best_score = combined_score
                best_code = str(row['SSO_Code'])
                best_title = str(row['SSO_Title'])
        
        # If no good 5-digit match found (threshold lowered), try 4-digit codes
        if best_score < 0.4:  # Lowered threshold
            four_digit_codes = self.ssoc_df[self.ssoc_df['SSO_Code'].astype(str).str.len() == 4].copy()
            for _, row in four_digit_codes.iterrows():
                sso_title = str(row['SSO_Title']).lower()
                
                title_score = self.enhanced_text_matching(job_title.lower(), sso_title)
                desc_score = self.enhanced_text_matching(job_description.lower(), sso_title)
                job_keywords = self._extract_job_keywords(search_text)
                keyword_score = self._calculate_enhanced_keyword_score(job_keywords, sso_title)
                exact_match_score = self._calculate_enhanced_job_match(job_title.lower(), sso_title)
                
                # Slightly lower confidence boost for 4-digit codes
                confidence_boost = 0.0
                if title_score > 0.6 or exact_match_score > 0.7:
                    confidence_boost = 0.2
                elif keyword_score > 0.6:
                    confidence_boost = 0.1
                
                combined_score = (title_score * 0.35) + (desc_score * 0.15) + (keyword_score * 0.25) + (exact_match_score * 0.25) + confidence_boost
                combined_score = min(combined_score, 1.0)
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_code = str(row['SSO_Code'])
                    best_title = str(row['SSO_Title'])
        
        # Apply final confidence boost for good matches
        if best_score > 0.5:
            best_score = min(best_score * 1.25, 1.0)  # 25% boost for good matches
        
        return best_code, best_title, best_score
    
    def _extract_industry_keywords(self, text: str) -> List[str]:
        """Extract industry-related keywords from text."""
        industry_keywords = [
            # Technology
            'technology', 'tech', 'software', 'it', 'information technology', 'digital', 'cyber', 'cybersecurity',
            'programming', 'development', 'web', 'mobile', 'cloud', 'ai', 'artificial intelligence', 'machine learning',
            'data', 'analytics', 'blockchain', 'fintech', 'saas', 'platform', 'api', 'database',
            
            # Manufacturing & Industry
            'manufacturing', 'production', 'factory', 'assembly', 'industrial', 'automotive', 'electronics',
            'machinery', 'equipment', 'processing', 'packaging', 'quality control', 'supply chain',
            
            # Finance & Banking
            'finance', 'financial', 'banking', 'insurance', 'investment', 'wealth management', 'accounting',
            'audit', 'compliance', 'risk', 'trading', 'fund', 'capital', 'securities', 'fintech',
            
            # Healthcare & Medical
            'healthcare', 'medical', 'hospital', 'clinic', 'pharmaceutical', 'biotech', 'nursing',
            'therapy', 'treatment', 'patient', 'clinical', 'diagnostic', 'surgery', 'medicine',
            
            # Education & Training
            'education', 'school', 'university', 'training', 'teaching', 'learning', 'academic',
            'curriculum', 'instruction', 'research', 'student', 'faculty', 'tuition',
            
            # Retail & Commerce
            'retail', 'sales', 'shop', 'store', 'commerce', 'ecommerce', 'shopping', 'customer',
            'merchandise', 'inventory', 'outlet', 'chain', 'franchise', 'marketplace',
            
            # Construction & Real Estate
            'construction', 'building', 'engineering', 'architecture', 'real estate', 'property',
            'development', 'infrastructure', 'civil', 'structural', 'contractor',
            
            # Logistics & Transportation
            'logistics', 'transport', 'shipping', 'delivery', 'freight', 'warehouse', 'distribution',
            'supply chain', 'courier', 'trucking', 'maritime', 'aviation', 'rail',
            
            # Hospitality & Food
            'hospitality', 'hotel', 'restaurant', 'food', 'tourism', 'catering', 'beverage',
            'accommodation', 'travel', 'resort', 'dining', 'culinary',
            
            # Communications & Media
            'telecommunications', 'telecom', 'communications', 'media', 'broadcasting', 'publishing',
            'advertising', 'marketing', 'public relations', 'journalism', 'content',
            
            # Others
            'agriculture', 'farming', 'agricultural', 'government', 'public', 'civil service',
            'consulting', 'advisory', 'professional services', 'legal', 'law',
            'energy', 'utilities', 'power', 'oil', 'gas', 'renewable', 'sustainability',
            'research', 'laboratory', 'scientific', 'innovation'
        ]
        
        found_keywords = []
        for keyword in industry_keywords:
            if keyword in text.lower():
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_job_keywords(self, text: str) -> List[str]:
        """Extract job role related keywords from text."""
        job_keywords = [
            # Technology & IT (Enhanced)
            'software engineer', 'software developer', 'web developer', 'mobile developer', 'full stack developer',
            'frontend developer', 'backend developer', 'devops engineer', 'cloud engineer', 'system engineer',
            'data scientist', 'data analyst', 'data engineer', 'machine learning engineer', 'ai engineer',
            'product manager', 'technical product manager', 'scrum master', 'agile coach',
            'ui designer', 'ux designer', 'product designer', 'graphic designer', 'web designer',
            'system administrator', 'database administrator', 'network administrator', 'security engineer',
            'cybersecurity analyst', 'information security', 'technical writer', 'qa engineer', 'test engineer',
            
            # Management & Leadership (Enhanced)
            'chief executive officer', 'ceo', 'managing director', 'general manager', 'country manager',
            'vice president', 'vp', 'director', 'senior director', 'associate director',
            'department head', 'team lead', 'team leader', 'project manager', 'program manager',
            'operations manager', 'business manager', 'relationship manager', 'account manager',
            
            # Finance & Accounting (Enhanced)
            'financial analyst', 'investment analyst', 'credit analyst', 'risk analyst', 'business analyst',
            'financial advisor', 'wealth manager', 'portfolio manager', 'fund manager',
            'accountant', 'senior accountant', 'accounting manager', 'finance manager', 'cfo',
            'auditor', 'internal auditor', 'external auditor', 'compliance officer', 'risk manager',
            'treasury analyst', 'budget analyst', 'cost analyst', 'tax specialist',
            
            # Sales & Marketing (Enhanced) 
            'sales manager', 'sales director', 'sales representative', 'account executive',
            'business development manager', 'business development', 'partnership manager',
            'marketing manager', 'digital marketing manager', 'brand manager', 'product marketing',
            'marketing director', 'communications manager', 'public relations', 'content manager',
            'social media manager', 'seo specialist', 'digital marketing specialist',
            
            # Human Resources (Enhanced)
            'hr manager', 'human resources manager', 'hr director', 'hr business partner',
            'recruiter', 'senior recruiter', 'talent acquisition', 'recruitment consultant',
            'hr generalist', 'hr specialist', 'compensation analyst', 'benefits administrator',
            'learning and development', 'training manager', 'organizational development',
            
            # Operations & Production (Enhanced)
            'operations manager', 'operations director', 'supply chain manager', 'logistics manager',
            'warehouse manager', 'production manager', 'manufacturing manager', 'plant manager',
            'quality manager', 'quality assurance', 'quality control', 'process engineer',
            'industrial engineer', 'manufacturing engineer', 'production supervisor',
            
            # Consulting & Professional Services (Enhanced)
            'consultant', 'senior consultant', 'principal consultant', 'management consultant',
            'strategy consultant', 'business consultant', 'it consultant', 'financial consultant',
            'advisory', 'advisor', 'senior advisor', 'subject matter expert', 'specialist',
            
            # Healthcare & Medical (Enhanced)
            'doctor', 'physician', 'medical doctor', 'surgeon', 'specialist doctor',
            'nurse', 'registered nurse', 'senior nurse', 'nurse manager', 'nursing supervisor',
            'pharmacist', 'clinical pharmacist', 'hospital pharmacist', 'medical technician',
            'radiologist', 'pathologist', 'anesthesiologist', 'cardiologist', 'neurologist',
            'physical therapist', 'occupational therapist', 'medical assistant',
            
            # Education & Training (Enhanced)
            'teacher', 'senior teacher', 'principal', 'vice principal', 'head of department',
            'professor', 'associate professor', 'assistant professor', 'lecturer', 'instructor',
            'trainer', 'corporate trainer', 'training specialist', 'curriculum developer',
            'education consultant', 'academic advisor', 'student counselor', 'librarian',
            
            # Legal & Compliance (Enhanced)
            'lawyer', 'senior lawyer', 'legal counsel', 'general counsel', 'legal advisor',
            'paralegal', 'legal assistant', 'compliance officer', 'regulatory affairs',
            'contract manager', 'legal manager', 'litigation lawyer', 'corporate lawyer',
            
            # Administrative & Support (Enhanced)
            'executive assistant', 'administrative assistant', 'personal assistant', 'secretary',
            'office manager', 'administrative coordinator', 'data entry', 'clerk',
            'receptionist', 'customer service representative', 'call center agent',
            'help desk', 'technical support', 'customer support specialist',
            
            # Creative & Design (Enhanced)
            'creative director', 'art director', 'graphic designer', 'visual designer',
            'multimedia designer', 'video editor', 'photographer', 'videographer',
            'copywriter', 'content writer', 'technical writer', 'editor', 'proofreader',
            'animator', 'illustrator', 'game designer', '3d artist',
            
            # Engineering & Technical (Enhanced)
            'mechanical engineer', 'electrical engineer', 'civil engineer', 'chemical engineer',
            'biomedical engineer', 'aerospace engineer', 'environmental engineer',
            'structural engineer', 'design engineer', 'project engineer', 'site engineer',
            'technician', 'senior technician', 'engineering technician', 'lab technician',
            'maintenance technician', 'field technician', 'service technician'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        # Sort by length (longest first) to catch compound terms first
        sorted_keywords = sorted(job_keywords, key=len, reverse=True)
        
        for keyword in sorted_keywords:
            if keyword in text_lower and keyword not in found_keywords:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_keyword_score(self, keywords: List[str], target_text: str) -> float:
        """Calculate keyword match score."""
        if not keywords:
            return 0.0
        
        matches = sum(1 for keyword in keywords if keyword in target_text.lower())
        return matches / len(keywords)
    
    def _calculate_enhanced_keyword_score(self, keywords: List[str], target_text: str) -> float:
        """Enhanced keyword matching with partial matches and weights."""
        if not keywords:
            return 0.0
        
        target_lower = target_text.lower()
        exact_matches = 0
        partial_matches = 0
        
        for keyword in keywords:
            if keyword in target_lower:
                exact_matches += 1
            else:
                # Check for partial matches (root words)
                keyword_root = keyword[:max(4, len(keyword)-2)]  # Get root of keyword
                if len(keyword_root) >= 4 and keyword_root in target_lower:
                    partial_matches += 1
        
        # Weight exact matches more than partial matches
        score = (exact_matches * 1.0 + partial_matches * 0.7) / len(keywords)
        return min(score, 1.0)
    
    def _calculate_company_industry_score(self, company_name: str, ssic_title: str) -> float:
        """Calculate industry score based on company name patterns."""
        industry_patterns = {
            'technology': ['tech', 'software', 'systems', 'solutions', 'digital', 'cyber', 'data', 'ai', 'cloud'],
            'consulting': ['consulting', 'advisory', 'professional services', 'management'],
            'financial': ['bank', 'finance', 'capital', 'investment', 'wealth', 'insurance'],
            'healthcare': ['health', 'medical', 'clinic', 'hospital', 'pharma', 'bio'],
            'education': ['education', 'school', 'university', 'institute', 'academy'],
            'manufacturing': ['manufacturing', 'production', 'industrial', 'factory', 'engineering'],
            'retail': ['retail', 'store', 'shop', 'mart', 'supermarket', 'mall'],
            'logistics': ['logistics', 'transport', 'shipping', 'delivery', 'supply', 'warehouse'],
            'construction': ['construction', 'building', 'property', 'real estate', 'development'],
            'government': ['government', 'ministry', 'authority', 'agency', 'public', 'statutory']
        }
        
        score = 0.0
        for industry, patterns in industry_patterns.items():
            if any(pattern in company_name for pattern in patterns):
                if industry in ssic_title:
                    score += 0.8
                elif any(pattern in ssic_title for pattern in patterns):
                    score += 0.5
        
        return min(score, 1.0)
    
    def _calculate_exact_job_match(self, job_title: str, sso_title: str) -> float:
        """Calculate exact job title match score."""
        # Common job title variations
        job_synonyms = {
            'software engineer': ['software developer', 'programmer', 'software engineer'],
            'data scientist': ['data analyst', 'data engineer', 'data scientist'],
            'manager': ['supervisor', 'head', 'director', 'lead', 'manager'],
            'analyst': ['specialist', 'consultant', 'analyst', 'associate'],
            'executive': ['officer', 'executive', 'coordinator'],
            'assistant': ['associate', 'assistant', 'support'],
            'designer': ['designer', 'creative', 'artist'],
            'accountant': ['accountant', 'financial analyst', 'finance'],
            'teacher': ['educator', 'instructor', 'trainer', 'teacher'],
            'nurse': ['nursing', 'nurse', 'healthcare'],
            'engineer': ['engineer', 'technician', 'specialist']
        }
        
        # Direct word matching
        job_words = set(job_title.lower().split())
        sso_words = set(sso_title.lower().split())
        
        # Calculate word overlap
        overlap = len(job_words.intersection(sso_words))
        total_words = len(job_words.union(sso_words))
        
        if total_words == 0:
            return 0.0
        
        base_score = overlap / total_words
        
        # Boost score for synonym matches
        for job_type, synonyms in job_synonyms.items():
            if any(word in job_title.lower() for word in synonyms):
                if any(word in sso_title.lower() for word in synonyms):
                    base_score += 0.3
        
        return min(base_score, 1.0)
    
    def _calculate_enhanced_job_match(self, job_title: str, sso_title: str) -> float:
        """Enhanced job title matching with better algorithms."""
        # Extended job title variations and synonyms
        job_synonyms = {
            'software engineer': ['software developer', 'programmer', 'application developer', 'systems developer'],
            'software developer': ['software engineer', 'programmer', 'application developer', 'web developer'],
            'data scientist': ['data analyst', 'data engineer', 'business analyst', 'research scientist'],
            'data analyst': ['business analyst', 'data scientist', 'research analyst', 'intelligence analyst'],
            'manager': ['supervisor', 'head', 'director', 'lead', 'team lead', 'senior manager'],
            'senior manager': ['director', 'head', 'manager', 'supervisor', 'team lead'],
            'analyst': ['specialist', 'consultant', 'associate', 'researcher'],
            'specialist': ['expert', 'consultant', 'analyst', 'advisor'],
            'executive': ['officer', 'coordinator', 'administrator', 'manager'],
            'assistant': ['associate', 'support', 'coordinator', 'helper'],
            'designer': ['creative', 'artist', 'stylist', 'developer'],
            'accountant': ['financial analyst', 'bookkeeper', 'finance officer', 'auditor'],
            'teacher': ['educator', 'instructor', 'trainer', 'lecturer', 'professor'],
            'engineer': ['technician', 'specialist', 'developer', 'architect'],
            'developer': ['engineer', 'programmer', 'builder', 'creator'],
            'consultant': ['advisor', 'specialist', 'expert', 'counselor'],
            'coordinator': ['organizer', 'administrator', 'manager', 'supervisor'],
            'technician': ['specialist', 'engineer', 'mechanic', 'operator']
        }
        
        # Direct word matching with enhanced scoring
        job_words = set(job_title.lower().split())
        sso_words = set(sso_title.lower().split())
        
        # Exact word matches
        exact_overlap = len(job_words.intersection(sso_words))
        total_words = len(job_words.union(sso_words))
        
        if total_words == 0:
            return 0.0
        
        base_score = exact_overlap / total_words
        
        # Enhanced synonym matching
        synonym_boost = 0.0
        for job_word in job_words:
            for sso_word in sso_words:
                # Direct synonym match
                if job_word in job_synonyms.get(sso_word, []) or sso_word in job_synonyms.get(job_word, []):
                    synonym_boost += 0.4
                # Partial word matching for compound terms
                elif len(job_word) >= 4 and len(sso_word) >= 4:
                    if job_word in sso_word or sso_word in job_word:
                        synonym_boost += 0.2
        
        # Seniority level matching
        seniority_levels = ['junior', 'senior', 'lead', 'principal', 'chief', 'head']
        job_seniority = any(level in job_title.lower() for level in seniority_levels)
        sso_seniority = any(level in sso_title.lower() for level in seniority_levels)
        
        seniority_boost = 0.1 if job_seniority == sso_seniority else 0.0
        
        # Final score calculation
        final_score = base_score + synonym_boost + seniority_boost
        
        return min(final_score, 1.0)
    
    def generate_company_description(self, company_name: str, job_title: str, 
                                   job_description: str, api_key: str) -> str:
        """
        Use AI to generate a company description specifically for SSIC industry classification.
        
        Args:
            company_name: Name of the company
            job_title: Job title being offered (for context)
            job_description: Job description content (for context)
            api_key: OpenAI API key
            
        Returns:
            Generated company description focusing on industry, business activities, and sector
        """
        try:
            client = OpenAI(api_key=api_key)
            
            prompt = f"""Based on the company name and job information provided, generate a brief company description that focuses EXCLUSIVELY on the company's industry sector and primary business activities. This will be used specifically for Singapore Standard Industrial Classification (SSIC) purposes.

Company Name: {company_name}
Job Title: {job_title}
Job Description: {job_description[:400]}...

Generate a concise 2-3 sentence company description that includes:

1. PRIMARY INDUSTRY SECTOR (e.g., Technology, Financial Services, Manufacturing, Retail, Healthcare, Education, Construction, etc.)
2. CORE BUSINESS ACTIVITIES (e.g., software development, banking services, manufacturing of electronics, retail sales, consulting services)  
3. PRIMARY BUSINESS MODEL (e.g., B2B services, B2C products, consulting, platform, manufacturing, etc.)

Focus on industry classification keywords. Avoid job-specific details.

Examples:
- "Google is a technology company specializing in software development, cloud computing services, and digital advertising platforms. The company provides internet-related services including search engines, online advertising technologies, and cloud computing solutions primarily to businesses and consumers globally."
- "DBS Bank is a financial services institution providing comprehensive banking and financial services. The company offers retail banking, corporate banking, investment banking, and wealth management services to individuals, businesses, and institutional clients."

Company Description for SSIC Classification:"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in business industry analysis. Generate company descriptions that clearly identify the industry sector and core business activities for accurate industrial classification. Focus on WHAT the company does (industry) not WHO they hire (jobs)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=250
            )
            
            company_description = response.choices[0].message.content.strip()
            logger.info(f"Generated industry-focused company description for {company_name}")
            return company_description
            
        except Exception as e:
            logger.warning(f"Failed to generate company description: {str(e)}")
            # Fallback to basic industry description based on company name
            return f"{company_name} is a company operating in the business sector related to its core activities and services."
    
    def _ai_enhanced_ssic_classification(self, company: str, company_description: str, 
                                       sso_code: str, sso_title: str, 
                                       api_key: str) -> Tuple[str, str, float]:
        """
        Use AI to determine the most appropriate 5-digit SSIC code based on Company Analysis 
        and ensuring compatibility with SSO classification.
        
        Args:
            company: Company name
            company_description: AI-generated company description 
            sso_code: Previously determined SSO code
            sso_title: Previously determined SSO title
            api_key: OpenAI API key
            
        Returns:
            Tuple of (ssic_code, ssic_title, confidence_score)
        """
        try:
            client = OpenAI(api_key=api_key)
            
            # Get top candidate SSIC codes using company analysis
            candidates = self._get_ssic_candidates_from_company_analysis(company_description)
            
            # Filter for 5-digit codes only
            five_digit_candidates = [(code, title, score) for code, title, score in candidates if len(code) == 5][:15]
            
            # Create AI prompt for SSIC reasoning with SSO compatibility
            candidates_text = "\n".join([f"- {code}: {title}" for code, title, _ in five_digit_candidates])
            
            prompt = f"""You are an expert in Singapore Standard Industrial Classification (SSIC 2025). Determine the most appropriate 5-DIGIT SSIC code based on the company analysis and ensuring compatibility with the occupation classification.

Company Name: {company}
Company Analysis: {company_description}

Occupation Classification (SSO 2024):
- Code: {sso_code}
- Title: {sso_title}

IMPORTANT REQUIREMENTS:
1. Must be a 5-DIGIT SSIC code for maximum specificity
2. Based primarily on the Company Analysis (business activities)
3. Must be logically compatible with the SSO occupation code
4. Consider industry-occupation compatibility

Top 5-digit SSIC candidates:
{candidates_text}

Key Guidelines:
1. Technology companies (software, IT): Use 62011 (Software development) or 62021 (IT consultancy)
2. Banks/Financial institutions: Use 641xx, 642xx, 649xx codes  
3. Government agencies: Use appropriate 841xx codes
4. Healthcare organizations: Use 861xx codes
5. Manufacturing companies: Use specific 1xxxx-3xxxx codes
6. Retail companies: Use 47xxx codes only if they sell directly to consumers
7. Consulting firms: Use 70xxx or 62021 codes

Compatibility Check:
- Software Developer (SSO 25121) → Technology company (SSIC 62011)
- Financial Analyst (SSO 24131) → Financial services (SSIC 641xx) 
- Management Consultant (SSO 24211) → Consulting firm (SSIC 70xxx)
- Government Officer → Government agency (SSIC 841xx)

Respond with ONLY the 5-digit SSIC code that best matches the company's business activities while being compatible with the occupation.

SSIC Code:"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in Singapore industrial classification. Provide only 5-digit SSIC codes that reflect company business activities and are compatible with occupation codes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            ai_suggested_code = response.choices[0].message.content.strip()
            
            # Validate and find the suggested code in our database
            try:
                ai_code_clean = ''.join(filter(str.isdigit, ai_suggested_code))[:5]
                if len(ai_code_clean) == 5:  # Ensure 5-digit code
                    matching_row = self.ssic_df[self.ssic_df['SSIC_Code'].astype(str) == ai_code_clean]
                    
                    if not matching_row.empty:
                        ssic_code = ai_code_clean
                        ssic_title = matching_row.iloc[0]['SSIC_Title']
                        confidence = 0.90  # High confidence for AI reasoning with SSO compatibility
                        logger.info(f"AI-enhanced SSIC classification (5-digit, SSO-compatible): {ssic_code} - {ssic_title}")
                        return ssic_code, ssic_title, confidence
            except:
                pass
            
            # Fallback to best 5-digit traditional match if AI fails
            logger.warning("AI SSIC classification failed, falling back to best 5-digit traditional matching")
            return self._find_best_5digit_ssic_match(company, company_description, sso_code)
            
        except Exception as e:
            logger.error(f"Error in AI SSIC classification: {str(e)}")
            # Fallback to traditional matching - ensure 5-digit
            return self._find_best_5digit_ssic_match(company, company_description, sso_code)
    
    def _get_ssic_candidates_from_company_analysis(self, company_description: str) -> List[Tuple[str, str, float]]:
        """Get top SSIC code candidates using ONLY company analysis."""
        search_text = company_description.lower()
        candidates = []
        
        for _, row in self.ssic_df.iterrows():
            ssic_code = str(row['SSIC_Code'])
            ssic_title = str(row['SSIC_Title'])
            
            # Scoring based ONLY on company analysis
            text_score = self.enhanced_text_matching(search_text, ssic_title.lower())
            keywords = self._extract_industry_keywords(search_text)
            keyword_score = self._calculate_enhanced_keyword_score(keywords, ssic_title.lower())
            
            # Company name pattern matching
            company_pattern_score = self._calculate_company_industry_score(search_text, ssic_title.lower())
            
            # Weighted combination - focus on company analysis only
            combined_score = (text_score * 0.4) + (keyword_score * 0.4) + (company_pattern_score * 0.2)
            candidates.append((ssic_code, ssic_title, combined_score))
        
        # Sort by score and return top candidates
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates
    
    def _find_best_5digit_ssic_match(self, company: str, company_description: str, 
                                    sso_code: str = None) -> Tuple[str, str, float]:
        """Find the best 5-digit SSIC code match based on company analysis and SSO compatibility."""
        best_match = None
        best_score = 0.0
        best_code = ""
        best_title = ""
        
        # Create search text from company and company description
        search_text = f"{company} {company_description}".lower()
        
        # Focus on 5-digit codes only for maximum specificity
        five_digit_codes = self.ssic_df[self.ssic_df['SSIC_Code'].astype(str).str.len() == 5].copy()
        
        for _, row in five_digit_codes.iterrows():
            ssic_code = str(row['SSIC_Code'])
            ssic_title = str(row['SSIC_Title']).lower()
            
            # Enhanced text matching based on company analysis
            text_score = self.enhanced_text_matching(search_text, ssic_title)
            
            # Extract and match industry keywords from company analysis
            keywords = self._extract_industry_keywords(search_text)
            keyword_score = self._calculate_enhanced_keyword_score(keywords, ssic_title)
            
            # Check for specific industry terms in company name/analysis
            company_score = self._calculate_company_industry_score(search_text, ssic_title)
            
            # SSO-SSIC compatibility boost if SSO code provided
            compatibility_boost = 0.0
            if sso_code:
                compatibility_boost = self._calculate_ssic_sso_compatibility(ssic_code, sso_code)
            
            # Boost score for high-confidence matches
            confidence_boost = 0.0
            if text_score > 0.7 or keyword_score > 0.8:
                confidence_boost = 0.2
            
            # Weighted combined score with compatibility boost
            combined_score = (text_score * 0.3) + (keyword_score * 0.3) + (company_score * 0.2) + (compatibility_boost * 0.2) + confidence_boost
            
            # Normalize to ensure it doesn't exceed 1.0
            combined_score = min(combined_score, 1.0)
            
            if combined_score > best_score:
                best_score = combined_score
                best_code = ssic_code
                best_title = str(row['SSIC_Title'])
        
        # Apply final confidence boost for good matches
        if best_score > 0.5:
            best_score = min(best_score * 1.2, 1.0)  # 20% boost for good matches
        
        # If no good match found, return a default 5-digit code
        if not best_code:
            best_code = "99999"
            best_title = "Other activities not elsewhere specified"
            best_score = 0.2
        
        return best_code, best_title, best_score
    
    def _calculate_ssic_sso_compatibility(self, ssic_code: str, sso_code: str) -> float:
        """Calculate compatibility score between SSIC industry and SSO occupation."""
        if not ssic_code or not sso_code:
            return 0.0
        
        # Define known compatible SSIC-SSO patterns
        compatibility_patterns = {
            # Technology Industry (62xxx) 
            '62': {
                'compatible_sso_prefixes': ['251', '252', '121', '132', '242'],  # Tech roles, managers
                'score': 0.8
            },
            # Financial Services (64xxx, 66xxx)
            '64': {
                'compatible_sso_prefixes': ['241', '121', '122', '131'],  # Finance roles, managers  
                'score': 0.8
            },
            '66': {
                'compatible_sso_prefixes': ['241', '121', '122', '131'],  # Finance roles, managers
                'score': 0.8
            },
            # Government (841xx)
            '841': {
                'compatible_sso_prefixes': ['111', '112', '121', '242', '251'],  # Officials, managers, analysts
                'score': 0.9
            },
            # Healthcare (861xx) 
            '861': {
                'compatible_sso_prefixes': ['221', '222', '321', '322'],  # Medical professionals
                'score': 0.9
            },
            # Manufacturing (1xxxx-3xxxx)
            '1': {
                'compatible_sso_prefixes': ['214', '215', '311', '312', '121'],  # Engineers, technicians, managers
                'score': 0.7
            },
            '2': {
                'compatible_sso_prefixes': ['214', '215', '311', '312', '121'],  # Engineers, technicians, managers  
                'score': 0.7
            },
            '3': {
                'compatible_sso_prefixes': ['214', '215', '311', '312', '121'],  # Engineers, technicians, managers
                'score': 0.7
            },
            # Professional Services (70xxx)
            '70': {
                'compatible_sso_prefixes': ['242', '121', '122'],  # Consultants, managers
                'score': 0.8
            },
            # Retail (47xxx)
            '47': {
                'compatible_sso_prefixes': ['333', '334', '121', '132'],  # Sales, managers
                'score': 0.7
            }
        }
        
        # Check compatibility patterns
        ssic_prefix = ssic_code[:2]
        if ssic_prefix in compatibility_patterns:
            pattern = compatibility_patterns[ssic_prefix]
            sso_prefix = sso_code[:3]
            
            for compatible_prefix in pattern['compatible_sso_prefixes']:
                if sso_prefix.startswith(compatible_prefix):
                    return pattern['score']
        
        # Special 3-digit SSIC patterns for government
        if ssic_code.startswith('841'):
            if sso_code.startswith('11') or sso_code.startswith('24') or sso_code.startswith('25'):
                return 0.9
        
        # Default compatibility for management roles (can work in any industry)
        if sso_code.startswith('11') or sso_code.startswith('12'):  # Senior managers
            return 0.5
        
        return 0.0  # No specific compatibility found
    
    def _ai_enhanced_sso_classification(self, company: str, job_title: str, 
                                       job_description: str, api_key: str) -> Tuple[str, str, float]:
        """
        Use AI to determine the most appropriate SSO code by reasoning about the job role.
        
        Args:
            company: Company name
            job_title: Job title  
            job_description: Job description
            api_key: OpenAI API key
            
        Returns:
            Tuple of (sso_code, sso_title, confidence_score)
        """
        try:
            client = OpenAI(api_key=api_key)
            
            # Get top candidate SSO codes using traditional matching first
            candidates = self._get_sso_candidates(company, job_title, job_description)
            
            # Create AI prompt for SSO reasoning
            candidates_text = "\n".join([f"- {code}: {title}" for code, title, _ in candidates[:15]])
            
            prompt = f"""You are an expert in Singapore Standard Occupational Classification (SSO 2024). Based on the job information provided, determine the most appropriate SSO code.

Company: {company}
Job Title: {job_title}
Job Description: {job_description[:400]}...

Here are the top candidate SSO codes:
{candidates_text}

Key Guidelines for Common Job Titles:
1. Software Engineer/Developer: 25121 (Software developer)
2. Data Scientist/Data Analyst: 21223 (Data scientist) or 24131 (Financial analyst) if finance-focused
3. Product Manager: 24221 (Business analyst) or 11202 (Company director) for senior roles
4. Financial Analyst: 24131 (Financial analyst)
5. HR Manager: 12122 (Human resource manager)
6. Marketing Manager: 12132 (Sales and marketing manager)
7. Business Analyst: 24221 (Business analyst)
8. Project Manager: 11201 (Finance manager) or 24221 (Business analyst) depending on focus
9. Senior/Lead roles: Look for appropriate senior/management codes
10. Specialist roles: Use specific technical specialist codes when available

Important Considerations:
- Consider the seniority level (Senior, Lead, Principal, Manager, Director)
- Look at actual responsibilities, not just job title
- For emerging tech roles (DevOps, Data Engineer), find the closest traditional equivalent
- Management roles should use 1xxxx codes when appropriate
- Technical roles should use 2xxxx codes
- Consider industry context (finance vs tech vs healthcare)

Respond with ONLY the 5-digit SSO code that best matches this specific job role and responsibilities.

SSO Code:"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in Singapore occupational classification. Provide only the most appropriate 5-digit SSO code based on the job title and responsibilities."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            ai_suggested_code = response.choices[0].message.content.strip()
            
            # Validate and find the suggested code in our database
            try:
                ai_code_clean = ''.join(filter(str.isdigit, ai_suggested_code))[:5]
                matching_row = self.ssoc_df[self.ssoc_df['SSO_Code'].astype(str) == ai_code_clean]
                
                if not matching_row.empty:
                    sso_code = ai_code_clean
                    sso_title = matching_row.iloc[0]['SSO_Title']
                    confidence = 0.90  # High confidence for AI reasoning
                    logger.info(f"AI-enhanced SSO classification: {sso_code} - {sso_title}")
                    return sso_code, sso_title, confidence
            except:
                pass
            
            # Fallback to traditional matching if AI fails
            logger.warning("AI SSO classification failed, falling back to traditional matching")
            return self.find_best_sso_match(company, job_title, job_description)
            
        except Exception as e:
            logger.error(f"Error in AI SSO classification: {str(e)}")
            # Fallback to traditional matching
            return self.find_best_sso_match(company, job_title, job_description)
    
    def _get_sso_candidates(self, company: str, job_title: str, 
                          job_description: str) -> List[Tuple[str, str, float]]:
        """Get top SSO code candidates using traditional matching."""
        search_text = f"{company} {job_title} {job_description}".lower()
        candidates = []
        
        for _, row in self.ssoc_df.iterrows():
            sso_code = str(row['SSO_Code'])
            sso_title = str(row['SSO_Title'])
            
            # Enhanced scoring for candidates
            title_score = self.enhanced_text_matching(job_title.lower(), sso_title.lower())
            desc_score = self.enhanced_text_matching(job_description.lower(), sso_title.lower())
            
            job_keywords = self._extract_job_keywords(search_text)
            keyword_score = self._calculate_enhanced_keyword_score(job_keywords, sso_title.lower())
            
            exact_match_score = self._calculate_enhanced_job_match(job_title.lower(), sso_title.lower())
            
            # Weighted combination
            combined_score = (title_score * 0.35) + (desc_score * 0.15) + (keyword_score * 0.25) + (exact_match_score * 0.25)
            candidates.append((sso_code, sso_title, combined_score))
        
        # Sort by score and return top candidates
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates
    
    def classify_job(self, company: str, job_title: str, job_description: str, 
                    api_key: Optional[str] = None) -> Dict[str, any]:
        """
        Classify a job with both SSIC and SSO codes.
        First determines SSO (occupation), then uses it to ensure SSIC-SSO compatibility.
        SSIC is 5-digit and considers Company Analysis + SSO compatibility.
        
        Args:
            company: Company name
            job_title: Job title
            job_description: FULL job description (including generated content)
            api_key: OpenAI API key for company description generation (optional)
            
        Returns:
            Dictionary with classification results including company description
        """
        try:
            # Step 1: Generate company description using AI for SSIC classification
            company_description = ""
            if api_key:
                company_description = self.generate_company_description(
                    company, job_title, job_description, api_key
                )
            
            # Step 2: Determine SSO classification first (job role)
            if api_key:
                sso_code, sso_title, sso_score = self._ai_enhanced_sso_classification(
                    company, job_title, job_description, api_key
                )
            else:
                # Fall back to traditional SSO matching
                sso_code, sso_title, sso_score = self.find_best_sso_match(
                    company, job_title, job_description
                )
            
            # Step 3: SSIC classification based on company analysis + SSO compatibility
            # Ensure we get 5-digit SSIC codes
            if api_key and company_description:
                ssic_code, ssic_title, ssic_score = self._ai_enhanced_ssic_classification(
                    company, company_description, sso_code, sso_title, api_key
                )
            else:
                # Fall back to traditional matching - ensure 5-digit
                ssic_code, ssic_title, ssic_score = self._find_best_5digit_ssic_match(
                    company, company_description or f"Business operations related to {company}", sso_code
                )
            
            result = {
                'ssic': {
                    'code': ssic_code,
                    'title': ssic_title,
                    'confidence': round(ssic_score * 100, 1)
                },
                'sso': {
                    'code': sso_code,
                    'title': sso_title,
                    'confidence': round(sso_score * 100, 1)
                }
            }
            
            # Include company description if generated
            if company_description:
                result['company_description'] = company_description
            
            return result
            
        except Exception as e:
            logger.error(f"Error in classification: {str(e)}")
            return {
                'ssic': {'code': 'Unknown', 'title': 'Classification failed', 'confidence': 0},
                'sso': {'code': 'Unknown', 'title': 'Classification failed', 'confidence': 0}
            }
    
    def get_classification_summary(self, classification: Dict[str, any]) -> str:
        """Generate a summary text of the classification results with 5-digit SSIC emphasis."""
        ssic = classification['ssic']
        sso = classification['sso']
        
        # Ensure SSIC is 5-digit for display
        ssic_display = f"{ssic['code']} (5-digit)" if len(str(ssic['code'])) == 5 else f"{ssic['code']} (non-standard)"
        
        summary = f"""
**Industry Classification (SSIC 2025):**
- Code: {ssic_display}
- Industry: {ssic['title']}
- Confidence: {ssic['confidence']}%

**Occupation Classification (SSO 2024):**
- Code: {sso['code']} (5-digit)
- Occupation: {sso['title']}
- Confidence: {sso['confidence']}%"""
        
        # Include company description if available
        if 'company_description' in classification:
            summary = f"""**Company Analysis:**
{classification['company_description']}

{summary}

**Classification Method:**
- SSIC determined from Company Analysis + SSO compatibility
- SSO determined from Job Title + Job Description
- Both codes are 5-digit for maximum specificity"""
        
        return summary.strip()
    
    def enhance_classification_with_ai(self, company: str, job_title: str, 
                                     job_description: str, api_key: str) -> Dict[str, any]:
        """Use AI to enhance classification accuracy by understanding context better."""
        try:
            client = OpenAI(api_key=api_key)
            
            # Get initial classification
            base_classification = self.classify_job(company, job_title, job_description)
            
            # Create AI prompt for validation and enhancement
            prompt = f"""
Based on the following job information, help validate and potentially improve the SSIC and SSO classification:

Company: {company}
Job Title: {job_title}
Job Description: {job_description}

Current Classification:
SSIC: {base_classification['ssic']['code']} - {base_classification['ssic']['title']}
SSO: {base_classification['sso']['code']} - {base_classification['sso']['title']}

Please analyze if these classifications are appropriate. Consider:
1. What industry does this company likely operate in?
2. What are the main responsibilities and skills required for this job?
3. Are there any specific industry or occupation keywords that suggest different classifications?

Respond with just: GOOD if classifications are appropriate, or suggest better matches if needed.
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in Singapore's SSIC and SSO classifications. Analyze job information and validate classifications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_feedback = response.choices[0].message.content.strip()
            base_classification['ai_validation'] = ai_feedback
            
            return base_classification
            
        except Exception as e:
            logger.error(f"Error in AI enhancement: {str(e)}")
            return self.classify_job(company, job_title, job_description)


if __name__ == "__main__":
    # Test the classifier
    classifier = SingaporeClassifier()
    
    # Test case
    result = classifier.classify_job(
        company="Tech Solutions Pte Ltd",
        job_title="Senior Software Engineer",
        job_description="Develop and maintain web applications using Python and React. Lead technical discussions and mentor junior developers."
    )
    
    print("Classification Result:")
    print(classifier.get_classification_summary(result))
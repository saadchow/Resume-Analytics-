from typing import List, Tuple, Dict
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def compute_score(
    jd_keywords: List[str], 
    found_keywords: List[str], 
    missing_keywords: List[str],
    semantic_similarity: float, 
    jd_text: str, 
    resume_text: str
) -> Tuple[Dict, int]:
    """
    Compute comprehensive match score using multiple factors.
    
    Args:
        jd_keywords: All keywords extracted from job description
        found_keywords: Keywords found in resume
        missing_keywords: Keywords missing from resume
        semantic_similarity: Normalized semantic similarity score [0,1]
        jd_text: Full job description text
        resume_text: Full resume text
        
    Returns:
        Tuple of (score_components_dict, final_score_int)
    """
    try:
        # 1. Keyword Recall (40% weight)
        # What percentage of JD keywords are covered?
        if jd_keywords:
            recall = len(found_keywords) / len(jd_keywords)
        else:
            recall = 0.0
        
        # 2. Keyword Precision (15% weight) 
        # Prevents keyword stuffing - how specific are resume keywords to this JD?
        total_extracted_keywords = len(found_keywords) + len(missing_keywords)
        if total_extracted_keywords > 0:
            precision = len(found_keywords) / total_extracted_keywords
        else:
            precision = 0.0
        
        # 3. Semantic Alignment (35% weight)
        # Already normalized to [0,1] from nlp.py
        semantic_score = max(0.0, min(1.0, semantic_similarity))
        
        # 4. Context/Seniority Bonus (10% weight)
        context_bonus = _compute_context_bonus(jd_text, resume_text)
        
        # Combine all components with weights
        components = {
            "recall": round(recall, 3),
            "precision": round(precision, 3), 
            "semantic": round(semantic_score, 3),
            "context": round(context_bonus, 3)
        }
        
        # Final weighted score
        weighted_score = (
            0.40 * recall +
            0.15 * precision + 
            0.35 * semantic_score +
            0.10 * context_bonus
        )
        
        # Convert to 0-100 scale and round
        final_score = max(0, min(100, int(round(weighted_score * 100))))
        
        logger.info(f"Score breakdown - Recall: {recall:.3f}, Precision: {precision:.3f}, "
                   f"Semantic: {semantic_score:.3f}, Context: {context_bonus:.3f}, "
                   f"Final: {final_score}")
        
        return components, final_score
        
    except Exception as e:
        logger.error(f"Error computing score: {e}")
        # Return safe defaults
        return {
            "recall": 0.0,
            "precision": 0.0,
            "semantic": 0.0,
            "context": 0.0
        }, 0

def _compute_context_bonus(jd_text: str, resume_text: str) -> float:
    """
    Compute context bonus based on seniority level alignment and domain fit.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
        
    Returns:
        Context bonus/penalty between -0.1 and +0.1
    """
    try:
        jd_lower = jd_text.lower()
        resume_lower = resume_text.lower()
        
        # Seniority level indicators
        junior_indicators_jd = [
            'junior', 'entry', 'entry-level', 'graduate', 'new grad',
            '0-2 years', '0-3 years', 'early career', 'associate',
            'bootcamp', 'internship', 'trainee'
        ]
        
        senior_indicators_jd = [
            'senior', 'lead', 'principal', 'staff', 'architect', 
            'manager', 'director', '5+ years', '3+ years',
            'experienced', 'expert', 'advanced'
        ]
        
        junior_indicators_resume = [
            'intern', 'internship', 'graduate', 'bootcamp', 'entry',
            'junior', 'associate', 'trainee', 'apprentice',
            'recent graduate', 'new to', 'learning'
        ]
        
        senior_indicators_resume = [
            'lead', 'senior', 'principal', 'manager', 'director',
            'architect', 'staff', 'expert', 'experienced',
            'mentored', 'managed team', 'led team', 'supervised'
        ]
        
        # Check JD seniority expectations
        jd_is_junior = any(indicator in jd_lower for indicator in junior_indicators_jd)
        jd_is_senior = any(indicator in jd_lower for indicator in senior_indicators_jd)
        
        # Check resume seniority signals
        resume_is_junior = any(indicator in resume_lower for indicator in junior_indicators_resume)
        resume_is_senior = any(indicator in resume_lower for indicator in senior_indicators_resume)
        
        # Compute seniority alignment bonus/penalty
        seniority_bonus = 0.0
        
        if jd_is_junior and not jd_is_senior:
            # JD is for junior role
            if resume_is_junior and not resume_is_senior:
                seniority_bonus = 0.08  # Good match
            elif resume_is_senior:
                seniority_bonus = -0.05  # Overqualified might be issue
            else:
                seniority_bonus = 0.02  # Neutral
                
        elif jd_is_senior and not jd_is_junior:
            # JD is for senior role
            if resume_is_senior:
                seniority_bonus = 0.08  # Good match
            elif resume_is_junior:
                seniority_bonus = -0.08  # Underqualified
            else:
                seniority_bonus = 0.0  # Neutral
                
        else:
            # Ambiguous or mid-level role
            seniority_bonus = 0.02
        
        # Years of experience indicators
        years_bonus = _extract_years_bonus(jd_text, resume_text)
        
        # Industry/domain alignment bonus
        domain_bonus = _compute_domain_alignment(jd_text, resume_text)
        
        # Combine bonuses (cap at ±0.1)
        total_bonus = seniority_bonus + years_bonus + domain_bonus
        return max(-0.1, min(0.1, total_bonus))
        
    except Exception as e:
        logger.error(f"Error computing context bonus: {e}")
        return 0.0

def _extract_years_bonus(jd_text: str, resume_text: str) -> float:
    """Extract and compare years of experience."""
    try:
        # Extract years from JD
        jd_years_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+(?:in|with)',
            r'minimum\s+(\d+)\s+years?',
            r'at\s+least\s+(\d+)\s+years?'
        ]
        
        jd_years = []
        for pattern in jd_years_patterns:
            matches = re.findall(pattern, jd_text.lower())
            jd_years.extend([int(match) for match in matches])
        
        # Extract years from resume (look for experience spans)
        resume_years_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d{4})\s*-\s*(?:present|current|\d{4})',  # Date ranges
        ]
        
        resume_years = []
        for pattern in resume_years_patterns:
            matches = re.findall(pattern, resume_text.lower())
            if 'experience' in pattern:
                resume_years.extend([int(match) for match in matches])
        
        # Calculate experience from date ranges
        # scoring.py

        current_year = datetime.now().year

        date_ranges = re.findall(r'(\d{4})\s*-\s*(?:present|current|(\d{4}))', resume_text.lower())
        for start_year, end_year in date_ranges:
            start = int(start_year)
            end = int(end_year) if end_year else current_year
            if end > start and start > 1990:  # Sanity check
                resume_years.append(end - start)
        
        if not jd_years or not resume_years:
            return 0.0
        
        # Compare experience levels
        jd_max_years = max(jd_years)
        resume_max_years = max(resume_years)
        
        if resume_max_years >= jd_max_years:
            return 0.02  # Meets or exceeds requirement
        elif resume_max_years >= jd_max_years * 0.7:
            return 0.01  # Close enough
        else:
            return -0.02  # Significantly below requirement
            
    except Exception as e:
        logger.error(f"Error extracting years bonus: {e}")
        return 0.0

def _compute_domain_alignment(jd_text: str, resume_text: str) -> float:
    """Compute domain/industry alignment bonus."""
    try:
        # Domain keywords by industry
        domain_keywords = {
            'fintech': ['finance', 'banking', 'trading', 'payment', 'fintech', 'cryptocurrency', 'blockchain'],
            'healthcare': ['healthcare', 'medical', 'hospital', 'patient', 'clinical', 'pharma', 'biotech'],
            'ecommerce': ['ecommerce', 'e-commerce', 'retail', 'shopping', 'marketplace', 'commerce'],
            'saas': ['saas', 'b2b', 'enterprise', 'subscription', 'platform'],
            'gaming': ['gaming', 'game', 'unity', 'unreal', 'mobile games', 'console'],
            'security': ['security', 'cybersecurity', 'infosec', 'penetration', 'vulnerability', 'encryption'],
            'data': ['data science', 'analytics', 'big data', 'machine learning', 'ai', 'ml'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter', 'swift', 'kotlin']
        }
        
        jd_lower = jd_text.lower()
        resume_lower = resume_text.lower()
        
        # Find domains mentioned in JD
        jd_domains = []
        for domain, keywords in domain_keywords.items():
            if any(keyword in jd_lower for keyword in keywords):
                jd_domains.append(domain)
        
        # Find domains mentioned in resume
        resume_domains = []
        for domain, keywords in domain_keywords.items():
            if any(keyword in resume_lower for keyword in keywords):
                resume_domains.append(domain)
        
        # Calculate overlap
        if not jd_domains:
            return 0.0
        
        overlap = len(set(jd_domains) & set(resume_domains))
        if overlap > 0:
            return 0.02  # Domain alignment bonus
        else:
            return -0.01  # No domain alignment
            
    except Exception as e:
        logger.error(f"Error computing domain alignment: {e}")
        return 0.0

def get_score_explanation(components: Dict, score: int) -> str:
    """
    Generate human-readable explanation of the score.
    
    Args:
        components: Score components dict
        score: Final score
        
    Returns:
        Explanation string
    """
    explanations = []
    
    # Recall explanation
    recall = components.get('recall', 0)
    if recall >= 0.8:
        explanations.append("Excellent keyword coverage")
    elif recall >= 0.6:
        explanations.append("Good keyword coverage")
    elif recall >= 0.4:
        explanations.append("Moderate keyword coverage")
    else:
        explanations.append("Low keyword coverage")
    
    # Semantic explanation
    semantic = components.get('semantic', 0)
    if semantic >= 0.7:
        explanations.append("strong semantic alignment")
    elif semantic >= 0.5:
        explanations.append("moderate semantic alignment")
    else:
        explanations.append("weak semantic alignment")
    
    # Context explanation
    context = components.get('context', 0)
    if context > 0.05:
        explanations.append("good seniority/domain fit")
    elif context < -0.05:
        explanations.append("seniority/domain mismatch")
    
    return f"Score {score}%: " + ", ".join(explanations) + "."
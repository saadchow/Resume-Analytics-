import os
import logging
from typing import List, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client lazily
_client = None

def _get_client():
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set - AI suggestions will be limited")
            return None
        _client = OpenAI(api_key=api_key)
    return _client

# Model selection - can be overridden with environment variable
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")  # Use gpt-4 as fallback since gpt-5 may not be available

def _trim_text(text: str, max_chars: int = 4000) -> str:
    """Trim text to fit within token limits while preserving meaning."""
    if not text:
        return ""
    
    # Clean up whitespace
    text = " ".join(text.split())
    
    if len(text) <= max_chars:
        return text
    
    # Try to cut at sentence boundaries
    sentences = text.split('.')
    trimmed = ""
    for sentence in sentences:
        if len(trimmed) + len(sentence) + 1 <= max_chars:
            trimmed += sentence + "."
        else:
            break
    
    if len(trimmed) > max_chars * 0.8:  # If we got most of it
        return trimmed
    else:
        # Just cut at character limit
        return text[:max_chars] + "..."

def generate_suggestions(
    jd_text: str, 
    resume_text: str, 
    missing_keywords: List[str], 
    semantic_matches: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate AI-powered resume improvement suggestions.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text  
        missing_keywords: Keywords missing from resume
        semantic_matches: Top semantic matches between JD and resume
        
    Returns:
        List of specific, actionable suggestions
    """
    client = _get_client()
    
    # Fallback suggestions if API not available
    if not client:
        return _generate_fallback_suggestions(missing_keywords)
    
    try:
        # Prepare inputs with trimming
        jd_trimmed = _trim_text(jd_text, 3000)
        resume_trimmed = _trim_text(resume_text, 3000)
        
        # Format top semantic matches for context
        top_matches = semantic_matches[:5] if semantic_matches else []
        matches_text = "\n".join([
            f"• JD: '{match['jd'][:100]}...' ↔ Resume: '{match['resume'][:100]}...' (similarity: {match['similarity']})"
            for match in top_matches
        ])
        
        # Create structured prompt
        prompt = f"""You are an expert technical recruiter and career coach. Your goal is to provide 3-5 specific, actionable suggestions to improve this resume for the given job description.

FOCUS ON:
- Incorporating missing keywords naturally
- Strengthening weak semantic matches
- Adding quantified impact where possible
- Improving technical language alignment

MISSING KEYWORDS (prioritize these): {missing_keywords[:10]}

TOP SEMANTIC MATCHES (strengthen these connections):
{matches_text}

=== JOB DESCRIPTION ===
{jd_trimmed}

=== CURRENT RESUME ===  
{resume_trimmed}

Provide 3-5 specific, actionable suggestions. Each should:
1. Target a specific section/bullet point
2. Include exact phrasing recommendations when possible
3. Incorporate relevant missing keywords naturally
4. Add quantified impact where appropriate

Format as a simple bullet list. Avoid generic advice."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful career coach specializing in technical resumes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        # Extract suggestions from response
        content = response.choices[0].message.content
        if not content:
            logger.warning("Empty response from OpenAI")
            return _generate_fallback_suggestions(missing_keywords)
        
        # Parse suggestions from response
        suggestions = _parse_suggestions(content)
        
        if not suggestions:
            logger.warning("Could not parse suggestions from OpenAI response")
            return _generate_fallback_suggestions(missing_keywords)
        
        logger.info(f"Generated {len(suggestions)} AI suggestions")
        return suggestions[:5]  # Limit to 5 suggestions
        
    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
        return _generate_fallback_suggestions(missing_keywords)

def _parse_suggestions(content: str) -> List[str]:
    """Parse suggestions from AI response content."""
    suggestions = []
    
    # Split by lines and clean up
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and headers
        if not line or line.lower().startswith(('here', 'suggestion', 'improve')):
            continue
        
        # Remove bullet points and numbering
        line = line.lstrip('•-*1234567890. ')
        
        # Skip if too short or looks like metadata
        if len(line) < 20:
            continue
        
        # Clean up the suggestion
        if line.endswith(':'):
            line = line[:-1]
        
        suggestions.append(line)
    
    return suggestions

def _generate_fallback_suggestions(missing_keywords: List[str]) -> List[str]:
    """Generate basic suggestions when AI is not available."""
    suggestions = [
        "Set OPENAI_API_KEY environment variable to enable AI-powered suggestions."
    ]
    
    if missing_keywords:
        # Group keywords by type for better suggestions
        top_missing = missing_keywords[:8]
        
        if any(k in ['react', 'vue', 'angular', 'javascript', 'typescript'] for k in top_missing):
            suggestions.append("Add frontend framework experience to your technical skills and project descriptions.")
        
        if any(k in ['python', 'java', 'node.js', 'go'] for k in top_missing):
            suggestions.append("Highlight backend programming language experience in your work history.")
        
        if any(k in ['aws', 'docker', 'kubernetes', 'ci/cd'] for k in top_missing):
            suggestions.append("Include cloud and DevOps experience in your infrastructure work.")
        
        if any(k in ['testing', 'jest', 'pytest', 'tdd'] for k in top_missing):
            suggestions.append("Add testing methodology experience to demonstrate code quality focus.")
        
        # Generic suggestion for remaining keywords
        remaining = [k for k in top_missing if k not in str(suggestions)]
        if remaining:
            suggestions.append(f"Consider incorporating these technologies in relevant project descriptions: {', '.join(remaining[:5])}")
    
    suggestions.extend([
        "Quantify your impact with specific metrics (e.g., 'Improved performance by 30%').",
        "Use action verbs like 'Built', 'Implemented', 'Optimized', 'Led' to start bullet points.",
        "Align your technical language with the job description terminology."
    ])
    
    return suggestions[:5]

def test_ai_connection() -> bool:
    """Test if AI service is available and working."""
    client = _get_client()
    if not client:
        return False
    
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Say 'AI connection test successful'"}],
            max_tokens=10
        )
        return bool(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI connection test failed: {e}")
        return False
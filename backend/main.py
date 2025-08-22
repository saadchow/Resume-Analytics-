from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import os

# Import our custom modules
from parsers import parse_resume
from nlp import extract_keywords, semantic_compare
from scoring import compute_score
from ai_openai import generate_suggestions
from latex_insert import insert_suggestions_into_latex

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume-Analytica API",
    description="AI-powered resume analysis and optimization",
    version="1.0.0"
)

# CORS middleware - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeResponse(BaseModel):
    score: int
    components: dict
    keywords: dict
    semantic_matches: list
    suggestions: list
    latex_annotated: Optional[str] = None
    limits: dict

@app.get("/")
async def root():
    return {"message": "Resume-Analytica API", "status": "running", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    job_description: str = Form(...),
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    is_latex: Optional[bool] = Form(False),
):
    """
    Analyze a resume against a job description.
    
    Args:
        job_description: The job posting text (required)
        file: Resume file (PDF/DOCX/LaTeX) - optional if resume_text provided
        resume_text: Raw resume text - optional if file provided
        is_latex: Whether the content is LaTeX format
    
    Returns:
        Comprehensive analysis with score, keywords, suggestions, etc.
    """
    try:
        # Validation
        if not file and not resume_text:
            raise HTTPException(
                status_code=400, 
                detail="Provide either a resume file or resume_text"
            )
        
        if not job_description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty"
            )
        
        # Parse resume
        logger.info("Parsing resume...")
        raw_text, latex_raw = await parse_resume(file, resume_text)
        
        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume"
            )
        
        # Extract keywords from job description
        logger.info("Extracting keywords...")
        jd_keywords, critical_keywords = extract_keywords(job_description)
        
        # Find matching keywords in resume
        resume_lower = raw_text.lower()
        found_keywords = [k for k in jd_keywords if k.lower() in resume_lower]
        missing_keywords = [k for k in jd_keywords if k.lower() not in resume_lower]
        
        # Semantic analysis
        logger.info("Performing semantic analysis...")
        sem_result = semantic_compare(job_description, raw_text)
        
        # Compute final score
        logger.info("Computing match score...")
        components, final_score = compute_score(
            jd_keywords, found_keywords, missing_keywords, 
            sem_result["avg_similarity"], job_description, raw_text
        )
        
        # Generate AI suggestions
        logger.info("Generating AI suggestions...")
        suggestions = generate_suggestions(
            job_description, raw_text, missing_keywords, sem_result["matches"]
        )
        
        # Handle LaTeX annotation
        latex_annotated = None
        if is_latex or (file and file.filename and file.filename.lower().endswith(".tex")):
            if latex_raw:
                latex_annotated = insert_suggestions_into_latex(latex_raw, suggestions)
        
        # Build response
        response = AnalyzeResponse(
            score=final_score,
            components=components,
            keywords={
                "found": found_keywords,
                "missing": missing_keywords,
                "all_extracted_from_jd": jd_keywords,
                "critical_missing": [k for k in missing_keywords if k in critical_keywords],
            },
            semantic_matches=sem_result["matches"],
            suggestions=suggestions,
            latex_annotated=latex_annotated,
            limits={
                "file_bytes_max": 4_000_000,
                "tokens_trimmed": len(raw_text) > 10000 or len(job_description) > 5000
            }
        )
        
        logger.info(f"Analysis complete. Score: {final_score}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during analysis. Please try again."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
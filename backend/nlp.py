import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer
import numpy as np
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple, Set
import logging
import re
import os

logger = logging.getLogger(__name__)

# Curated technical skills vocabulary
TECHNICAL_SKILLS = [
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
    'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'bash', 'shell',
    
    # Frontend Frameworks/Libraries
    'react', 'vue', 'angular', 'next.js', 'nuxt.js', 'svelte', 'jquery', 'bootstrap',
    'tailwind', 'sass', 'less', 'webpack', 'vite', 'parcel',
    
    # Backend Frameworks
    'node.js', 'express', 'fastapi', 'django', 'flask', 'spring', 'spring boot',
    'rails', 'laravel', 'asp.net', '.net core', 'gin', 'fiber', 'nest.js',
    
    # Databases
    'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'elasticsearch',
    'sqlite', 'oracle', 'cassandra', 'dynamodb', 'neo4j', 'influxdb',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
    'terraform', 'ansible', 'jenkins', 'gitlab ci', 'github actions', 'ci/cd',
    'lambda', 's3', 'ec2', 'cloudfront', 'cloudflare', 'nginx', 'apache',
    
    # Data & ML
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
    'jupyter', 'matplotlib', 'seaborn', 'plotly', 'apache spark', 'hadoop',
    'airflow', 'kafka', 'rabbitmq', 'etl', 'data pipeline', 'machine learning',
    'deep learning', 'nlp', 'computer vision', 'rag', 'llm',
    
    # APIs & Protocols
    'rest', 'restful', 'graphql', 'grpc', 'soap', 'websocket', 'api',
    'json', 'xml', 'yaml', 'oauth', 'jwt', 'microservices',
    
    # Testing & Quality
    'jest', 'pytest', 'junit', 'selenium', 'cypress', 'playwright',
    'unit testing', 'integration testing', 'tdd', 'bdd', 'mocha', 'chai',
    
    # Tools & Platforms
    'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
    'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator', 'postman',
    'insomnia', 'swagger', 'openapi',
    
    # Methodologies
    'agile', 'scrum', 'kanban', 'lean', 'waterfall', 'devops', 'sre',
    'pair programming', 'code review', 'continuous deployment',
    
    # Vector & AI Databases
    'chromadb', 'pinecone', 'weaviate', 'qdrant', 'milvus', 'faiss',
    'vector database', 'embedding', 'similarity search',
]

# Initialize spaCy model and matcher
try:
    _nlp = spacy.load("en_core_web_sm")
    logger.info("Loaded spaCy model: en_core_web_sm")
except OSError:
    logger.error("spaCy model not found. Please install: python -m spacy download en_core_web_sm")
    _nlp = None

_matcher = None
if _nlp:
    _matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
    # Add patterns for technical skills
    patterns = [_nlp.make_doc(skill) for skill in TECHNICAL_SKILLS]
    _matcher.add("TECHNICAL_SKILLS", patterns)

# Initialize sentence transformer model
try:
    _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Loaded SentenceTransformer: all-MiniLM-L6-v2")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer: {e}")
    _embedding_model = None

# Embedding function for ChromaDB
class EmbeddingFunction:
    def __call__(self, texts: List[str]) -> List[List[float]]:
        if _embedding_model is None:
            logger.error("SentenceTransformer model not available")
            return [[0.0] * 384 for _ in texts]  # Return zero vectors
        
        try:
            embeddings = _embedding_model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[0.0] * 384 for _ in texts]

# Initialize ChromaDB client
_embed_fn = EmbeddingFunction()
try:
    _chroma_client = chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        )
    )
    logger.info("ChromaDB client initialized")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {e}")
    _chroma_client = None

def extract_keywords(text: str) -> Tuple[List[str], Set[str]]:
    """
    Extract technical keywords from text using spaCy and pattern matching.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (all_keywords, critical_keywords)
    """
    if not _nlp or not _matcher:
        logger.warning("spaCy not available, falling back to simple keyword matching")
        return _fallback_keyword_extraction(text)
    
    try:
        doc = _nlp(text)
        matches = _matcher(doc)
        
        # Extract matched keywords
        keywords = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            keyword = span.text.lower().strip()
            if keyword and len(keyword) > 1:
                keywords.add(keyword)
        
        # Find critical keywords (mentioned multiple times or in headings)
        critical_keywords = _find_critical_keywords(text, keywords)
        
        return sorted(list(keywords)), critical_keywords
        
    except Exception as e:
        logger.error(f"Error in keyword extraction: {e}")
        return _fallback_keyword_extraction(text)

def _fallback_keyword_extraction(text: str) -> Tuple[List[str], Set[str]]:
    """Fallback keyword extraction using simple string matching."""
    text_lower = text.lower()
    found_keywords = []
    
    for skill in TECHNICAL_SKILLS:
        if skill.lower() in text_lower:
            found_keywords.append(skill)
    
    # Simple critical keyword detection - mentioned more than once
    critical = set()
    for keyword in found_keywords:
        if text_lower.count(keyword.lower()) >= 2:
            critical.add(keyword)
    
    return sorted(found_keywords), critical

def _find_critical_keywords(text: str, keywords: Set[str]) -> Set[str]:
    """Identify critical keywords based on frequency and context."""
    critical = set()
    text_lower = text.lower()
    
    # Split into sections (rough approximation)
    sections = re.split(r'\n\s*\n|\n\s*[A-Z][A-Za-z\s]+:', text)
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Count occurrences
        count = text_lower.count(keyword_lower)
        
        # Check if in multiple sections
        sections_with_keyword = sum(1 for section in sections if keyword_lower in section.lower())
        
        # Mark as critical if:
        # 1. Mentioned multiple times, OR
        # 2. Appears in multiple sections, OR
        # 3. Appears near requirement indicators
        if (count >= 2 or 
            sections_with_keyword >= 2 or
            _is_near_requirement_indicator(text_lower, keyword_lower)):
            critical.add(keyword)
    
    return critical

def _is_near_requirement_indicator(text: str, keyword: str) -> bool:
    """Check if keyword appears near requirement indicators."""
    requirement_indicators = [
        'required', 'must have', 'essential', 'mandatory', 'need',
        'experience with', 'proficient', 'expert', 'skilled'
    ]
    
    # Simple proximity check
    keyword_pos = text.find(keyword)
    if keyword_pos == -1:
        return False
    
    # Check 100 characters before and after
    start = max(0, keyword_pos - 100)
    end = min(len(text), keyword_pos + len(keyword) + 100)
    context = text[start:end]
    
    return any(indicator in context for indicator in requirement_indicators)

def semantic_compare(jd_text: str, resume_text: str) -> Dict:
    """
    Compare job description and resume using semantic similarity.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
        
    Returns:
        Dict with avg_similarity and top matches
    """
    if not _chroma_client or not _embedding_model:
        logger.warning("ChromaDB or embeddings not available, returning zero similarity")
        return {"avg_similarity": 0.0, "matches": []}
    
    try:
        # Chunk texts for better granularity
        jd_chunks = _chunk_text(jd_text, max_chars=300)
        resume_chunks = _chunk_text(resume_text, max_chars=300)
        
        if not jd_chunks or not resume_chunks:
            return {"avg_similarity": 0.0, "matches": []}
        
        # Create temporary collection for this analysis
        collection_name = "temp_jd_analysis"
        try:
            _chroma_client.delete_collection(collection_name)
        except:
            pass
        
        collection = _chroma_client.create_collection(
            name=collection_name,
            embedding_function=_embed_fn
        )
        
        # Add JD chunks to collection
        collection.add(
            documents=jd_chunks,
            ids=[f"jd_{i}" for i in range(len(jd_chunks))]
        )
        
        # Query with resume chunks and collect matches
        matches = []
        similarities_per_jd = {}
        
        for resume_chunk in resume_chunks:
            try:
                results = collection.query(
                    query_texts=[resume_chunk],
                    n_results=min(3, len(jd_chunks))
                )
                
                if results['documents'] and results['documents'][0]:
                    docs = results['documents'][0]
                    distances = results.get('distances', [None])[0] or [None] * len(docs)
                    
                    for doc, distance in zip(docs, distances):
                        # Convert distance to similarity
                        if distance is not None:
                            similarity = max(0.0, 1.0 - distance)
                        else:
                            # Fallback: compute similarity directly
                            similarity = _compute_direct_similarity(resume_chunk, doc)
                        
                        matches.append({
                            "jd": doc,
                            "resume": resume_chunk,
                            "similarity": round(float(similarity), 3)
                        })
                        
                        # Track best similarity for each JD chunk
                        if doc not in similarities_per_jd:
                            similarities_per_jd[doc] = similarity
                        else:
                            similarities_per_jd[doc] = max(similarities_per_jd[doc], similarity)
            
            except Exception as e:
                logger.error(f"Error in semantic query: {e}")
                continue
        
        # Compute average similarity across JD chunks
        if similarities_per_jd:
            avg_similarity = sum(similarities_per_jd.values()) / len(similarities_per_jd)
        else:
            avg_similarity = 0.0
        
        # Normalize from [~0.5, 1.0] to [0, 1.0]
        normalized_similarity = max(0.0, min(1.0, (avg_similarity - 0.5) / 0.5))
        
        # Sort matches by similarity and return top matches
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Clean up temporary collection
        try:
            _chroma_client.delete_collection(collection_name)
        except:
            pass
        
        return {
            "avg_similarity": normalized_similarity,
            "matches": matches[:20]  # Return top 20 matches
        }
        
    except Exception as e:
        logger.error(f"Error in semantic comparison: {e}")
        return {"avg_similarity": 0.0, "matches": []}

def _chunk_text(text: str, max_chars: int = 300) -> List[str]:
    """Split text into semantic chunks."""
    if not text.strip():
        return []
    
    # First, try to split by sentences
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # If adding this sentence would exceed limit, save current chunk
        if len(current_chunk) + len(sentence) + 1 > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = (current_chunk + " " + sentence).strip()
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # If we have very long chunks, split them further
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chars * 1.5:  # Split very long chunks
            words = chunk.split()
            temp_chunk = ""
            for word in words:
                if len(temp_chunk) + len(word) + 1 > max_chars and temp_chunk:
                    final_chunks.append(temp_chunk.strip())
                    temp_chunk = word
                else:
                    temp_chunk = (temp_chunk + " " + word).strip()
            if temp_chunk:
                final_chunks.append(temp_chunk.strip())
        else:
            final_chunks.append(chunk)
    
    return final_chunks[:50]  # Limit to 50 chunks max

def _compute_direct_similarity(text1: str, text2: str) -> float:
    """Compute similarity directly using sentence transformers."""
    if not _embedding_model:
        return 0.0
    
    try:
        embeddings = _embedding_model.encode([text1, text2], normalize_embeddings=True)
        similarity = np.dot(embeddings[0], embeddings[1])
        return float(similarity)
    except Exception as e:
        logger.error(f"Error computing direct similarity: {e}")
        return 0.0
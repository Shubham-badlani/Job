import os
import json
import logging
import uuid
from datetime import datetime
from models.job_description import JobDescription
from models.resume import Resume
from models.candidate import Candidate
from models.matching import MatchResult

# Initialize logger
logger = logging.getLogger(__name__)

# In-memory storage for the MVP
STORAGE = {
    'job_descriptions': {},
    'resumes': {},
    'candidates': {},
    'matches': {}
}

def init_storage():
    """Initialize the storage system"""
    logger.info("Initializing in-memory storage")
    # This is where we would set up persistent storage if needed
    # For now, we're using in-memory storage

def generate_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())

def save_job_description(job_description):
    """
    Save a job description to storage
    
    Args:
        job_description: JobDescription object to save
        
    Returns:
        Saved JobDescription with ID
    """
    if not job_description.id:
        job_description.id = generate_id()
    
    job_description.created_at = datetime.now().isoformat()
    STORAGE['job_descriptions'][job_description.id] = job_description
    
    logger.info(f"Saved job description with ID: {job_description.id}")
    return job_description

def get_job_description(job_id):
    """
    Retrieve a job description by ID
    
    Args:
        job_id: ID of the job description to retrieve
        
    Returns:
        JobDescription object or None if not found
    """
    return STORAGE['job_descriptions'].get(job_id)

def get_all_job_descriptions():
    """
    Retrieve all job descriptions
    
    Returns:
        List of all JobDescription objects
    """
    return list(STORAGE['job_descriptions'].values())

def save_resume(resume):
    """
    Save a resume to storage
    
    Args:
        resume: Resume object to save
        
    Returns:
        Saved Resume with ID
    """
    if not resume.id:
        resume.id = generate_id()
    
    resume.created_at = datetime.now().isoformat()
    STORAGE['resumes'][resume.id] = resume
    
    logger.info(f"Saved resume with ID: {resume.id}")
    return resume

def get_resume(resume_id):
    """
    Retrieve a resume by ID
    
    Args:
        resume_id: ID of the resume to retrieve
        
    Returns:
        Resume object or None if not found
    """
    return STORAGE['resumes'].get(resume_id)

def save_candidate(candidate):
    """
    Save a candidate to storage
    
    Args:
        candidate: Candidate object to save
        
    Returns:
        Saved Candidate with ID
    """
    if not candidate.id:
        candidate.id = generate_id()
    
    candidate.created_at = datetime.now().isoformat()
    STORAGE['candidates'][candidate.id] = candidate
    
    logger.info(f"Saved candidate with ID: {candidate.id}")
    return candidate

def get_candidate(candidate_id):
    """
    Retrieve a candidate by ID
    
    Args:
        candidate_id: ID of the candidate to retrieve
        
    Returns:
        Candidate object or None if not found
    """
    return STORAGE['candidates'].get(candidate_id)

def get_candidates_by_job(job_id):
    """
    Get all candidates for a specific job
    
    Args:
        job_id: Job ID to filter by
        
    Returns:
        List of Candidate objects for the job
    """
    return [c for c in STORAGE['candidates'].values() if c.job_id == job_id]

def get_all_candidates():
    """
    Retrieve all candidates
    
    Returns:
        List of all Candidate objects
    """
    return list(STORAGE['candidates'].values())

def save_match_result(match_result):
    """
    Save a match result to storage
    
    Args:
        match_result: MatchResult object to save
        
    Returns:
        Saved MatchResult
    """
    key = f"{match_result.candidate_id}_{match_result.job_id}"
    STORAGE['matches'][key] = match_result
    
    logger.info(f"Saved match result for candidate {match_result.candidate_id} and job {match_result.job_id}")
    return match_result

def get_match_result(candidate_id, job_id):
    """
    Retrieve a match result by candidate ID and job ID
    
    Args:
        candidate_id: ID of the candidate
        job_id: ID of the job
        
    Returns:
        MatchResult object or None if not found
    """
    key = f"{candidate_id}_{job_id}"
    return STORAGE['matches'].get(key)

def get_all_match_results():
    """
    Retrieve all match results
    
    Returns:
        List of all MatchResult objects
    """
    return list(STORAGE['matches'].values())

def get_statistics():
    """
    Get recruitment statistics
    
    Returns:
        Dictionary with statistics
    """
    total_candidates = len(STORAGE['candidates'])
    shortlisted = sum(1 for c in STORAGE['candidates'].values() if c.is_shortlisted)
    job_positions = len(STORAGE['job_descriptions'])
    
    # Calculate average match score
    match_scores = [c.match_score for c in STORAGE['candidates'].values()]
    avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0
    
    # Count candidates by match score range
    high_matches = sum(1 for c in STORAGE['candidates'].values() if c.match_score >= 75)
    medium_matches = sum(1 for c in STORAGE['candidates'].values() if 50 <= c.match_score < 75)
    low_matches = sum(1 for c in STORAGE['candidates'].values() if c.match_score < 50)
    
    return {
        'total_candidates': total_candidates,
        'shortlisted': shortlisted,
        'job_positions': job_positions,
        'avg_match_score': round(avg_match_score, 1),
        'high_matches': high_matches,
        'medium_matches': medium_matches,
        'low_matches': low_matches
    }

def get_category_distribution():
    """
    Get distribution of candidates by match category
    
    Returns:
        Dictionary with counts for each category
    """
    candidates = STORAGE['candidates'].values()
    
    distribution = {
        'High Match (>=75%)': sum(1 for c in candidates if c.match_score >= 75),
        'Medium Match (50-74%)': sum(1 for c in candidates if 50 <= c.match_score < 75),
        'Low Match (<50%)': sum(1 for c in candidates if c.match_score < 50)
    }
    
    return distribution

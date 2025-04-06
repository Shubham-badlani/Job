import logging
from agents.jd_analyzer import JDAnalyzer
from agents.cv_analyzer import CVAnalyzer
from agents.matcher import Matcher
from agents.email_generator import EmailGenerator
from models.job_description import JobDescription
from models.resume import Resume
from models.candidate import Candidate
from utils.storage import (
    save_job_description, save_resume, save_candidate, 
    save_match_result, get_job_description, get_candidates_by_job
)

# Initialize logger
logger = logging.getLogger(__name__)

class RecruitmentService:
    """
    Service class that orchestrates the recruitment process using multiple agents.
    """
    def __init__(self):
        """Initialize the recruitment service with all necessary agents"""
        self.jd_analyzer = JDAnalyzer()
        self.cv_analyzer = CVAnalyzer()
        self.matcher = Matcher()
        self.email_generator = EmailGenerator()
        logger.info("Recruitment service initialized with all agents")
    
    def process_job_description(self, title, department, content):
        """
        Process a job description document
        
        Args:
            title: Job title
            department: Department name
            content: Job description content text
            
        Returns:
            Processed JobDescription object
        """
        logger.info(f"Processing job description: {title}")
        
        # Create job description model
        job_description = JobDescription(None, title, department, content)
        
        # Analyze job description using the JD analyzer agent
        job_description = self.jd_analyzer.analyze(job_description)
        
        # Save to storage
        job_description = save_job_description(job_description)
        
        logger.info(f"Job description processed and saved with ID: {job_description.id}")
        return job_description
    
    def process_resume(self, name, email, content, job_id):
        """
        Process a resume document and match against a job description
        
        Args:
            name: Candidate name
            email: Candidate email
            content: Resume content text
            job_id: ID of the job to match against
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing resume for {name} against job {job_id}")
        
        # Get the job description
        job_description = get_job_description(job_id)
        if not job_description:
            logger.error(f"Job description with ID {job_id} not found")
            return {"success": False, "error": "Job description not found"}
        
        # Create resume model
        resume = Resume(None, name, email, content)
        
        # Analyze resume using the CV analyzer agent
        resume = self.cv_analyzer.analyze(resume)
        
        # Save resume to storage
        resume = save_resume(resume)
        
        # Create candidate model
        candidate = Candidate(None, name, email, resume.id, job_id)
        
        # Extract relevant information from resume
        candidate.skills = resume.skills
        candidate.experience = ' '.join(resume.experience) if resume.experience else ""
        candidate.education = resume.education
        
        # Match resume against job description
        match_result = self.matcher.match(resume, job_description, candidate.id)
        
        # Save match result
        save_match_result(match_result)
        
        # Update candidate with match score and details
        candidate.match_score = match_result.overall_score
        candidate.match_details = match_result.to_dict()
        
        # Determine if candidate should be shortlisted
        candidate.is_shortlisted = candidate.match_score >= 70  # Threshold of 70%
        
        # Save candidate
        candidate = save_candidate(candidate)
        
        logger.info(f"Resume processed with match score: {candidate.match_score}%")
        
        return {
            "success": True,
            "candidate_id": candidate.id,
            "match_score": candidate.match_score,
            "shortlisted": candidate.is_shortlisted
        }
    
    def generate_interview_request(self, candidate_id, job_id):
        """
        Generate an interview request email template
        
        Args:
            candidate_id: ID of the candidate
            job_id: ID of the job
            
        Returns:
            Email template or None if candidate/job not found
        """
        from utils.storage import get_candidate, get_job_description
        
        candidate = get_candidate(candidate_id)
        job_description = get_job_description(job_id)
        
        if not candidate or not job_description:
            logger.error(f"Candidate or job description not found for email generation")
            return None
        
        return self.email_generator.generate_interview_request(candidate, job_description)
    
    def get_candidates_for_job(self, job_id, shortlisted_only=False):
        """
        Get all candidates for a specific job
        
        Args:
            job_id: Job ID to filter by
            shortlisted_only: If True, return only shortlisted candidates
            
        Returns:
            List of candidate dictionaries with additional match information
        """
        candidates = get_candidates_by_job(job_id)
        
        if shortlisted_only:
            candidates = [c for c in candidates if c.is_shortlisted]
        
        # Sort by match score (descending)
        candidates.sort(key=lambda c: c.match_score, reverse=True)
        
        return [c.to_dict() for c in candidates]
    
    def get_job_with_candidates(self, job_id):
        """
        Get a job description with all of its candidates
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job and candidate information
        """
        from utils.storage import get_job_description, get_candidates_by_job
        
        job = get_job_description(job_id)
        if not job:
            logger.error(f"Job description with ID {job_id} not found")
            return None
        
        candidates = get_candidates_by_job(job_id)
        candidates.sort(key=lambda c: c.match_score, reverse=True)
        
        job_dict = job.to_dict()
        job_dict['candidates'] = []
        
        for candidate in candidates:
            candidate_dict = candidate.to_dict()
            # Add match analysis in a more frontend-friendly format
            if 'match_details' in candidate_dict:
                match_details = candidate_dict['match_details']
                candidate_dict['match_analysis'] = {
                    'skills': match_details.get('skills', {}),
                    'experience': match_details.get('experience', {}),
                    'education': match_details.get('education', {})
                }
            job_dict['candidates'].append(candidate_dict)
        
        return job_dict

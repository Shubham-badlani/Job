import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from services.recruitment_service import RecruitmentService
from utils.text_extraction import extract_text_from_file
from utils.storage import (
    get_all_job_descriptions, get_statistics, 
    get_category_distribution, get_candidates_by_job
)

# Initialize logger
logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Initialize recruitment service
recruitment_service = RecruitmentService()

@api_bp.route('/job-description', methods=['POST'])
def upload_job_description():
    """API endpoint to upload and analyze a job description"""
    logger.debug("Job description upload endpoint called")
    
    try:
        # Get form data
        title = request.form.get('title')
        department = request.form.get('department')
        
        if not title or not department:
            return jsonify({"success": False, "error": "Title and department are required"}), 400
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Extract text from file
        content = extract_text_from_file(file)
        
        if not content:
            return jsonify({"success": False, "error": "Failed to extract text from file"}), 400
        
        # Process job description
        job_description = recruitment_service.process_job_description(title, department, content)
        
        # Return success response with analysis results
        return jsonify({
            "success": True,
            "job_id": job_description.id,
            "analysis": {
                "skills": job_description.skills,
                "experience": job_description.experience,
                "qualifications": job_description.qualifications,
                "responsibilities": job_description.responsibilities
            }
        })
    
    except Exception as e:
        logger.error(f"Error processing job description: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/resume', methods=['POST'])
def upload_resume():
    """API endpoint to upload and analyze a resume"""
    logger.debug("Resume upload endpoint called")
    
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        job_id = request.form.get('job_id')
        
        if not name or not email or not job_id:
            return jsonify({"success": False, "error": "Name, email, and job ID are required"}), 400
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Extract text from file
        content = extract_text_from_file(file)
        
        if not content:
            return jsonify({"success": False, "error": "Failed to extract text from file"}), 400
        
        # Process resume
        result = recruitment_service.process_resume(name, email, content, job_id)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Return success response
        response = {
            "success": True,
            "candidate_id": result['candidate_id'],
            "match_score": result['match_score'],
            "shortlisted": result['shortlisted'],
            "redirect": "/dashboard"  # Redirect to dashboard after processing
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/job-descriptions', methods=['GET'])
def get_job_descriptions():
    """API endpoint to get all job descriptions"""
    logger.debug("Get job descriptions endpoint called")
    
    job_descriptions = get_all_job_descriptions()
    
    # Convert to JSON-serializable format
    jobs_list = [
        {
            'id': job.id,
            'title': job.title,
            'department': job.department,
            'created_at': job.created_at
        }
        for job in job_descriptions
    ]
    
    return jsonify(jobs_list)

@api_bp.route('/candidates/scores', methods=['GET'])
def get_candidate_scores():
    """API endpoint to get candidate scores for charts"""
    logger.debug("Get candidate scores endpoint called")
    
    from utils.storage import get_all_candidates
    
    candidates = get_all_candidates()
    
    # Convert to JSON-serializable format
    candidates_list = [
        {
            'id': candidate.id,
            'name': candidate.name,
            'score': candidate.match_score,
            'job_id': candidate.job_id
        }
        for candidate in candidates
    ]
    
    return jsonify(candidates_list)

@api_bp.route('/candidates/category-distribution', methods=['GET'])
def get_candidates_distribution():
    """API endpoint to get category distribution for charts"""
    logger.debug("Get candidate distribution endpoint called")
    
    distribution = get_category_distribution()
    
    return jsonify(distribution)

@api_bp.route('/candidates/<candidate_id>/skills-match', methods=['GET'])
def get_skills_match(candidate_id):
    """API endpoint to get skills match data for a specific candidate"""
    logger.debug(f"Get skills match endpoint called for candidate: {candidate_id}")
    
    from utils.storage import get_candidate, get_job_description, get_resume
    
    # Get candidate
    candidate = get_candidate(candidate_id)
    
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404
    
    # Get job description and resume
    job = get_job_description(candidate.job_id)
    resume = get_resume(candidate.resume_id)
    
    if not job or not resume:
        return jsonify({"error": "Job or resume not found"}), 404
    
    # Create skills match data
    skills_match = []
    
    # Include both job skills and candidate skills for a complete radar chart
    all_skills = set(job.skills) | set(resume.skills)
    
    for skill in all_skills:
        # Calculate normalized levels (0.0-1.0)
        # For simplicity, if skill is present, level is 1.0, otherwise 0.0
        candidate_level = 1.0 if skill in resume.skills else 0.0
        required_level = 1.0 if skill in job.skills else 0.0
        
        skills_match.append({
            'skill': skill,
            'candidateLevel': candidate_level,
            'requiredLevel': required_level
        })
    
    return jsonify(skills_match)

@api_bp.route('/email/interview-request/<candidate_id>', methods=['GET'])
def get_interview_request(candidate_id):
    """API endpoint to generate interview request email"""
    logger.debug(f"Get interview request endpoint called for candidate: {candidate_id}")
    
    from utils.storage import get_candidate
    
    # Get candidate
    candidate = get_candidate(candidate_id)
    
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404
    
    # Generate email template
    email_template = recruitment_service.generate_interview_request(candidate_id, candidate.job_id)
    
    if not email_template:
        return jsonify({"error": "Failed to generate email template"}), 500
    
    return jsonify(email_template)

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.storage import get_all_job_descriptions, get_statistics
from services.recruitment_service import RecruitmentService

# Initialize logger
logger = logging.getLogger(__name__)

# Create Blueprint
main_bp = Blueprint('main', __name__)

# Initialize recruitment service
recruitment_service = RecruitmentService()

@main_bp.route('/')
def index():
    """Render the homepage"""
    logger.debug("Rendering index page")
    
    # Get all job descriptions for dropdown
    job_descriptions = get_all_job_descriptions()
    
    return render_template('index.html', job_descriptions=job_descriptions)

@main_bp.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    logger.debug("Rendering dashboard page")
    
    # Get statistics for dashboard
    stats = get_statistics()
    
    # Get all job descriptions with their candidates
    jobs = []
    for job in get_all_job_descriptions():
        job_data = recruitment_service.get_job_with_candidates(job.id)
        if job_data:
            jobs.append(job_data)
    
    return render_template('dashboard.html', stats=stats, jobs=jobs)

@main_bp.route('/job/<job_id>')
def job_details(job_id):
    """Render the job details page"""
    logger.debug(f"Rendering job details page for job ID: {job_id}")
    
    # Get job with candidates
    job_data = recruitment_service.get_job_with_candidates(job_id)
    
    if not job_data:
        flash("Job not found", "danger")
        return redirect(url_for('main.dashboard'))
    
    return render_template('job_details.html', job=job_data)

@main_bp.route('/candidate/<candidate_id>')
def candidate_details(candidate_id):
    """Render the candidate details page"""
    logger.debug(f"Rendering candidate details page for candidate ID: {candidate_id}")
    
    from utils.storage import get_candidate, get_job_description, get_resume
    
    # Get candidate
    candidate = get_candidate(candidate_id)
    
    if not candidate:
        flash("Candidate not found", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Get associated job and resume
    job = get_job_description(candidate.job_id)
    resume = get_resume(candidate.resume_id)
    
    # Generate interview request email template
    email_template = recruitment_service.generate_interview_request(candidate_id, candidate.job_id)
    
    return render_template(
        'candidate_details.html', 
        candidate=candidate, 
        job=job,
        resume=resume,
        email_template=email_template
    )

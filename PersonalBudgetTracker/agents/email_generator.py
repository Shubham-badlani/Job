import logging
from datetime import datetime, timedelta

# Initialize logger
logger = logging.getLogger(__name__)

class EmailGenerator:
    """
    Agent class for generating email templates for candidate communication.
    """
    def __init__(self):
        """Initialize the email generator agent"""
        pass
    
    def generate_interview_request(self, candidate, job_description):
        """
        Generate an interview request email template
        
        Args:
            candidate: Candidate object with details
            job_description: JobDescription object with job details
            
        Returns:
            Dictionary with email subject and body
        """
        logger.info(f"Generating interview request email for candidate {candidate.id}")
        
        # Create email subject
        subject = f"Interview Request: {job_description.title} Position"
        
        # Create email body
        body = self._create_interview_email_body(candidate, job_description)
        
        # Suggested interview slots
        slots = self._suggest_interview_slots()
        
        return {
            'to': candidate.email,
            'subject': subject,
            'body': body,
            'suggested_slots': slots
        }
    
    def generate_rejection_email(self, candidate, job_description):
        """
        Generate a rejection email template
        
        Args:
            candidate: Candidate object with details
            job_description: JobDescription object with job details
            
        Returns:
            Dictionary with email subject and body
        """
        logger.info(f"Generating rejection email for candidate {candidate.id}")
        
        # Create email subject
        subject = f"Regarding Your Application for {job_description.title} Position"
        
        # Create email body
        body = self._create_rejection_email_body(candidate, job_description)
        
        return {
            'to': candidate.email,
            'subject': subject,
            'body': body
        }
    
    def _create_interview_email_body(self, candidate, job_description):
        """Create the body text for an interview request email"""
        body = f"""Dear {candidate.name},

I hope this email finds you well. Thank you for applying for the {job_description.title} position at our company.

We were impressed with your application and would like to invite you for an interview to discuss your qualifications further.

Could you please provide your availability for the upcoming week? We're flexible and happy to accommodate your schedule.

Looking forward to speaking with you soon.

Best regards,
Recruitment Team"""
        
        return body
    
    def _create_rejection_email_body(self, candidate, job_description):
        """Create the body text for a rejection email"""
        body = f"""Dear {candidate.name},

Thank you for your interest in the {job_description.title} position and for taking the time to submit your application.

After careful consideration of your qualifications against the requirements for the role, we regret to inform you that we have decided to pursue other candidates whose experience more closely aligns with our current needs.

We appreciate your interest in our company and wish you the best in your job search and future professional endeavors.

Best regards,
Recruitment Team"""
        
        return body
    
    def _suggest_interview_slots(self):
        """Generate some suggested interview time slots"""
        # Start from next business day
        now = datetime.now()
        start_date = now + timedelta(days=1)
        
        # Skip to Monday if it's weekend
        if start_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            days_to_add = 7 - start_date.weekday()
            start_date = now + timedelta(days=days_to_add)
        
        slots = []
        
        # Generate slots for the next 5 business days
        current_date = start_date
        for _ in range(5):
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date = current_date + timedelta(days=2)
            
            # Morning slot
            morning = datetime(
                current_date.year, 
                current_date.month, 
                current_date.day, 
                10, 0
            )
            slots.append(morning)
            
            # Afternoon slot
            afternoon = datetime(
                current_date.year, 
                current_date.month, 
                current_date.day, 
                14, 0
            )
            slots.append(afternoon)
            
            current_date = current_date + timedelta(days=1)
        
        # Format slots for display
        formatted_slots = []
        for slot in slots:
            formatted_slots.append({
                'date': slot.strftime('%Y-%m-%d'),
                'time': slot.strftime('%H:%M'),
                'formatted': slot.strftime('%A, %B %d at %I:%M %p')
            })
        
        return formatted_slots

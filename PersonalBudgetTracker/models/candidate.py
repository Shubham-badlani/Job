class Candidate:
    """
    Model class representing a processed candidate with matching information.
    """
    def __init__(self, id, name, email, resume_id, job_id):
        self.id = id
        self.name = name
        self.email = email
        self.resume_id = resume_id
        self.job_id = job_id
        self.match_score = 0
        self.skills = []
        self.experience = ""
        self.education = []
        self.match_details = {}  # Detailed matching info
        self.is_shortlisted = False
        self.created_at = None
    
    def to_dict(self):
        """
        Convert the Candidate object to a dictionary for JSON serialization
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'match_score': self.match_score,
            'skills': self.skills,
            'experience': self.experience,
            'education': self.education,
            'match_details': self.match_details,
            'is_shortlisted': self.is_shortlisted,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Candidate instance from a dictionary
        """
        candidate = cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            resume_id=data.get('resume_id'),
            job_id=data.get('job_id')
        )
        candidate.match_score = data.get('match_score', 0)
        candidate.skills = data.get('skills', [])
        candidate.experience = data.get('experience', "")
        candidate.education = data.get('education', [])
        candidate.match_details = data.get('match_details', {})
        candidate.is_shortlisted = data.get('is_shortlisted', False)
        candidate.created_at = data.get('created_at')
        return candidate

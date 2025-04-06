class Resume:
    """
    Model class representing a resume/CV with extracted information.
    """
    def __init__(self, id, candidate_name, email, content=None):
        self.id = id
        self.candidate_name = candidate_name
        self.email = email
        self.content = content
        self.skills = []
        self.experience = []
        self.education = []
        self.certifications = []
        self.created_at = None
    
    def to_dict(self):
        """
        Convert the Resume object to a dictionary for JSON serialization
        """
        return {
            'id': self.id,
            'candidate_name': self.candidate_name,
            'email': self.email,
            'skills': self.skills,
            'experience': self.experience,
            'education': self.education,
            'certifications': self.certifications,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Resume instance from a dictionary
        """
        resume = cls(
            id=data.get('id'),
            candidate_name=data.get('candidate_name'),
            email=data.get('email'),
            content=data.get('content')
        )
        resume.skills = data.get('skills', [])
        resume.experience = data.get('experience', [])
        resume.education = data.get('education', [])
        resume.certifications = data.get('certifications', [])
        resume.created_at = data.get('created_at')
        return resume

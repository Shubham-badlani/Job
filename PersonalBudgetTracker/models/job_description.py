class JobDescription:
    """
    Model class representing a job description with extracted fields.
    """
    def __init__(self, id, title, department, content=None):
        self.id = id
        self.title = title
        self.department = department
        self.content = content
        self.skills = []
        self.experience = []
        self.qualifications = []
        self.responsibilities = []
        self.created_at = None
    
    def to_dict(self):
        """
        Convert the JobDescription object to a dictionary for JSON serialization
        """
        return {
            'id': self.id,
            'title': self.title,
            'department': self.department,
            'skills': self.skills,
            'experience': self.experience,
            'qualifications': self.qualifications,
            'responsibilities': self.responsibilities,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a JobDescription instance from a dictionary
        """
        job = cls(
            id=data.get('id'),
            title=data.get('title'),
            department=data.get('department'),
            content=data.get('content')
        )
        job.skills = data.get('skills', [])
        job.experience = data.get('experience', [])
        job.qualifications = data.get('qualifications', [])
        job.responsibilities = data.get('responsibilities', [])
        job.created_at = data.get('created_at')
        return job

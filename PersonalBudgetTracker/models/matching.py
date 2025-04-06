class MatchField:
    """
    Represents a matching field with required and found values.
    """
    def __init__(self, required=0, found=0):
        self.required = required
        self.found = found
        self.percentage = 0
        self.calculate_percentage()
    
    def calculate_percentage(self):
        """Calculate the percentage match based on required and found values"""
        if self.required == 0:
            self.percentage = 100
        else:
            self.percentage = min(round((self.found / self.required) * 100), 100)
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'required': self.required,
            'found': self.found,
            'percentage': self.percentage
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        match = cls(
            required=data.get('required', 0),
            found=data.get('found', 0)
        )
        match.percentage = data.get('percentage', 0)
        return match


class MatchResult:
    """
    Represents the result of matching a resume against a job description.
    """
    def __init__(self, candidate_id, job_id):
        self.candidate_id = candidate_id
        self.job_id = job_id
        self.overall_score = 0
        self.skills = MatchField()
        self.experience = MatchField()
        self.education = MatchField()
        self.weights = {
            'skills': 0.5,  # 50% weight to skills
            'experience': 0.3,  # 30% weight to experience
            'education': 0.2   # 20% weight to education
        }
    
    def calculate_overall_score(self):
        """Calculate the overall weighted score"""
        self.overall_score = (
            self.skills.percentage * self.weights['skills'] +
            self.experience.percentage * self.weights['experience'] +
            self.education.percentage * self.weights['education']
        )
        return round(self.overall_score)
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'overall_score': self.overall_score,
            'skills': self.skills.to_dict(),
            'experience': self.experience.to_dict(),
            'education': self.education.to_dict(),
            'weights': self.weights
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        result = cls(
            candidate_id=data.get('candidate_id'),
            job_id=data.get('job_id')
        )
        result.overall_score = data.get('overall_score', 0)
        
        if 'skills' in data:
            result.skills = MatchField.from_dict(data['skills'])
        
        if 'experience' in data:
            result.experience = MatchField.from_dict(data['experience'])
        
        if 'education' in data:
            result.education = MatchField.from_dict(data['education'])
        
        if 'weights' in data:
            result.weights = data['weights']
        
        return result

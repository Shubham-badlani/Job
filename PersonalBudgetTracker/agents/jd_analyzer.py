import re
import logging
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import spacy
from utils.nlp_utils import extract_skills, extract_qualifications

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Initialize logger
logger = logging.getLogger(__name__)

class JDAnalyzer:
    """
    Agent class for analyzing job descriptions and extracting structured information.
    """
    def __init__(self):
        """Initialize the JD analyzer agent"""
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Downloading spaCy en_core_web_sm model")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.stop_words = set(stopwords.words('english'))
    
    def analyze(self, job_description):
        """
        Analyze the job description text and extract structured information
        
        Args:
            job_description: JobDescription object with content to analyze
            
        Returns:
            Updated JobDescription object with extracted information
        """
        if not job_description.content:
            logger.error("No content to analyze in job description")
            return job_description
        
        content = job_description.content
        
        # Extract skills
        job_description.skills = self._extract_skills(content)
        
        # Extract experience requirements
        job_description.experience = self._extract_experience(content)
        
        # Extract qualifications
        job_description.qualifications = self._extract_qualifications(content)
        
        # Extract responsibilities
        job_description.responsibilities = self._extract_responsibilities(content)
        
        logger.info(f"JD analysis complete: {len(job_description.skills)} skills, "
                   f"{len(job_description.experience)} experience items, "
                   f"{len(job_description.qualifications)} qualifications, "
                   f"{len(job_description.responsibilities)} responsibilities")
        
        return job_description
    
    def _extract_skills(self, text):
        """Extract skills from job description text"""
        skills = extract_skills(text)
        
        # Extract technical skills using pattern matching
        technical_skills_pattern = r'(?:technical skills|technologies required|requirements include|proficiency in|experience with|knowledge of)\s*(?::|\-|–)?\s*([\w\s,\.\/\+\(\)\&\;\-]+)'
        tech_matches = re.finditer(technical_skills_pattern, text, re.IGNORECASE)
        
        for match in tech_matches:
            skill_text = match.group(1).strip()
            # Split by common delimiters and clean up
            skill_items = re.split(r'[,;]|\s+and\s+', skill_text)
            for item in skill_items:
                item = item.strip()
                if item and len(item) > 1:
                    skills.append(item)
        
        # Remove duplicates and standardize
        return list(set([skill.strip() for skill in skills if skill.strip()]))
    
    def _extract_experience(self, text):
        """Extract experience requirements from text"""
        experience = []
        
        # Look for sections about experience requirements
        exp_patterns = [
            r'(?:[\d\-\+]+)\s+years\s+(?:of)?\s+experience\s+(?:in|with)?\s+([\w\s\,\/\+\&]+)',
            r'Experience\s*(?::|\-|–)?\s*([\w\s,\.\/\+\(\)\&\;\-]+)',
            r'(?:minimum|at least)\s+(?:of)?\s*(\d+)\s*(?:\+)?\s*years?\s+(?:of)?\s+experience',
            r'(?:[\d\-\+]+)\s+to\s+(?:[\d\-\+]+)\s+years\s+(?:of)?\s+experience'
        ]
        
        for pattern in exp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                exp_text = match.group(0).strip()
                if exp_text and exp_text not in experience:
                    experience.append(exp_text)
        
        # If no structured experience found, look for sentences with experience keywords
        if not experience:
            sentences = sent_tokenize(text)
            for sentence in sentences:
                if re.search(r'\bexperience\b', sentence, re.IGNORECASE):
                    if len(sentence) < 200:  # Avoid overly long sentences
                        experience.append(sentence.strip())
        
        return experience
    
    def _extract_qualifications(self, text):
        """Extract qualifications from text"""
        qualifications = extract_qualifications(text)
        
        # Look for education/qualification sections
        qual_patterns = [
            r'(?:Education|Qualifications|Requirements)(?:\s+Required)?(?:\s+:|\:|\-|–)?\s*([\w\s,\.\/\+\(\)\&\;\-]+)',
            r'(?:Bachelor|Master|PhD|Graduate|Undergraduate|Degree)\s+(?:in|of)\s+([\w\s\,\/\+\&]+)',
            r'(?:Bachelor|Master|PhD)\'?s?(?:\s+degree)?(?:\s+in|\s+of)?\s+([\w\s\,\/\+\&]+)'
        ]
        
        for pattern in qual_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                qual_text = match.group(0).strip()
                if qual_text and qual_text not in qualifications:
                    qualifications.append(qual_text)
        
        # Find education-related sentences
        sentences = sent_tokenize(text)
        edu_keywords = ['degree', 'education', 'university', 'college', 'diploma', 'certification']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in edu_keywords):
                if len(sentence) < 200 and sentence not in qualifications:  # Avoid overly long sentences
                    qualifications.append(sentence.strip())
        
        return qualifications
    
    def _extract_responsibilities(self, text):
        """Extract job responsibilities from text"""
        responsibilities = []
        
        # Look for responsibilities sections
        doc = self.nlp(text)
        
        # Pattern matching for responsibilities
        resp_patterns = [
            r'(?:Responsibilities|Duties|Key\s+Responsibilities|Job\s+Description|Role|The\s+Role|What\s+You\'ll\s+Do)(?:\s*:|\-|–)?\s*([\w\s\,\.\/\+\(\)\&\;\-]+)'
        ]
        
        for pattern in resp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                resp_text = match.group(1).strip() if match.group(1) else match.group(0).strip()
                
                # Check if this is followed by a list of items
                lines = resp_text.split('\n')
                for line in lines:
                    line = line.strip()
                    # Look for bullet points or numbered items
                    if re.match(r'^(?:\-|\•|\*|\d+\.|\([a-z\d]\))\s+', line):
                        clean_line = re.sub(r'^(?:\-|\•|\*|\d+\.|\([a-z\d]\))\s+', '', line)
                        if clean_line and clean_line not in responsibilities:
                            responsibilities.append(clean_line)
        
        # If no clear responsibilities found, extract sentences with action verbs
        if not responsibilities:
            action_verbs = ['develop', 'manage', 'create', 'design', 'implement', 'coordinate', 
                            'lead', 'analyze', 'build', 'maintain', 'support', 'drive', 'execute']
            
            sentences = sent_tokenize(text)
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                if any(verb in words for verb in action_verbs):
                    if len(sentence) < 200:  # Avoid overly long sentences
                        responsibilities.append(sentence.strip())
        
        return responsibilities

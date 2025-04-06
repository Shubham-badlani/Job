import re
import logging
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import spacy
from utils.nlp_utils import extract_skills, extract_qualifications, clean_text

# Initialize logger
logger = logging.getLogger(__name__)

class CVAnalyzer:
    """
    Agent class for analyzing resumes/CVs and extracting structured information.
    """
    def __init__(self):
        """Initialize the CV analyzer agent"""
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Downloading spaCy en_core_web_sm model")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Download necessary NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def analyze(self, resume):
        """
        Analyze the resume text and extract structured information
        
        Args:
            resume: Resume object with content to analyze
            
        Returns:
            Updated Resume object with extracted information
        """
        if not resume.content:
            logger.error("No content to analyze in resume")
            return resume
        
        content = resume.content
        
        # Extract skills
        resume.skills = self._extract_skills(content)
        
        # Extract experience
        resume.experience = self._extract_experience(content)
        
        # Extract education
        resume.education = self._extract_education(content)
        
        # Extract certifications
        resume.certifications = self._extract_certifications(content)
        
        logger.info(f"CV analysis complete: {len(resume.skills)} skills, "
                   f"{len(resume.experience)} experience entries, "
                   f"{len(resume.education)} education entries, "
                   f"{len(resume.certifications)} certifications")
        
        return resume
    
    def _extract_skills(self, text):
        """Extract skills from resume text"""
        # Get general skills from utility function
        skills = extract_skills(text)
        
        # Look for skills sections
        skills_section = self._extract_section(text, ['skills', 'technical skills', 'core competencies'])
        
        if skills_section:
            # Extract skills from the dedicated section
            # Look for list items or comma-separated values
            skill_items = re.findall(r'(?:^|\n)(?:\-|\•|\*|\d+\.|\([a-z\d]\))\s*([\w\s\,\/\+\#\&]+)', skills_section)
            
            for item in skill_items:
                # For each list item, split by commas if present
                if ',' in item:
                    sub_items = [s.strip() for s in item.split(',')]
                    skills.extend(sub_items)
                else:
                    skills.append(item.strip())
            
            # If no list items found, try comma separation
            if not skill_items:
                comma_skills = re.split(r'\s*,\s*', skills_section)
                skills.extend([s.strip() for s in comma_skills if s.strip()])
        
        # Clean up skills
        clean_skills = []
        for skill in skills:
            # Remove any leading/trailing punctuation and whitespace
            skill = re.sub(r'^[\s\,\.\-\:]+|[\s\,\.\-\:]+$', '', skill)
            if skill and len(skill) > 1 and skill not in clean_skills:
                clean_skills.append(skill)
        
        return clean_skills
    
    def _extract_experience(self, text):
        """Extract work experience from resume text"""
        experience_entries = []
        
        # Look for experience section
        experience_section = self._extract_section(text, ['experience', 'work experience', 'professional experience', 'employment'])
        
        if not experience_section:
            # If no clear section found, return empty list
            return experience_entries
        
        # Use NER to identify organizations and dates
        doc = self.nlp(experience_section)
        
        # Look for job positions and companies
        job_pattern = r'(?:^|\n)(?:\-|\•|\*|\d+\.|\([a-z\d]\))?\s*([A-Z][A-Za-z\s\,\&\-\'\.]+)\s*(?:\-|–|at|\@)\s*([A-Z][A-Za-z\s\,\&\-\'\.]+)(?:\s*\((\d{4}(?:\s*\-\s*\d{4}|\s*\-\s*Present|present)?)\))?'
        
        job_matches = re.finditer(job_pattern, experience_section)
        
        for match in job_matches:
            title = match.group(1).strip() if match.group(1) else ""
            company = match.group(2).strip() if match.group(2) else ""
            dates = match.group(3).strip() if match.group(3) else ""
            
            if title and company:
                entry = f"{title} at {company}"
                if dates:
                    entry += f" ({dates})"
                experience_entries.append(entry)
        
        # If structured matching failed, return the entire section
        if not experience_entries:
            # Clean up the section and return it
            clean_exp = clean_text(experience_section)
            if len(clean_exp) > 500:  # If too long, try to truncate sensibly
                sentences = sent_tokenize(clean_exp)
                clean_exp = ' '.join(sentences[:10]) + '...'  # Take first 10 sentences
            
            experience_entries.append(clean_exp)
        
        return experience_entries
    
    def _extract_education(self, text):
        """Extract education information from resume text"""
        education_entries = []
        
        # Look for education section
        education_section = self._extract_section(text, ['education', 'academic background', 'academic qualification'])
        
        if not education_section:
            # If no clear section found, use qualification extraction
            qualifications = extract_qualifications(text)
            for qual in qualifications:
                education_entries.append({
                    'degree': qual,
                    'institution': '',
                    'year': ''
                })
            return education_entries
        
        # Use NER to identify organizations and dates
        doc = self.nlp(education_section)
        
        # Pattern for education entries
        edu_pattern = r'(?:^|\n)(?:\-|\•|\*|\d+\.|\([a-z\d]\))?\s*([A-Z][A-Za-z\s\,\&\-\'\.]+)(?:\s*\-\s*|\s*from\s*|\s*at\s*)([A-Z][A-Za-z\s\,\&\-\'\.]+)(?:\s*\((\d{4}(?:\s*\-\s*\d{4}|\s*\-\s*Present|present)?)\))?'
        
        edu_matches = re.finditer(edu_pattern, education_section)
        
        for match in edu_matches:
            degree = match.group(1).strip() if match.group(1) else ""
            institution = match.group(2).strip() if match.group(2) else ""
            year = match.group(3).strip() if match.group(3) else ""
            
            if degree and institution:
                education_entries.append({
                    'degree': degree,
                    'institution': institution,
                    'year': year
                })
        
        # Look for common degree patterns if structured matching failed
        if not education_entries:
            degree_patterns = [
                r'(Bachelor[\'s]* of [A-Za-z\s]+|B\.[A-Z][\.A-Za-z]*)',
                r'(Master[\'s]* of [A-Za-z\s]+|M\.[A-Z][\.A-Za-z]*)',
                r'(Doctor of [A-Za-z\s]+|Ph\.D\.)',
                r'([A-Z][A-Za-z\s\,\&\-\'\.]+(?:University|College|Institute|School))'
            ]
            
            for pattern in degree_patterns:
                matches = re.finditer(pattern, education_section)
                for match in matches:
                    edu_text = match.group(1).strip()
                    if edu_text:
                        # Try to find year near this degree
                        year_match = re.search(r'\b((?:19|20)\d{2})\b', education_section[match.start():match.start()+200])
                        year = year_match.group(1) if year_match else ""
                        
                        education_entries.append({
                            'degree': edu_text,
                            'institution': '',
                            'year': year
                        })
        
        return education_entries
    
    def _extract_certifications(self, text):
        """Extract certifications from resume text"""
        certifications = []
        
        # Look for certifications section
        cert_section = self._extract_section(text, ['certifications', 'certificates', 'professional qualifications'])
        
        if cert_section:
            # Look for list items
            cert_items = re.findall(r'(?:^|\n)(?:\-|\•|\*|\d+\.|\([a-z\d]\))\s*([\w\s\,\-\.\(\)\/\+]+)', cert_section)
            
            for item in cert_items:
                certifications.append(item.strip())
            
            # If no list items found, try to get sentences
            if not cert_items:
                sentences = sent_tokenize(cert_section)
                for sentence in sentences:
                    # Filter out very short or very long sentences
                    if 10 < len(sentence) < 200:
                        certifications.append(sentence.strip())
        
        # Look for certification keywords throughout the document if none found in dedicated section
        if not certifications:
            cert_keywords = ['certified', 'certification', 'certificate', 'licensed', 'license']
            sentences = sent_tokenize(text)
            
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in cert_keywords):
                    if len(sentence) < 200:  # Avoid overly long sentences
                        certifications.append(sentence.strip())
        
        return certifications
    
    def _extract_section(self, text, section_names):
        """
        Extract a specific section from the text based on section names
        
        Args:
            text: The full text content
            section_names: List of possible section names to look for
            
        Returns:
            The extracted section text or None if not found
        """
        for name in section_names:
            # Create pattern to match section header
            pattern = rf'(?i)(?:^|\n)[\s\*\-]*{re.escape(name)}[\s\*\-]*(?::|\.|\n)'
            
            match = re.search(pattern, text)
            if match:
                start_pos = match.end()
                
                # Look for the next section header
                next_section_pattern = r'(?i)(?:^|\n)[\s\*\-]*(?:education|experience|skills|certifications|projects|languages|interests|publications|references|summary|objective)[\s\*\-]*(?::|\.|\n)'
                next_match = re.search(next_section_pattern, text[start_pos:])
                
                if next_match:
                    end_pos = start_pos + next_match.start()
                    return text[start_pos:end_pos].strip()
                else:
                    # If no next section, take the rest of the text
                    return text[start_pos:].strip()
        
        return None

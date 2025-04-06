import logging
import re
from difflib import SequenceMatcher
import spacy
from models.matching import MatchResult, MatchField

# Initialize logger
logger = logging.getLogger(__name__)

class Matcher:
    """
    Agent class for matching resume information against job description requirements.
    """
    def __init__(self):
        """Initialize the matcher agent"""
        # Load spaCy model for text similarity
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Downloading spaCy en_core_web_sm model")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def match(self, resume, job_description, candidate_id):
        """
        Match resume against job description and calculate match score
        
        Args:
            resume: Resume object with extracted information
            job_description: JobDescription object with requirements
            candidate_id: ID of the candidate being matched
            
        Returns:
            MatchResult object with calculated scores
        """
        logger.info(f"Starting matching process for candidate {candidate_id} and job {job_description.id}")
        
        # Initialize match result
        match_result = MatchResult(candidate_id, job_description.id)
        
        # Match skills
        self._match_skills(resume, job_description, match_result)
        
        # Match experience
        self._match_experience(resume, job_description, match_result)
        
        # Match education/qualifications
        self._match_education(resume, job_description, match_result)
        
        # Calculate overall score
        match_result.calculate_overall_score()
        
        logger.info(f"Match completed. Overall score: {match_result.overall_score}%")
        
        return match_result
    
    def _match_skills(self, resume, job_description, match_result):
        """Match skills from resume against required skills in job description"""
        required_skills = job_description.skills
        candidate_skills = resume.skills
        
        if not required_skills:
            # If no skills specified in JD, assume perfect match
            match_result.skills = MatchField(0, 0)
            return
        
        match_result.skills.required = len(required_skills)
        matched_skills = 0
        
        # For each required skill, check if it exists in candidate skills
        for req_skill in required_skills:
            req_skill_doc = self.nlp(req_skill.lower())
            
            # Exact match
            if any(self._normalize_skill(req_skill) == self._normalize_skill(cand_skill) 
                   for cand_skill in candidate_skills):
                matched_skills += 1
                continue
            
            # Semantic similarity match
            best_match_score = 0
            for cand_skill in candidate_skills:
                cand_skill_doc = self.nlp(cand_skill.lower())
                
                # Calculate similarity if both documents have vectors
                if req_skill_doc.has_vector and cand_skill_doc.has_vector:
                    similarity = req_skill_doc.similarity(cand_skill_doc)
                    best_match_score = max(best_match_score, similarity)
                else:
                    # Fall back to string similarity for short texts
                    string_similarity = SequenceMatcher(None, req_skill.lower(), cand_skill.lower()).ratio()
                    best_match_score = max(best_match_score, string_similarity)
            
            # If similarity is above threshold, count as match
            if best_match_score > 0.8:
                matched_skills += 1
            elif best_match_score > 0.6:
                matched_skills += 0.5  # Partial match
        
        match_result.skills.found = matched_skills
        match_result.skills.calculate_percentage()
        
        logger.info(f"Skills match: {match_result.skills.percentage}% ({matched_skills}/{match_result.skills.required})")
    
    def _match_experience(self, resume, job_description, match_result):
        """Match experience from resume against required experience in job description"""
        required_experience = job_description.experience
        candidate_experience = ' '.join(resume.experience)
        
        if not required_experience:
            # If no experience specified in JD, assume perfect match
            match_result.experience = MatchField(0, 0)
            return
        
        match_result.experience.required = len(required_experience)
        matched_exp = 0
        
        # Extract years of experience requirements
        years_required = self._extract_years_requirement(required_experience)
        years_candidate = self._extract_years_candidate(candidate_experience)
        
        # If years are specified and can be extracted from both, compare directly
        if years_required > 0 and years_candidate > 0:
            if years_candidate >= years_required:
                matched_exp += 1
            elif years_candidate >= years_required * 0.7:  # 70% of required years
                matched_exp += 0.5  # Partial match
        
        # Look for domain/technology experience matches
        for req_exp in required_experience:
            req_exp_doc = self.nlp(req_exp.lower())
            
            # Calculate similarity with candidate's experience text
            cand_exp_doc = self.nlp(candidate_experience.lower())
            
            # If experience entry is short, look for it as a substring
            if len(req_exp.split()) < 6:
                domain_terms = self._extract_domain_terms(req_exp)
                if domain_terms:
                    # Check if domain terms are present in candidate experience
                    matches = sum(1 for term in domain_terms 
                                 if term.lower() in candidate_experience.lower())
                    if matches / len(domain_terms) > 0.7:
                        matched_exp += 1
                        continue
            
            # Otherwise use semantic similarity
            if req_exp_doc.has_vector and cand_exp_doc.has_vector:
                similarity = req_exp_doc.similarity(cand_exp_doc)
                if similarity > 0.6:
                    matched_exp += similarity / 0.6  # Scale match by similarity
            
        match_result.experience.found = min(matched_exp, match_result.experience.required)
        match_result.experience.calculate_percentage()
        
        logger.info(f"Experience match: {match_result.experience.percentage}%")
    
    def _match_education(self, resume, job_description, match_result):
        """Match education from resume against required qualifications in job description"""
        required_qualifications = job_description.qualifications
        
        if not required_qualifications:
            # If no qualifications specified in JD, assume perfect match
            match_result.education = MatchField(0, 0)
            return
        
        match_result.education.required = len(required_qualifications)
        matched_edu = 0
        
        # Extract degree levels from requirements
        required_degrees = self._extract_degree_levels(required_qualifications)
        
        # Extract candidate's highest degree
        candidate_degrees = []
        for edu in resume.education:
            degree = edu.get('degree', '')
            if degree:
                candidate_degrees.append(degree)
        
        highest_candidate_degree = self._determine_highest_degree(candidate_degrees)
        highest_required_degree = self._determine_highest_degree(required_degrees)
        
        # Compare degree levels
        if highest_candidate_degree and highest_required_degree:
            degree_levels = {
                'high school': 1,
                'associate': 2,
                'bachelor': 3,
                'master': 4,
                'doctorate': 5
            }
            
            candidate_level = degree_levels.get(highest_candidate_degree, 0)
            required_level = degree_levels.get(highest_required_degree, 0)
            
            if candidate_level >= required_level:
                matched_edu += 1
        
        # Look for field of study matches
        required_fields = self._extract_fields_of_study(required_qualifications)
        candidate_fields = []
        
        for edu in resume.education:
            degree = edu.get('degree', '')
            if degree:
                fields = self._extract_fields_of_study([degree])
                candidate_fields.extend(fields)
        
        if required_fields and candidate_fields:
            field_matches = 0
            for req_field in required_fields:
                req_field_doc = self.nlp(req_field.lower())
                
                # Check for exact matches
                if any(req_field.lower() == cand_field.lower() for cand_field in candidate_fields):
                    field_matches += 1
                    continue
                
                # Check for semantic similarity
                best_match = 0
                for cand_field in candidate_fields:
                    cand_field_doc = self.nlp(cand_field.lower())
                    
                    if req_field_doc.has_vector and cand_field_doc.has_vector:
                        similarity = req_field_doc.similarity(cand_field_doc)
                        best_match = max(best_match, similarity)
                
                if best_match > 0.7:
                    field_matches += best_match / 0.7
            
            if field_matches > 0:
                matched_edu += min(field_matches / len(required_fields), 1)
        
        match_result.education.found = min(matched_edu, match_result.education.required)
        match_result.education.calculate_percentage()
        
        logger.info(f"Education match: {match_result.education.percentage}%")
    
    def _normalize_skill(self, skill):
        """Normalize skill text for better matching"""
        # Convert to lowercase, remove punctuation
        normalized = re.sub(r'[^\w\s]', '', skill.lower())
        
        # Handle common abbreviations and variations
        replacements = {
            'javascript': 'js',
            'js': 'javascript',
            'react': 'reactjs',
            'reactjs': 'react',
            'node': 'nodejs',
            'nodejs': 'node',
            'py': 'python',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'ui': 'user interface',
            'ux': 'user experience'
        }
        
        for old, new in replacements.items():
            if old == normalized or old in normalized.split():
                return new
        
        return normalized
    
    def _extract_years_requirement(self, experience_list):
        """Extract the number of years required from experience requirements"""
        years = 0
        
        for exp in experience_list:
            # Look for patterns like "X years of experience" or "X+ years"
            year_match = re.search(r'(\d+)(?:\+)?\s*years?', exp, re.IGNORECASE)
            if year_match:
                years = max(years, int(year_match.group(1)))
                
            # Look for ranges like "X-Y years"
            range_match = re.search(r'(\d+)\s*-\s*(\d+)\s*years?', exp, re.IGNORECASE)
            if range_match:
                years = max(years, int(range_match.group(2)))  # Take the upper bound
        
        return years
    
    def _extract_years_candidate(self, experience_text):
        """Extract the number of years of experience from candidate's experience"""
        total_years = 0
        
        # Look for year ranges in formats like "2018-2022" or "2019-present"
        year_ranges = re.findall(r'((?:19|20)\d{2})\s*(?:-|to|–)\s*((?:19|20)\d{2}|present|current|now)', 
                                experience_text, re.IGNORECASE)
        
        import datetime
        current_year = datetime.datetime.now().year
        
        for start, end in year_ranges:
            start_year = int(start)
            if end.lower() in ['present', 'current', 'now']:
                end_year = current_year
            else:
                end_year = int(end)
            
            # Add to total if the range makes sense
            if start_year < end_year and start_year >= 1950 and end_year <= current_year:
                total_years += (end_year - start_year)
        
        # Also look for explicit mentions of years of experience
        exp_mentions = re.findall(r'(\d+)\+?\s*years?(?:\s+of)?\s+experience', 
                                 experience_text, re.IGNORECASE)
        
        if exp_mentions:
            mentioned_years = max(int(y) for y in exp_mentions)
            total_years = max(total_years, mentioned_years)
        
        return total_years
    
    def _extract_domain_terms(self, experience_text):
        """Extract domain-specific terms from experience requirement"""
        # Remove common words and keep domain-specific terms
        doc = self.nlp(experience_text)
        
        domain_terms = []
        for token in doc:
            # Keep nouns, proper nouns, and adjectives that aren't stop words
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and not token.is_stop and len(token.text) > 2):
                domain_terms.append(token.text)
        
        # Also extract technology or field names (often capitalized or with special formatting)
        tech_pattern = r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*|[A-Z]{2,}(?:\+\+)?|\w+\.\w+|\w+\#)\b'
        tech_terms = re.findall(tech_pattern, experience_text)
        
        domain_terms.extend(tech_terms)
        
        # Remove duplicates
        return list(set(domain_terms))
    
    def _extract_degree_levels(self, qualifications):
        """Extract degree levels from qualifications"""
        degrees = []
        
        for qual in qualifications:
            # Check for common degree mentions
            if re.search(r'\b(?:bachelor|BS|BA|B\.S\.|B\.A\.)\b', qual, re.IGNORECASE):
                degrees.append('bachelor')
            
            if re.search(r'\b(?:master|MS|MA|M\.S\.|M\.A\.|MBA|MSc)\b', qual, re.IGNORECASE):
                degrees.append('master')
            
            if re.search(r'\b(?:doctorate|phd|ph\.d\.|doctor)\b', qual, re.IGNORECASE):
                degrees.append('doctorate')
            
            if re.search(r'\b(?:associate|AA|A\.A\.|A\.S\.|AS)\b', qual, re.IGNORECASE):
                degrees.append('associate')
            
            if re.search(r'\b(?:high school|diploma|GED)\b', qual, re.IGNORECASE):
                degrees.append('high school')
        
        return degrees
    
    def _determine_highest_degree(self, degrees):
        """Determine the highest degree from a list of degrees"""
        degree_rank = {
            'doctorate': 5,
            'master': 4,
            'bachelor': 3,
            'associate': 2,
            'high school': 1
        }
        
        highest_rank = 0
        highest_degree = None
        
        for degree in degrees:
            rank = degree_rank.get(degree, 0)
            if rank > highest_rank:
                highest_rank = rank
                highest_degree = degree
        
        return highest_degree
    
    def _extract_fields_of_study(self, text_list):
        """Extract fields of study from text"""
        fields = []
        
        # Pattern for "X in Y" where Y is the field
        for text in text_list:
            # Look for "degree in field" pattern
            field_matches = re.findall(r'(?:degree|bachelor|master|phd|doctorate)\s+(?:of|in)\s+([A-Za-z\s\,\&]+)(?:or|and|,|\.|\)|\(|$)', 
                                      text, re.IGNORECASE)
            
            fields.extend([f.strip() for f in field_matches if f.strip()])
            
            # Also look for specific fields mentioned
            common_fields = [
                'computer science', 'engineering', 'information technology', 'business',
                'mathematics', 'physics', 'chemistry', 'biology', 'medicine', 'law',
                'finance', 'accounting', 'marketing', 'management', 'economics',
                'psychology', 'sociology', 'political science', 'arts', 'design',
                'communications', 'journalism', 'education', 'healthcare'
            ]
            
            for field in common_fields:
                if re.search(r'\b' + re.escape(field) + r'\b', text, re.IGNORECASE):
                    fields.append(field)
        
        return list(set(fields))

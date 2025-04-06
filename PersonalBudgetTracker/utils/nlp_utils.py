import re
import logging
import nltk
from nltk.corpus import stopwords
import string

# Initialize logger
logger = logging.getLogger(__name__)

# Try to download necessary NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load stop words
try:
    STOP_WORDS = set(stopwords.words('english'))
except:
    logger.warning("Failed to load NLTK stopwords, using a minimal set")
    STOP_WORDS = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
                 "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", 
                 "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", 
                 "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
                 "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", 
                 "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", 
                 "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", 
                 "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", 
                 "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", 
                 "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", 
                 "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", 
                 "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}

# Common technical skills
TECHNICAL_SKILLS = {
    "programming": [
        "python", "java", "javascript", "c++", "c#", "ruby", "go", "php", "swift", "kotlin",
        "typescript", "scala", "rust", "perl", "r", "matlab", "bash", "shell", "powershell",
        "dart", "assembly", "vba", "fortran", "sql", "pl/sql", "t-sql", "cobol"
    ],
    "frontend": [
        "html", "css", "sass", "less", "bootstrap", "tailwind", "material ui", "jquery",
        "react", "angular", "vue", "svelte", "redux", "next.js", "gatsby", "ember",
        "webpack", "babel", "electron", "pwa", "responsive design", "web components"
    ],
    "backend": [
        "node.js", "express", "django", "flask", "spring", "laravel", "ruby on rails", "asp.net",
        "fastapi", "phoenix", "nestjs", "nginx", "apache", "graphql", "rest", "soap", "grpc"
    ],
    "database": [
        "mysql", "postgresql", "mongodb", "oracle", "sqlite", "sql server", "redis", "cassandra",
        "elasticsearch", "couchdb", "neo4j", "dynamodb", "mariadb", "firebase", "supabase",
        "rdbms", "nosql", "db2", "snowflake", "data modeling", "etl", "data warehousing"
    ],
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "cloud computing", "lambda", "ec2", "s3", "rds",
        "kubernetes", "docker", "terraform", "serverless", "cloudformation", "heroku", "vercel",
        "netlify", "digital ocean", "iaas", "paas", "saas", "cloud native", "virtualization"
    ],
    "devops": [
        "ci/cd", "jenkins", "github actions", "gitlab ci", "circleci", "travis ci", "ansible", "puppet",
        "chef", "kubernetes", "docker", "docker-compose", "microservices", "monitoring", "logging",
        "elk stack", "prometheus", "grafana", "sre", "infrastructure as code", "configuration management"
    ],
    "ai/ml": [
        "machine learning", "deep learning", "nlp", "computer vision", "neural networks", "ai",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "scipy", "matplotlib",
        "data science", "regression", "classification", "clustering", "reinforcement learning",
        "transformers", "gpt", "bert", "llm", "generative ai", "computer vision", "image processing"
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "swift", "kotlin", "xamarin", "ionic",
        "objective-c", "mobile development", "pwa", "app development", "ui/ux", "ar", "vr"
    ],
    "tools": [
        "git", "svn", "mercurial", "jira", "confluence", "slack", "trello", "notion", "figma",
        "photoshop", "sketch", "illustrator", "adobe xd", "postman", "swagger", "visual studio",
        "vs code", "intellij", "eclipse", "jupyter", "colab", "tableau", "power bi"
    ],
    "methodologies": [
        "agile", "scrum", "kanban", "waterfall", "tdd", "bdd", "ddd", "devops", "ci/cd",
        "lean", "extreme programming", "pair programming", "mvp", "safe", "sprint", "standup"
    ]
}

# Flatten the technical skills list
ALL_TECHNICAL_SKILLS = []
for category in TECHNICAL_SKILLS.values():
    ALL_TECHNICAL_SKILLS.extend(category)

def clean_text(text):
    """
    Clean and normalize text content
    
    Args:
        text: The text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that don't add meaning
    text = re.sub(r'[\n\r\t]', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_skills(text):
    """
    Extract skills from text
    
    Args:
        text: The text to extract skills from
        
    Returns:
        List of extracted skills
    """
    skills = []
    text_lower = text.lower()
    
    # Check for technical skills
    for skill in ALL_TECHNICAL_SKILLS:
        # Match whole words only
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            skills.append(skill)
    
    # Look for skill-like patterns
    skill_patterns = [
        # Skills listed with bullet points
        r'(?:^|\n)(?:\-|\•|\*|\d+\.|\([a-z\d]\))\s*([\w\s\+\#\&]+)(?:$|\n)',
        # Skills with proficiency indicators
        r'([\w\s\+\#]+)\s*(?:\-|:)\s*(?:proficient|expert|advanced|intermediate|beginner)',
        # Capitalized multi-word skills
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b',
        # Technical abbreviations
        r'\b([A-Z]{2,}(?:\+\+)?)\b'
    ]
    
    for pattern in skill_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            skill = match.group(1).strip()
            if skill and len(skill) > 1:
                skills.append(skill)
    
    # Remove duplicates and normalize
    return list(set([skill.strip() for skill in skills if skill.strip()]))

def extract_qualifications(text):
    """
    Extract qualifications from text
    
    Args:
        text: The text to extract qualifications from
        
    Returns:
        List of extracted qualifications
    """
    qualifications = []
    
    # Look for common degree patterns
    degree_patterns = [
        r'(?:Bachelor|Master|PhD|Graduate|Undergraduate|Associate)(?:\'s)?\s+(?:degree|diploma)?\s+(?:of|in)\s+([\w\s]+)',
        r'(?:B\.S\.|M\.S\.|Ph\.D\.|B\.A\.|M\.A\.|M\.B\.A\.)\s+(?:in|of)?\s+([\w\s]+)?',
        r'(?:Bachelor|Master|Doctorate|PhD|Associate)\s+(?:of|in)\s+([\w\s]+)'
    ]
    
    for pattern in degree_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            qualification = match.group(0).strip()
            if qualification and qualification not in qualifications:
                qualifications.append(qualification)
    
    # Look for certification patterns
    cert_patterns = [
        r'(?:Certified|Licensed|Registered)\s+([\w\s]+)',
        r'([\w\s]+)\s+certification',
        r'([\w\s]+)\s+certificate'
    ]
    
    for pattern in cert_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            certification = match.group(0).strip()
            if certification and certification not in qualifications:
                qualifications.append(certification)
    
    return qualifications


import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')


import re
from docx import Document
import fitz  
import io
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
import spacy
import subprocess
import importlib.util

model_name = "en_core_web_sm"
if importlib.util.find_spec(model_name) is None:
    subprocess.run(["python", "-m", "spacy", "download", model_name])

nlp = spacy.load(model_name)



class ResumeParser:
    """
    A class to parse resume files (PDF and DOCX) and extract key information.
    This version is adapted for Google Colab with improved extraction logic
    and NLTK integration, excluding LinkedIn URL extraction.
    """
    def __init__(self, file_content, file_extension):
        """
        Initializes the parser with the content of the uploaded file.
        """
        self.file_content = file_content
        self.file_extension = file_extension
        self.text = self._read_file()
        self.doc = nlp(self.text) 
        self.data = {
            "name": None,
            "contact_number": None,
            "email": None,
            "education": [],
            "skills": []
        }

    def _read_file(self):
        """
        Reads a resume file from its byte content.
        Handles both PDF and DOCX formats.
        """
        if self.file_extension.lower() == ".pdf":
            with fitz.open(stream=self.file_content, filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            return text
        elif self.file_extension.lower() == ".docx":
            doc = Document(io.BytesIO(self.file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            raise ValueError("Unsupported file format. Please provide a .pdf or .docx file.")

    def parse(self):
        """
        Parses the resume text and extracts all the required information.
        """
        print("Parsing resume...")
        self._extract_name()
        self._extract_contact_info()
        self._extract_skills()
        self._extract_education()
        return self.data

    def _extract_name(self):
        """
        Extracts the name. Prioritizes text at the very top, then looks for PERSON entities
        using spaCy, and finally uses NLTK as a fallback.
        """
        
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        if lines:
            for i in range(min(5, len(lines))): # Check first 5 lines
                if len(lines[i].split()) >= 2 and len(lines[i].split()) <= 4 and (lines[i].isupper() or lines[i].istitle()):
                    if not any(keyword in lines[i].lower() for keyword in ["education", "skills", "projects", "experience", "contact", "profile", "summary"]):
                        self.data["name"] = lines[i]
                        return

      
        for ent in self.doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) > 1:
                
                if "coursework" not in ent.text.lower() and \
                   "technologies" not in ent.text.lower() and \
                   "projects" not in ent.text.lower() and \
                   "member" not in ent.text.lower():
                    self.data["name"] = ent.text
                    return

        
        sentences = sent_tokenize(self.text[:500]) 
        for sentence in sentences:
            words = word_tokenize(sentence)
            tagged_words = pos_tag(words)
            chunked_tree = ne_chunk(tagged_words)

            for subtree in chunked_tree.subtrees():
                if subtree.label() == 'PERSON':
                    name = " ".join([leaf[0] for leaf in subtree.leaves()])
                    if len(name.split()) > 1 and not any(keyword in name.lower() for keyword in ["coursework", "technologies", "projects", "member"]):
                        self.data["name"] = name
                        return


    def _extract_contact_info(self):
        email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_regex, self.text)
        if emails:
            self.data["email"] = emails[0]

        phone_regex = r"(?:\+\d{1,3}[\s\-]?)?\d{2,}[\s\-]?(?:\d{3}[\s\-]?)?\d{3}[\s\-]?\d{4,}\b"

        found_numbers = []
        matches = re.findall(phone_regex, self.text)

        for match_group in matches:
            num_str = "".join(match_group) if isinstance(match_group, tuple) else match_group

            cleaned_number = re.sub(r'[\s\-()]', '', num_str)

            if cleaned_number and 10 <= len(cleaned_number) <= 15:
                if not cleaned_number.startswith('+') and re.match(r'^\d{11,15}$', cleaned_number):
                    found_numbers.append("+" + cleaned_number)
                else:
                    found_numbers.append(cleaned_number)

        if found_numbers:
            self.data["contact_number"] = next((num for num in found_numbers if num.startswith('+')), found_numbers[0])



    def _extract_skills(self):
        """
        Extracts skills by matching a predefined list of keywords against the resume text.
        """
        SKILLS_LIST = [
            "python", "java", "c++", "c#", "javascript", "react", "angular", "node.js",
            "sql", "nosql", "mongodb", "mysql", "postgresql", "docker", "kubernetes",
            "aws", "azure", "gcp", "machine learning", "data science", "nlp", "tableau",
            "power bi", "excel", "git", "github", "jira", "agile", "scrum", "project management",
            "communication", "teamwork", "leadership", "problem-solving", "pandas", "numpy",
            "seaborn", "scikit-learn", "matplotlib", "keras", "opencv", "streamlit", "xgboost",
            "html", "css", "power query", "r", "sas", "spss", "hadoop", "spark", "kafka",
            "tensorflow", "pytorch", "azure devops", "jenkins", "ansible", "terraform",
            "data analysis", "business intelligence", "statistical analysis", "web development",
            "mobile development", "cloud computing", "cybersecurity", "network security",
            "database management", "system administration", "technical support", "customer service",
            "ux/ui design", "graphic design", "content writing", "marketing", "sales", "finance",
            "accounting", "human resources", "supply chain", "logistics", "operations", "research",
            "public speaking", "negotiation", "critical thinking", "adaptability", "creativity",
            "time management", "organization", "attention to detail", "decision making",
            "conflict resolution", "mentoring", "training", "documentation", "data structures",
            "algorithms", "object-oriented programming", "rest api", "microservices", "blockchain",
            "devops", "ci/cd", "big data", "data visualization", "predictive modeling", "deep learning",
            "computer vision", "natural language processing", "etl", "data warehousing", "cloud architecture",
            "security compliance", "penetration testing", "network administration", "system design",
            "technical writing", "customer relationship management", "salesforce", "sap", "erp",
            "budgeting", "financial analysis", "recruitment", "employee relations", "performance management",
            "supply chain optimization", "inventory management", "lean manufacturing", "quality assurance",
            "risk management", "strategic planning", "business development", "client management",
            "public relations", "social media marketing", "email marketing", "seo", "sem", "content strategy",
            "brand management", "market research", "statistical modeling", "econometrics", "quantitative analysis",
            "qualitative analysis", "report writing", "presentation skills", "cross-functional collaboration",
            "remote work", "virtual teams", "change management", "process improvement", "six sigma",
            "root cause analysis", "data mining", "feature engineering", "model deployment", "api integration",
            "unix", "linux", "windows server", "shell scripting", "bash", "powershell", "virtualization",
            "vmware", "hyper-v", "containerization", "message queues", "rabbitmq", "apache kafka",
            "tensorflow", "pytorch", "azure devops", "jenkins", "ansible", "terraform",
            "data analysis", "business intelligence", "statistical analysis", "web development",
            "mobile development", "cloud computing", "cybersecurity", "network security",
            "database management", "system administration", "technical support", "customer service",
            "ux/ui design", "graphic design", "content writing", "marketing", "sales", "finance",
            "accounting", "human resources", "supply chain", "logistics", "operations", "research",
            "public speaking", "negotiation", "critical thinking", "adaptability", "creativity",
            "time management", "organization", "attention to detail", "decision making",
            "conflict resolution", "mentoring", "training", "documentation", "data structures",
            "algorithms", "object-oriented programming", "rest api", "microservices", "blockchain",
            "devops", "ci/cd", "big data", "data visualization", "predictive modeling", "deep learning",
            "computer vision", "natural language processing", "etl", "data warehousing", "cloud architecture",
            "security compliance", "penetration testing", "network administration", "system design",
            "technical writing", "customer relationship management", "salesforce", "sap", "erp",
            "budgeting", "financial analysis", "recruitment", "employee relations", "performance management",
            "supply chain optimization", "inventory management", "lean manufacturing", "quality assurance",
            "risk management", "strategic planning", "business development", "client management",
            "public relations", "social media marketing", "email marketing", "seo", "sem", "content strategy",
            "brand management", "market research", "statistical modeling", "econometrics", "quantitative analysis",
            "qualitative analysis", "report writing",
        ]

        found_skills = set()
        text_lower = self.text.lower()
        for skill in SKILLS_LIST:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.add(skill.capitalize())

        self.data["skills"] = sorted(list(found_skills)) 

    def _extract_education(self):
        """
        Extracts education details by looking for a dedicated 'Education' section
        and then parsing lines within that section for degree.
        Focuses on extracting only the degree name as requested.
        """
        education_section_start = -1
        match = re.search(r"\n\s*Education\s*\n", self.text, re.IGNORECASE)
        if match:
            education_section_start = match.end()

        if education_section_start != -1:
            next_section_keywords = ["projects", "experience", "skills", "extracurricular", "certifications", "awards"]
            education_section_end = len(self.text)
            for keyword in next_section_keywords:
                section_match = re.search(r"\n\s*" + re.escape(keyword) + r"\s*\n", self.text, re.IGNORECASE)
                if section_match and section_match.start() > education_section_start:
                    education_section_end = section_match.start()
                    break

            education_text = self.text[education_section_start:education_section_end].strip()

            
            degree_regex = r"(Bachelor|Master|Ph\.D\.|B\.E\.|B\.Tech|M\.Tech|M\.S\.|Diploma)\s+(?:of\s+)?(.+?)(?=\n|\s*\(?\d{4}|\s*from\s+)"

            unique_degrees = set()
            for match in re.finditer(degree_regex, education_text, re.IGNORECASE):
                full_degree_match = match.group(0).strip()

                cleaned_degree = re.sub(r'\n.*$', '', full_degree_match).strip() 
                cleaned_degree = re.sub(r'\s*\(.*\)\s*$', '', cleaned_degree).strip() 
                cleaned_degree = re.sub(r'\s*,\s*$', '', cleaned_degree).strip() 
                cleaned_degree = re.sub(r'\s*from\s+.*$', '', cleaned_degree).strip() 

                unique_degrees.add(cleaned_degree)

            self.data["education"] = sorted(list(unique_degrees))

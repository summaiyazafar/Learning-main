"""
============================================================
AI RESUME TAILORING SYSTEM
============================================================

File:
    modules/jd_analyzer.py

Purpose:
    Analyze Job Descriptions (JD) and convert them into
    structured information for:

        Resume Parser
              ↓
        JD Analyzer
              ↓
        Skill Matching
              ↓
        Gap Analyzer
              ↓
        Resume Tailor
              ↓
        ATS / Match Score
              ↓
        Final Resume

IMPORTANT SAFETY RULE
---------------------

This module ONLY analyzes the Job Description.

It NEVER:

    - changes candidate personal information
    - adds skills to candidate resume
    - creates fake experience
    - creates fake projects
    - creates fake education
    - creates fake certifications

A skill found in a JD means:

    "Employer wants this skill."

It does NOT mean:

    "Candidate has this skill."

============================================================
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ============================================================
# OPTIONAL SENTENCE TRANSFORMER
# ============================================================

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True

except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False


# ============================================================
# JD ANALYZER
# ============================================================

class JDAnalyzer:
    """
    Professional Job Description Analyzer.

    Extracts:

        - Job title
        - Experience
        - Skills
        - Required skills
        - Preferred skills
        - Nice-to-have skills
        - Responsibilities
        - Qualifications
        - Keywords
        - Skill categories
        - Skill priorities
        - Semantic chunks
        - Optional Sentence Transformer embedding
    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        use_embeddings: bool = True
    ):
        self.embedding_model_name = embedding_model_name

        self.use_embeddings = (
            use_embeddings
            and SENTENCE_TRANSFORMERS_AVAILABLE
        )

        self._embedding_model = None

        self.skill_dictionary = (
            self._build_skill_dictionary()
        )

        self.skill_aliases = (
            self._build_skill_aliases()
        )

        self.stop_words = (
            self._build_stop_words()
        )

        self.section_headings = (
            self._build_section_headings()
        )

    # ========================================================
    # SKILL DATABASE
    # ========================================================

    def _build_skill_dictionary(
        self
    ) -> Dict[str, List[str]]:

        return {

            # ------------------------------------------------
            # PROGRAMMING
            # ------------------------------------------------

            "programming": [

                "python",
                "r",
                "java",
                "javascript",
                "typescript",

                "c",
                "c++",
                "c#",

                "go",
                "golang",

                "ruby",
                "php",
                "scala",
                "matlab",

                "kotlin",
                "swift",

                "rust",

                "node.js",
                "nodejs",

                "bash",
                "shell scripting",
                "powershell"
            ],

            # ------------------------------------------------
            # DATA ANALYSIS
            # ------------------------------------------------

            "data": [

                "sql",
                "mysql",
                "postgresql",
                "postgres",
                "sql server",
                "microsoft sql server",
                "oracle",
                "sqlite",

                "pandas",
                "numpy",
                "scipy",

                "excel",
                "microsoft excel",
                "power query",
                "power pivot",
                "vba",

                "matplotlib",
                "seaborn",
                "plotly",

                "statsmodels",
                "jupyter",
                "jupyter notebook",
                "anaconda",

                "data analysis",
                "data analytics",

                "data cleaning",
                "data preprocessing",
                "data transformation",

                "exploratory data analysis",
                "eda",

                "data visualization",
                "data visualisation",

                "statistics",
                "statistical analysis",

                "descriptive statistics",
                "inferential statistics",

                "hypothesis testing",
                "a/b testing",
                "ab testing",

                "regression analysis",
                "time series",
                "time series analysis",
                "forecasting",

                "kpi",
                "kpis",

                "reporting",
                "business reporting",

                "dashboard",
                "dashboards"
            ],

            # ------------------------------------------------
            # BUSINESS INTELLIGENCE
            # ------------------------------------------------

            "business_intelligence": [

                "power bi",
                "powerbi",
                "dax",

                "tableau",

                "looker",
                "looker studio",

                "qlik",
                "qlik sense",

                "microstrategy",

                "business intelligence",
                "bi",

                "data storytelling",

                "dashboard development",
                "dashboarding"
            ],

            # ------------------------------------------------
            # MACHINE LEARNING
            # ------------------------------------------------

            "machine_learning": [

                "artificial intelligence",
                "ai",

                "machine learning",
                "ml",

                "deep learning",
                "dl",

                "supervised learning",
                "unsupervised learning",

                "semi-supervised learning",
                "reinforcement learning",

                "scikit-learn",
                "scikit learn",
                "sklearn",

                "tensorflow",
                "keras",

                "pytorch",

                "xgboost",
                "lightgbm",
                "catboost",

                "machine learning algorithms",

                "predictive modeling",
                "predictive modelling",

                "feature engineering",
                "feature selection",

                "model training",
                "model evaluation",

                "model validation",

                "cross validation",
                "cross-validation",

                "hyperparameter tuning",
                "hyperparameter optimization",

                "classification",
                "regression",

                "linear regression",
                "logistic regression",

                "decision tree",
                "decision trees",

                "random forest",

                "support vector machine",
                "support vector machines",
                "svm",

                "knn",
                "k-nearest neighbors",

                "naive bayes",

                "clustering",

                "k-means",
                "kmeans",

                "hierarchical clustering",

                "pca",
                "principal component analysis",

                "dimensionality reduction",

                "ensemble learning",

                "anomaly detection",

                "recommender systems",
                "recommendation systems",

                "model deployment",

                "model monitoring"
            ],

            # ------------------------------------------------
            # NLP / GENAI / LLM
            # ------------------------------------------------

            "nlp_genai": [

                "nlp",
                "natural language processing",

                "text classification",
                "text mining",

                "sentiment analysis",

                "named entity recognition",
                "ner",

                "tokenization",
                "stemming",
                "lemmatization",

                "word embeddings",
                "embeddings",

                "transformers",

                "bert",

                "gpt",
                "gpt-4",
                "gpt-4o",

                "llm",
                "llms",

                "large language model",
                "large language models",

                "generative ai",
                "gen ai",
                "genai",

                "prompt engineering",

                "langchain",
                "langgraph",

                "llamaindex",
                "llama index",

                "rag",
                "retrieval augmented generation",
                "retrieval-augmented generation",

                "ai agent",
                "ai agents",

                "autonomous agents",

                "function calling",

                "fine tuning",
                "fine-tuning",

                "lora",
                "peft",

                "hugging face",
                "huggingface",

                "openai",

                "faiss",

                "pinecone",

                "chromadb",
                "chroma",

                "vector database",
                "vector databases",

                "vector search"
            ],

            # ------------------------------------------------
            # COMPUTER VISION
            # ------------------------------------------------

            "computer_vision": [

                "computer vision",

                "opencv",
                "opencv-python",

                "image processing",

                "image classification",

                "image recognition",

                "object detection",

                "object tracking",

                "image segmentation",

                "semantic segmentation",

                "instance segmentation",

                "yolo",
                "yolov5",
                "yolov8",
                "yolov9",

                "cnn",
                "convolutional neural network",

                "ocr",
                "optical character recognition",

                "image augmentation",

                "torchvision"
            ],

            # ------------------------------------------------
            # DATABASES
            # ------------------------------------------------

            "database": [

                "database",
                "databases",

                "database management",

                "mysql",
                "postgresql",
                "postgres",

                "sql server",
                "microsoft sql server",

                "oracle",

                "sqlite",

                "mongodb",
                "mongo db",

                "redis",

                "cassandra",

                "snowflake",

                "bigquery",
                "google bigquery",

                "redshift",

                "databricks",

                "database design",

                "database administration"
            ],

            # ------------------------------------------------
            # DATA ENGINEERING
            # ------------------------------------------------

            "data_engineering": [

                "data engineering",

                "data pipeline",
                "data pipelines",

                "etl",
                "elt",

                "data warehouse",
                "data warehousing",

                "data lake",
                "data lakehouse",

                "apache spark",
                "spark",

                "pyspark",

                "apache kafka",
                "kafka",

                "apache airflow",
                "airflow",

                "dbt",

                "hadoop",

                "hive",

                "presto",
                "trino",

                "delta lake",

                "databricks",

                "data orchestration",

                "workflow orchestration"
            ],

            # ------------------------------------------------
            # CLOUD
            # ------------------------------------------------

            "cloud": [

                "aws",
                "amazon web services",

                "azure",
                "microsoft azure",

                "google cloud",
                "gcp",
                "google cloud platform",

                "amazon s3",
                "s3",

                "ec2",

                "lambda",

                "azure blob storage",

                "azure machine learning",
                "azure ml",

                "sagemaker",
                "amazon sagemaker",

                "vertex ai",
                "google vertex ai",

                "cloud computing"
            ],

            # ------------------------------------------------
            # WEB / API
            # ------------------------------------------------

            "web_api": [

                "fastapi",
                "flask",

                "django",

                "streamlit",

                "rest api",
                "restful api",
                "restful services",

                "api",
                "apis",

                "graphql",

                "web development",

                "backend development",
                "frontend development",
                "full stack development",

                "html",
                "css",

                "react",
                "angular",
                "vue",

                "bootstrap"
            ],

            # ------------------------------------------------
            # DEVOPS / MLOPS
            # ------------------------------------------------

            "devops_mlops": [

                "git",
                "github",
                "gitlab",
                "bitbucket",

                "docker",
                "docker containers",

                "kubernetes",

                "ci/cd",
                "continuous integration",
                "continuous deployment",

                "mlops",

                "mlflow",

                "dvc",

                "airflow",

                "jenkins",

                "linux",

                "bash",

                "deployment",

                "model deployment",

                "monitoring"
            ],

            # ------------------------------------------------
            # SOFT SKILLS
            # ------------------------------------------------

            "soft_skills": [

                "communication",
                "verbal communication",
                "written communication",

                "teamwork",
                "team collaboration",
                "collaboration",

                "leadership",

                "problem solving",
                "problem-solving",

                "critical thinking",

                "analytical thinking",

                "attention to detail",

                "time management",

                "adaptability",

                "presentation skills",

                "interpersonal skills",

                "stakeholder management",

                "project management",

                "decision making",
                "decision-making",

                "research",

                "documentation"
            ],

            # ------------------------------------------------
            # PROJECT MANAGEMENT
            # ------------------------------------------------

            "project_management": [

                "agile",
                "scrum",
                "kanban",

                "jira",

                "project management",

                "product management",

                "stakeholder management",

                "requirements gathering",

                "business requirements",

                "technical documentation"
            ],

            # ------------------------------------------------
            # OFFICE / PRODUCTIVITY
            # ------------------------------------------------

            "office": [

                "microsoft office",
                "ms office",

                "excel",

                "word",
                "microsoft word",

                "powerpoint",
                "microsoft powerpoint",

                "outlook",

                "google sheets",
                "google docs",
                "google slides"
            ],

            # ------------------------------------------------
            # CYBERSECURITY
            # ------------------------------------------------

            "cybersecurity": [

                "cybersecurity",
                "cyber security",

                "information security",

                "network security",

                "application security",

                "penetration testing",

                "ethical hacking",

                "vulnerability assessment",

                "siem",

                "soc",

                "firewalls",

                "encryption",

                "authentication",

                "authorization"
            ],

            # ------------------------------------------------
            # FINANCE / ACCOUNTING
            # ------------------------------------------------

            "finance": [

                "financial analysis",

                "financial modeling",
                "financial modelling",

                "accounting",

                "bookkeeping",

                "budgeting",

                "forecasting",

                "financial reporting",

                "accounts payable",
                "accounts receivable",

                "quickbooks",

                "sap",

                "erp"
            ],

            # ------------------------------------------------
            # MARKETING
            # ------------------------------------------------

            "marketing": [

                "digital marketing",

                "seo",
                "search engine optimization",

                "sem",
                "search engine marketing",

                "social media marketing",

                "content marketing",

                "email marketing",

                "google analytics",

                "google ads",

                "facebook ads",

                "keyword research",

                "market research"
            ]
        }

    # ========================================================
    # SKILL ALIASES
    # ========================================================

    def _build_skill_aliases(
        self
    ) -> Dict[str, str]:

        return {

            "py": "python",

            "js": "javascript",
            "ts": "typescript",

            "nodejs": "node.js",
            "node js": "node.js",

            "golang": "go",

            "postgres": "postgresql",

            "powerbi": "power bi",
            "power-bi": "power bi",

            "scikit learn": "scikit-learn",
            "sklearn": "scikit-learn",

            "tf": "tensorflow",

            "torch": "pytorch",

            "opencv-python": "opencv",

            "cv": "computer vision",

            "ml": "machine learning",

            "ai": "artificial intelligence",

            "dl": "deep learning",

            "gen ai": "generative ai",
            "genai": "generative ai",

            "llms": "llm",

            "large language model":
                "large language models",

            "huggingface":
                "hugging face",

            "llamaindex":
                "llama index",

            "retrieval-augmented generation":
                "retrieval augmented generation",

            "ai agent":
                "ai agents",

            "restful api":
                "rest api",

            "gcp":
                "google cloud",

            "aws cloud":
                "aws",

            "microsoft azure":
                "azure",

            "ms office":
                "microsoft office",

            "seo":
                "search engine optimization",

            "ab testing":
                "a/b testing"
        }

    # ========================================================
    # STOP WORDS
    # ========================================================

    def _build_stop_words(self) -> set:

        return {

            "the",
            "and",
            "for",
            "with",
            "from",
            "that",
            "this",
            "these",
            "those",

            "are",
            "you",
            "your",
            "our",

            "will",
            "have",
            "has",
            "had",

            "can",
            "could",
            "should",
            "would",

            "who",
            "their",
            "they",
            "them",

            "into",
            "than",
            "then",

            "when",
            "where",
            "what",
            "which",
            "while",

            "about",
            "over",
            "under",
            "between",
            "through",
            "during",
            "within",

            "role",
            "position",

            "company",
            "organization",
            "organisation",

            "employee",
            "employees",

            "candidate",
            "candidates",

            "required",
            "requirements",
            "requirement",

            "experience",
            "experiences",

            "years",
            "year",

            "job",
            "jobs",

            "team",
            "teams",

            "work",
            "working",

            "ability",
            "abilities",

            "skills",
            "skill",

            "responsibilities",
            "responsibility",

            "qualification",
            "qualifications",

            "preferred",

            "strong",
            "good",
            "excellent",

            "including",

            "etc",

            "using",
            "used",
            "use",

            "based",

            "provide",
            "support",
            "supporting",

            "looking",
            "seeking"
        }

    # ========================================================
    # SECTION HEADINGS
    # ========================================================

    def _build_section_headings(
        self
    ) -> Dict[str, List[str]]:

        return {

            "responsibilities": [

                "responsibilities",
                "key responsibilities",
                "job responsibilities",
                "job duties",
                "duties",

                "what you will do",
                "what you'll do",

                "role responsibilities",
                "your responsibilities"
            ],

            "requirements": [

                "requirements",
                "required skills",
                "required qualifications",

                "basic qualifications",
                "minimum qualifications",

                "must have",
                "must-have",

                "essential skills",
                "essential requirements"
            ],

            "preferred": [

                "preferred qualifications",
                "preferred skills",

                "preferred",

                "nice to have",
                "nice-to-have",

                "desired skills",
                "desired qualifications",

                "bonus skills",
                "bonus"
            ],

            "qualifications": [

                "qualifications",
                "education",

                "educational requirements",
                "academic qualifications",

                "education requirements"
            ],

            "benefits": [

                "benefits",
                "what we offer",
                "perks"
            ]
        }

    # ========================================================
    # CLEAN TEXT
    # ========================================================

    def clean_text(
        self,
        text: Any
    ) -> str:

        if text is None:
            return ""

        text = str(text)

        text = text.replace(
            "\r\n",
            "\n"
        )

        text = text.replace(
            "\r",
            "\n"
        )

        # Remove HTML
        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        # Normalize bullets
        text = re.sub(
            r"[•●▪◦■►➤]",
            "\n",
            text
        )

        # Normalize tabs
        text = text.replace(
            "\t",
            " "
        )

        # Normalize spaces
        text = re.sub(
            r"[ ]{2,}",
            " ",
            text
        )

        # Normalize blank lines
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    # ========================================================
    # NORMALIZE SKILL
    # ========================================================

    def normalize_skill(
        self,
        skill: Any
    ) -> str:

        if skill is None:
            return ""

        skill = str(skill).strip().lower()

        skill = skill.replace(
            "&",
            "and"
        )

        skill = re.sub(
            r"[\u2010\u2011\u2012\u2013\u2014]",
            "-",
            skill
        )

        skill = re.sub(
            r"\s+",
            " ",
            skill
        )

        skill = skill.strip(
            " .,;:|()[]{}"
        )

        if skill in self.skill_aliases:
            skill = self.skill_aliases[
                skill
            ]

        return skill

    # ========================================================
    # DEDUPLICATE
    # ========================================================

    def deduplicate(
        self,
        items: List[Any]
    ) -> List[str]:

        result = []
        seen = set()

        for item in items:

            if item is None:
                continue

            item = str(item).strip()

            if not item:
                continue

            normalized = (
                self.normalize_skill(item)
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)

            result.append(
                normalized
            )

        return result

    # ========================================================
    # NORMALIZE LIST
    # ========================================================

    def normalize_list(
        self,
        value: Any
    ) -> List[str]:

        if value is None:
            return []

        if isinstance(value, list):

            result = []

            for item in value:

                if item is None:
                    continue

                if isinstance(item, dict):

                    for key in (
                        "text",
                        "description",
                        "value",
                        "name"
                    ):

                        if item.get(key):

                            result.append(
                                str(
                                    item[key]
                                ).strip()
                            )

                            break

                else:

                    item = str(
                        item
                    ).strip()

                    if item:
                        result.append(item)

            return self.deduplicate(
                result
            )

        if isinstance(
            value,
            tuple
        ):

            return self.normalize_list(
                list(value)
            )

        if isinstance(
            value,
            set
        ):

            return self.normalize_list(
                list(value)
            )

        if isinstance(
            value,
            dict
        ):

            result = []

            for key, values in value.items():

                if isinstance(
                    values,
                    list
                ):

                    for item in values:

                        if item:
                            result.append(
                                str(item)
                            )

                elif values:

                    result.append(
                        str(values)
                    )

            return self.deduplicate(
                result
            )

        text = str(
            value
        ).strip()

        if not text:
            return []

        parts = re.split(
            r"[,|;\n]+",
            text
        )

        return self.deduplicate(
            parts
        )

    # ========================================================
    # REGEX SKILL PATTERN
    # ========================================================

    def _skill_pattern(
        self,
        skill: str
    ) -> str:

        normalized = self.normalize_skill(
            skill
        )

        if not normalized:
            return ""

        pattern = re.escape(
            normalized
        )

        # Allow spaces and hyphens
        pattern = pattern.replace(
            r"\ ",
            r"[\s\-]+"
        )

        return (
            rf"(?<!\w){pattern}(?!\w)"
        )

    # ========================================================
    # EXTRACT JOB TITLE
    # ========================================================

    def extract_job_title(
        self,
        text: str
    ) -> str:

        if not text:
            return "Target Position"

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        # Explicit title
        patterns = [

            r"(?:job\s*title|position|role)"
            r"\s*[:\-]\s*(.+)",

            r"title\s*[:\-]\s*(.+)",

            r"hiring\s+for\s*[:\-]?\s*(.+)"
        ]

        for line in lines[:20]:

            for pattern in patterns:

                match = re.search(
                    pattern,
                    line,
                    flags=re.IGNORECASE
                )

                if match:

                    title = match.group(
                        1
                    ).strip()

                    title = re.sub(
                        r"\s+",
                        " ",
                        title
                    )

                    if (
                        2
                        <= len(title.split())
                        <= 12
                    ):

                        return title

        # Common job titles
        title_keywords = [

            "machine learning engineer",
            "artificial intelligence engineer",
            "ai engineer",

            "data scientist",
            "data analyst",
            "data engineer",

            "business analyst",
            "business intelligence analyst",

            "power bi developer",

            "ml engineer",
            "nlp engineer",

            "computer vision engineer",

            "software engineer",

            "software developer",

            "python developer",

            "full stack developer",
            "backend developer",
            "frontend developer",
            "web developer",

            "devops engineer",
            "cloud engineer",

            "database administrator",
            "sql developer",

            "project manager",
            "product manager",

            "financial analyst",

            "marketing analyst",

            "cybersecurity analyst"
        ]

        lower_text = text.lower()

        for title in title_keywords:

            if title in lower_text:

                return title.title()

        # First meaningful line
        bad_words = {

            "job",
            "description",
            "requirements",
            "responsibilities",
            "qualifications",
            "about",
            "company",
            "overview",
            "we are",
            "looking"
        }

        for line in lines[:10]:

            clean_line = re.sub(
                r"[^A-Za-z0-9+#&/.\- ]",
                " ",
                line
            )

            clean_line = re.sub(
                r"\s+",
                " ",
                clean_line
            ).strip()

            words = clean_line.split()

            if (
                2 <= len(words) <= 8
                and len(clean_line) <= 100
            ):

                lower_line = (
                    clean_line.lower()
                )

                if not any(
                    bad in lower_line
                    for bad in bad_words
                ):

                    return clean_line

        return "Target Position"

    # ========================================================
    # EXPERIENCE YEARS
    # ========================================================

    def extract_experience_years(
        self,
        text: str
    ) -> float:

        if not text:
            return 0.0

        patterns = [

            r"(\d+(?:\.\d+)?)\s*\+?\s*"
            r"years?\s+of\s+experience",

            r"(\d+(?:\.\d+)?)\s*\+?\s*"
            r"years?\s+experience",

            r"minimum\s+of\s+"
            r"(\d+(?:\.\d+)?)\s*years?",

            r"at\s+least\s+"
            r"(\d+(?:\.\d+)?)\s*years?",

            r"(\d+(?:\.\d+)?)\s*\+\s*years?",

            r"(\d+(?:\.\d+)?)\s*-\s*"
            r"(\d+(?:\.\d+)?)\s*years?"
        ]

        values = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                try:

                    if isinstance(
                        match,
                        tuple
                    ):

                        numbers = [
                            float(x)
                            for x in match
                            if x
                        ]

                        if numbers:
                            values.append(
                                min(numbers)
                            )

                    else:

                        values.append(
                            float(match)
                        )

                except (
                    ValueError,
                    TypeError
                ):
                    continue

        if not values:
            return 0.0

        # Avoid unrealistic values
        values = [
            value
            for value in values
            if 0 <= value <= 50
        ]

        if not values:
            return 0.0

        return min(values)

    # ========================================================
    # EXTRACT SKILLS
    # ========================================================

    def extract_skills(
        self,
        text: str
    ) -> List[str]:

        if not text:
            return []

        lower_text = text.lower()

        found = []

        for category, skills in (
            self.skill_dictionary.items()
        ):

            for skill in skills:

                normalized = (
                    self.normalize_skill(
                        skill
                    )
                )

                if not normalized:
                    continue

                pattern = (
                    self._skill_pattern(
                        normalized
                    )
                )

                if not pattern:
                    continue

                try:

                    if re.search(
                        pattern,
                        lower_text,
                        flags=re.IGNORECASE
                    ):

                        found.append(
                            normalized
                        )

                except re.error:

                    continue

        return self.deduplicate(
            found
        )

    # ========================================================
    # EXPLICIT SKILLS
    # ========================================================

    def extract_explicit_skills(
        self,
        text: str
    ) -> List[str]:

        if not text:
            return []

        lines = text.split("\n")

        collected = []

        in_skill_section = False

        headings = {

            "skills",
            "technical skills",
            "technical skill",

            "required skills",
            "preferred skills",

            "technologies",
            "technology",

            "tools",

            "technical requirements",

            "core skills",
            "key skills",

            "technical stack",
            "tech stack"
        }

        stop_headings = {

            "responsibilities",
            "requirements",
            "qualifications",
            "education",
            "experience",
            "benefits",
            "about us",
            "about the company"
        }

        for line in lines:

            clean_line = line.strip()

            if not clean_line:
                continue

            heading = re.sub(
                r"[:\-]+$",
                "",
                clean_line.lower()
            ).strip()

            if heading in headings:

                in_skill_section = True
                continue

            if (
                in_skill_section
                and heading in stop_headings
            ):

                in_skill_section = False
                continue

            if in_skill_section:

                found = self.extract_skills(
                    clean_line
                )

                collected.extend(
                    found
                )

        return self.deduplicate(
            collected
        )

    # ========================================================
    # RESPONSIBILITIES
    # ========================================================

    def extract_responsibilities(
        self,
        text: str
    ) -> List[str]:

        if not text:
            return []

        lines = text.split("\n")

        responsibilities = []

        in_section = False

        responsibility_headings = {
            heading.lower()
            for heading in (
                self.section_headings[
                    "responsibilities"
                ]
            )
        }

        all_headings = set()

        for values in (
            self.section_headings.values()
        ):

            for heading in values:
                all_headings.add(
                    heading.lower()
                )

        for line in lines:

            original = line.strip()

            if not original:
                continue

            normalized_heading = re.sub(
                r"[:\-]+$",
                "",
                original.lower()
            ).strip()

            # Start
            if (
                normalized_heading
                in responsibility_headings
            ):

                in_section = True
                continue

            # Stop
            if (
                in_section
                and normalized_heading
                in all_headings
                and normalized_heading
                not in responsibility_headings
            ):

                in_section = False
                continue

            cleaned = re.sub(
                r"^[\-\*\u2022\u25CF\u25AA\d]+"
                r"[\.\)\-:]?\s*",
                "",
                original
            ).strip()

            if in_section:

                if len(cleaned) >= 8:

                    responsibilities.append(
                        cleaned
                    )

        # Fallback
        if not responsibilities:

            sentences = re.split(
                r"\n+|(?<=[.!?])\s+",
                text
            )

            action_words = {

                "develop",
                "design",
                "build",
                "create",
                "analyze",
                "analyse",

                "manage",
                "maintain",

                "implement",
                "support",

                "lead",

                "developing",
                "building",
                "creating",

                "analyzing",
                "analysing",

                "managing",
                "maintaining",

                "implementing",
                "supporting",

                "collaborate",
                "collaborating",

                "monitor",
                "monitoring",

                "deploy",
                "deploying",

                "test",
                "testing",

                "evaluate",
                "evaluating",

                "report",
                "reporting",

                "prepare",
                "preparing",

                "extract",
                "extracting",

                "transform",
                "transforming"
            }

            for sentence in sentences:

                sentence = sentence.strip()

                if len(sentence) < 12:
                    continue

                first_word = (
                    sentence
                    .split()[0]
                    .lower()
                    .strip(".,:;-")
                )

                if first_word in action_words:

                    responsibilities.append(
                        sentence
                    )

        return self.deduplicate_text(
            responsibilities
        )

    # ========================================================
    # TEXT DEDUPLICATION
    # ========================================================

    def deduplicate_text(
        self,
        items: List[Any]
    ) -> List[str]:

        result = []
        seen = set()

        for item in items:

            if item is None:
                continue

            value = str(
                item
            ).strip()

            if not value:
                continue

            key = re.sub(
                r"\s+",
                " ",
                value.lower()
            )

            if key in seen:
                continue

            seen.add(key)

            result.append(
                value
            )

        return result

    # ========================================================
    # QUALIFICATIONS
    # ========================================================

    def extract_qualifications(
        self,
        text: str
    ) -> List[str]:

        if not text:
            return []

        qualifications = []

        patterns = [

            r"\b(?:bachelor|bachelors|"
            r"b\.?s\.?|bs)\b[^.\n]{0,150}",

            r"\b(?:master|masters|"
            r"m\.?s\.?|ms)\b[^.\n]{0,150}",

            r"\b(?:phd|ph\.d)\b[^.\n]{0,150}",

            r"\b(?:degree|graduation)\b"
            r"[^.\n]{0,150}",

            r"\b(?:computer science|"
            r"information technology|"
            r"data science|"
            r"software engineering|"
            r"statistics|"
            r"mathematics)\b"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                if isinstance(
                    match,
                    tuple
                ):

                    value = (
                        match[0]
                        if match
                        else ""
                    )

                else:

                    value = match

                value = str(
                    value
                ).strip()

                if value:
                    qualifications.append(
                        value
                    )

        return self.deduplicate_text(
            qualifications
        )

    # ========================================================
    # KEYWORDS
    # ========================================================

    def extract_keywords(
        self,
        text: str,
        skills: Optional[List[str]] = None
    ) -> List[str]:

        if not text:
            return []

        keywords = []

        # Add known skills
        if skills:
            keywords.extend(
                skills
            )

        important_terms = {

            "analysis",
            "analytics",

            "reporting",

            "dashboard",
            "dashboards",

            "automation",

            "data",

            "integration",

            "visualization",
            "visualisation",

            "forecasting",

            "modeling",
            "modelling",

            "deployment",
            "development",

            "testing",

            "optimization",
            "optimisation",

            "monitoring",

            "performance",

            "documentation",

            "pipeline",
            "pipelines",

            "database",
            "databases",

            "cloud",

            "api",
            "apis",

            "etl",
            "elt",

            "business intelligence",

            "machine learning",
            "deep learning",

            "artificial intelligence",

            "natural language processing",

            "generative ai",

            "problem solving",

            "communication",

            "collaboration",

            "leadership",

            "research",

            "automation",

            "decision making",

            "stakeholder management"
        }

        lower_text = text.lower()

        for term in important_terms:

            if term in lower_text:

                keywords.append(
                    term
                )

        # Meaningful repeated words
        words = re.findall(
            r"\b[A-Za-z][A-Za-z0-9+#./-]{2,}\b",
            text
        )

        frequency = {}

        for word in words:

            normalized = (
                self.normalize_skill(
                    word
                )
            )

            if not normalized:
                continue

            if normalized in self.stop_words:
                continue

            if len(normalized) < 3:
                continue

            frequency[
                normalized
            ] = (
                frequency.get(
                    normalized,
                    0
                ) + 1
            )

        repeated_terms = [

            word
            for word, count
            in frequency.items()
            if count >= 2
        ]

        keywords.extend(
            repeated_terms
        )

        return self.deduplicate(
            keywords
        )

    # ========================================================
    # REQUIRED SKILLS
    # ========================================================

    def extract_required_skills(
        self,
        text: str,
        all_skills: List[str]
    ) -> List[str]:

        if not text or not all_skills:
            return []

        required = []

        lower_text = text.lower()

        strong_terms = [

            "required",
            "must have",
            "must-have",

            "mandatory",
            "essential",

            "minimum qualification",
            "minimum qualifications",

            "required skills",
            "requirements",

            "you must",
            "must be"
        ]

        # ----------------------------------------------------
        # Requirement section
        # ----------------------------------------------------

        requirement_text = ""

        lines = text.split("\n")

        in_required_section = False

        required_headings = {

            "requirements",
            "required skills",
            "required qualifications",

            "basic qualifications",
            "minimum qualifications",

            "must have",
            "must-have",

            "essential skills",
            "essential requirements"
        }

        stop_headings = {

            "preferred",
            "preferred skills",
            "preferred qualifications",

            "nice to have",
            "nice-to-have",

            "qualifications",
            "responsibilities",

            "benefits",
            "education",

            "about us",
            "about the company"
        }

        for line in lines:

            clean_line = line.strip()

            if not clean_line:
                continue

            heading = re.sub(
                r"[:\-]+$",
                "",
                clean_line.lower()
            ).strip()

            if heading in required_headings:

                in_required_section = True
                continue

            if (
                in_required_section
                and heading in stop_headings
            ):

                in_required_section = False
                continue

            if in_required_section:

                requirement_text += (
                    " " + clean_line
                )

        requirement_text = (
            requirement_text.lower()
        )

        # ----------------------------------------------------
        # Match skills
        # ----------------------------------------------------

        for skill in all_skills:

            normalized = (
                self.normalize_skill(
                    skill
                )
            )

            if not normalized:
                continue

            pattern = (
                self._skill_pattern(
                    normalized
                )
            )

            if not pattern:
                continue

            # Direct requirement section
            if requirement_text:

                try:

                    if re.search(
                        pattern,
                        requirement_text,
                        flags=re.IGNORECASE
                    ):

                        required.append(
                            normalized
                        )

                        continue

                except re.error:

                    pass

            # Context search
            try:

                matches = re.finditer(
                    pattern,
                    lower_text,
                    flags=re.IGNORECASE
                )

            except re.error:

                continue

            for match in matches:

                start = max(
                    0,
                    match.start() - 180
                )

                end = min(
                    len(lower_text),
                    match.end() + 180
                )

                context = lower_text[
                    start:end
                ]

                if any(
                    term in context
                    for term in strong_terms
                ):

                    required.append(
                        normalized
                    )

                    break

        return self.deduplicate(
            required
        )

    # ========================================================
    # PREFERRED SKILLS
    # ========================================================

    def extract_preferred_skills(
        self,
        text: str,
        all_skills: List[str]
    ) -> List[str]:

        if not text or not all_skills:
            return []

        preferred = []

        lower_text = text.lower()

        preferred_terms = [

            "preferred",
            "strongly preferred",
            "highly preferred",

            "preferred qualification",
            "preferred qualifications",

            "preferred skills",

            "nice to have",
            "nice-to-have",

            "bonus",
            "desired",

            "plus"
        ]

        for skill in all_skills:

            normalized = (
                self.normalize_skill(
                    skill
                )
            )

            pattern = (
                self._skill_pattern(
                    normalized
                )
            )

            if not pattern:
                continue

            try:

                matches = list(
                    re.finditer(
                        pattern,
                        lower_text,
                        flags=re.IGNORECASE
                    )
                )

            except re.error:

                matches = []

            for match in matches:

                start = max(
                    0,
                    match.start() - 180
                )

                end = min(
                    len(lower_text),
                    match.end() + 180
                )

                context = lower_text[
                    start:end
                ]

                if any(
                    term in context
                    for term in preferred_terms
                ):

                    preferred.append(
                        normalized
                    )

                    break

        return self.deduplicate(
            preferred
        )

    # ========================================================
    # NICE TO HAVE
    # ========================================================

    def extract_nice_to_have_skills(
        self,
        text: str,
        all_skills: List[str]
    ) -> List[str]:

        if not text:
            return []

        nice_to_have = []

        lower_text = text.lower()

        optional_terms = [

            "nice to have",
            "nice-to-have",

            "bonus",

            "plus",

            "optional",

            "desired"
        ]

        for skill in all_skills:

            normalized = (
                self.normalize_skill(
                    skill
                )
            )

            pattern = (
                self._skill_pattern(
                    normalized
                )
            )

            if not pattern:
                continue

            try:

                matches = re.finditer(
                    pattern,
                    lower_text,
                    flags=re.IGNORECASE
                )

            except re.error:

                continue

            for match in matches:

                start = max(
                    0,
                    match.start() - 180
                )

                end = min(
                    len(lower_text),
                    match.end() + 180
                )

                context = lower_text[
                    start:end
                ]

                if any(
                    term in context
                    for term in optional_terms
                ):

                    nice_to_have.append(
                        normalized
                    )

                    break

        return self.deduplicate(
            nice_to_have
        )

    # ========================================================
    # CATEGORIZE SKILLS
    # ========================================================

    def categorize_skills(
        self,
        skills: List[str]
    ) -> Dict[str, List[str]]:

        result = {}

        normalized_input = {

            self.normalize_skill(
                skill
            )

            for skill in skills
        }

        for category, category_skills in (
            self.skill_dictionary.items()
        ):

            category_result = []

            for skill in category_skills:

                normalized = (
                    self.normalize_skill(
                        skill
                    )
                )

                if normalized in normalized_input:

                    category_result.append(
                        normalized
                    )

            if category_result:

                result[
                    category
                ] = self.deduplicate(
                    category_result
                )

        return result

    # ========================================================
    # SENTENCE SPLITTING
    # ========================================================

    def split_sentences(
        self,
        text: str
    ) -> List[str]:

        if not text:
            return []

        parts = re.split(
            r"\n+|(?<=[.!?])\s+",
            text
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    # ========================================================
    # LOAD EMBEDDING MODEL
    # ========================================================

    def _load_embedding_model(self):

        if not self.use_embeddings:
            return None

        if self._embedding_model is not None:
            return self._embedding_model

        try:

            self._embedding_model = (
                SentenceTransformer(
                    self.embedding_model_name
                )
            )

            return self._embedding_model

        except Exception:

            self._embedding_model = None

            return None

    # ========================================================
    # GENERATE EMBEDDING
    # ========================================================

    def generate_embedding(
        self,
        text: str
    ) -> Optional[List[float]]:

        text = self.clean_text(
            text
        )

        if not text:
            return None

        model = (
            self._load_embedding_model()
        )

        if model is None:
            return None

        try:

            embedding = model.encode(
                text,
                normalize_embeddings=True
            )

            return embedding.tolist()

        except Exception:

            return None

    # ========================================================
    # SEMANTIC CHUNKS
    # ========================================================

    def generate_semantic_chunks(
        self,
        text: str,
        max_chunks: int = 30
    ) -> List[str]:

        sentences = (
            self.split_sentences(
                text
            )
        )

        if not sentences:
            return []

        chunks = []

        current = ""

        for sentence in sentences:

            if not current:

                current = sentence

            elif (
                len(current)
                + len(sentence)
                < 500
            ):

                current += (
                    " " + sentence
                )

            else:

                chunks.append(
                    current.strip()
                )

                current = sentence

            if len(chunks) >= max_chunks:
                break

        if (
            current
            and len(chunks) < max_chunks
        ):

            chunks.append(
                current.strip()
            )

        return chunks

    # ========================================================
    # SKILL PRIORITY
    # ========================================================

    def classify_skill_priority(
        self,
        skill: str,
        text: str
    ) -> str:

        if not skill or not text:
            return "Low"

        lower_text = text.lower()

        normalized_skill = (
            self.normalize_skill(
                skill
            )
        )

        pattern = (
            self._skill_pattern(
                normalized_skill
            )
        )

        if not pattern:
            return "Low"

        try:

            matches = list(
                re.finditer(
                    pattern,
                    lower_text,
                    flags=re.IGNORECASE
                )
            )

        except re.error:

            matches = []

        if not matches:
            return "Low"

        critical_terms = [

            "required",
            "must have",
            "must-have",

            "mandatory",
            "essential",

            "minimum qualification",
            "minimum qualifications"
        ]

        high_terms = [

            "strongly preferred",
            "highly preferred",

            "preferred qualification",
            "preferred qualifications",

            "preferred skills"
        ]

        medium_terms = [

            "preferred",
            "nice to have",
            "nice-to-have",

            "bonus",
            "desired",
            "plus"
        ]

        priority_rank = {

            "Low": 0,
            "Medium": 1,
            "High": 2,
            "Critical": 3
        }

        best_priority = "Low"

        for match in matches:

            start = max(
                0,
                match.start() - 180
            )

            end = min(
                len(lower_text),
                match.end() + 180
            )

            context = lower_text[
                start:end
            ]

            current_priority = "Low"

            if any(
                term in context
                for term in critical_terms
            ):

                current_priority = "Critical"

            elif any(
                term in context
                for term in high_terms
            ):

                current_priority = "High"

            elif any(
                term in context
                for term in medium_terms
            ):

                current_priority = "Medium"

            if (
                priority_rank[
                    current_priority
                ]
                >
                priority_rank[
                    best_priority
                ]
            ):

                best_priority = (
                    current_priority
                )

        return best_priority

    # ========================================================
    # BUILD SKILL DETAILS
    # ========================================================

    def build_skill_details(
        self,
        skills: List[str],
        text: str
    ) -> List[Dict[str, Any]]:

        details = []

        categories = (
            self.categorize_skills(
                skills
            )
        )

        category_lookup = {}

        for category, category_skills in (
            categories.items()
        ):

            for skill in category_skills:

                category_lookup[
                    self.normalize_skill(
                        skill
                    )
                ] = category

        required = {

            self.normalize_skill(
                skill
            )

            for skill
            in self.extract_required_skills(
                text,
                skills
            )
        }

        preferred = {

            self.normalize_skill(
                skill
            )

            for skill
            in self.extract_preferred_skills(
                text,
                skills
            )
        }

        nice_to_have = {

            self.normalize_skill(
                skill
            )

            for skill
            in self.extract_nice_to_have_skills(
                text,
                skills
            )
        }

        for skill in skills:

            normalized = (
                self.normalize_skill(
                    skill
                )
            )

            if normalized in required:

                priority = "Critical"

            elif normalized in preferred:

                priority = "High"

            elif normalized in nice_to_have:

                priority = "Medium"

            else:

                priority = (
                    self.classify_skill_priority(
                        normalized,
                        text
                    )
                )

            details.append({

                "skill":
                    skill,

                "normalized_skill":
                    normalized,

                "category":
                    category_lookup.get(
                        normalized,
                        "other"
                    ),

                "priority":
                    priority,

                "required":
                    normalized in required,

                "preferred":
                    normalized in preferred,

                "nice_to_have":
                    normalized in nice_to_have
            })

        return details

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        job_description: Any
    ) -> Dict[str, Any]:

        # ----------------------------------------------------
        # Clean JD
        # ----------------------------------------------------

        text = self.clean_text(
            job_description
        )

        # ----------------------------------------------------
        # Empty
        # ----------------------------------------------------

        if not text:

            return {

                "job_title":
                    "Target Position",

                "experience_years":
                    0.0,

                "skills":
                    [],

                "required_skills":
                    [],

                "preferred_skills":
                    [],

                "nice_to_have_skills":
                    [],

                "responsibilities":
                    [],

                "keywords":
                    [],

                "qualifications":
                    [],

                "skill_categories":
                    {},

                "skill_details":
                    [],

                "semantic_chunks":
                    [],

                "embedding":
                    None,

                "job_description":
                    "",

                "jd_text":
                    "",

                "analysis_status":
                    "empty",

                "skills_count":
                    0,

                "required_skills_count":
                    0,

                "preferred_skills_count":
                    0,

                "nice_to_have_skills_count":
                    0,

                "responsibilities_count":
                    0,

                "keywords_count":
                    0
            }

        # ----------------------------------------------------
        # Job title
        # ----------------------------------------------------

        job_title = (
            self.extract_job_title(
                text
            )
        )

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        experience_years = (
            self.extract_experience_years(
                text
            )
        )

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        dictionary_skills = (
            self.extract_skills(
                text
            )
        )

        explicit_skills = (
            self.extract_explicit_skills(
                text
            )
        )

        all_skills = self.deduplicate(

            dictionary_skills
            + explicit_skills
        )

        # ----------------------------------------------------
        # Required
        # ----------------------------------------------------

        required_skills = (
            self.extract_required_skills(
                text,
                all_skills
            )
        )

        # ----------------------------------------------------
        # Preferred
        # ----------------------------------------------------

        preferred_skills = (
            self.extract_preferred_skills(
                text,
                all_skills
            )
        )

        # ----------------------------------------------------
        # Nice to have
        # ----------------------------------------------------

        nice_to_have_skills = (
            self.extract_nice_to_have_skills(
                text,
                all_skills
            )
        )

        # ----------------------------------------------------
        # Responsibilities
        # ----------------------------------------------------

        responsibilities = (
            self.extract_responsibilities(
                text
            )
        )

        # ----------------------------------------------------
        # Qualifications
        # ----------------------------------------------------

        qualifications = (
            self.extract_qualifications(
                text
            )
        )

        # ----------------------------------------------------
        # Keywords
        # ----------------------------------------------------

        keywords = (
            self.extract_keywords(
                text,
                all_skills
            )
        )

        # ----------------------------------------------------
        # Categories
        # ----------------------------------------------------

        skill_categories = (
            self.categorize_skills(
                all_skills
            )
        )

        # ----------------------------------------------------
        # Skill details
        # ----------------------------------------------------

        skill_details = (
            self.build_skill_details(
                all_skills,
                text
            )
        )

        # ----------------------------------------------------
        # Semantic chunks
        # ----------------------------------------------------

        semantic_chunks = (
            self.generate_semantic_chunks(
                text
            )
        )

        # ----------------------------------------------------
        # Embedding
        # ----------------------------------------------------

        embedding = None

        if self.use_embeddings:

            embedding = (
                self.generate_embedding(
                    text
                )
            )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if all_skills:

            status = "success"

        else:

            status = "partial"

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return {

            # Job information
            "job_title":
                job_title,

            "experience_years":
                experience_years,

            # Skills
            "skills":
                all_skills,

            "required_skills":
                required_skills,

            "preferred_skills":
                preferred_skills,

            "nice_to_have_skills":
                nice_to_have_skills,

            # JD content
            "responsibilities":
                responsibilities,

            "keywords":
                keywords,

            "qualifications":
                qualifications,

            # Structured analysis
            "skill_categories":
                skill_categories,

            "skill_details":
                skill_details,

            # Semantic / DL
            "semantic_chunks":
                semantic_chunks,

            "embedding":
                embedding,

            # Original JD
            "job_description":
                text,

            "jd_text":
                text,

            # Status
            "analysis_status":
                status,

            # Counts
            "skills_count":
                len(all_skills),

            "required_skills_count":
                len(required_skills),

            "preferred_skills_count":
                len(preferred_skills),

            "nice_to_have_skills_count":
                len(nice_to_have_skills),

            "responsibilities_count":
                len(responsibilities),

            "keywords_count":
                len(keywords)
        }

    # ========================================================
    # ANALYZE DICT
    # ========================================================

    def analyze_dict(
        self,
        jd_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(
            jd_data,
            dict
        ):

            return self.analyze(
                jd_data
            )

        text_parts = []

        possible_fields = [

            "job_description",
            "Job Description",

            "description",
            "Description",

            "responsibilities",
            "Responsibilities",

            "skills",
            "Skills",

            "requirements",
            "Requirements",

            "qualifications",
            "Qualifications"
        ]

        for field in possible_fields:

            value = jd_data.get(
                field
            )

            if value is None:
                continue

            if isinstance(
                value,
                list
            ):

                text_parts.extend(

                    str(item)
                    for item in value
                    if item
                )

            else:

                value = str(
                    value
                ).strip()

                if value:

                    text_parts.append(
                        value
                    )

        combined_text = "\n".join(
            text_parts
        )

        result = self.analyze(
            combined_text
        )

        # Explicit title
        explicit_title = (

            jd_data.get(
                "job_title"
            )

            or jd_data.get(
                "Job Title"
            )

            or jd_data.get(
                "title"
            )

            or jd_data.get(
                "Title"
            )
        )

        if explicit_title:

            result["job_title"] = str(
                explicit_title
            ).strip()

        # Explicit experience
        explicit_experience = (

            jd_data.get(
                "experience_years"
            )

            or jd_data.get(
                "Experience Years"
            )
        )

        if explicit_experience is not None:

            try:

                result[
                    "experience_years"
                ] = float(
                    explicit_experience
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        result[
            "source_data"
        ] = jd_data

        return result

    # ========================================================
    # GET SKILLS
    # ========================================================

    def get_skills(
        self,
        job_description: Any
    ) -> List[str]:

        result = self.analyze(
            job_description
        )

        return result.get(
            "skills",
            []
        )

    # ========================================================
    # GET RESPONSIBILITIES
    # ========================================================

    def get_responsibilities(
        self,
        job_description: Any
    ) -> List[str]:

        result = self.analyze(
            job_description
        )

        return result.get(
            "responsibilities",
            []
        )

    # ========================================================
    # GET REQUIRED SKILLS
    # ========================================================

    def get_required_skills(
        self,
        job_description: Any
    ) -> List[str]:

        result = self.analyze(
            job_description
        )

        return result.get(
            "required_skills",
            []
        )

    # ========================================================
    # GET SUMMARY
    # ========================================================

    def get_summary(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(
            analysis,
            dict
        ):

            return {}

        return {

            "job_title":
                analysis.get(
                    "job_title",
                    "Target Position"
                ),

            "experience_years":
                analysis.get(
                    "experience_years",
                    0
                ),

            "skills_count":
                len(
                    analysis.get(
                        "skills",
                        []
                    )
                ),

            "required_skills_count":
                len(
                    analysis.get(
                        "required_skills",
                        []
                    )
                ),

            "preferred_skills_count":
                len(
                    analysis.get(
                        "preferred_skills",
                        []
                    )
                ),

            "nice_to_have_count":
                len(
                    analysis.get(
                        "nice_to_have_skills",
                        []
                    )
                ),

            "responsibilities_count":
                len(
                    analysis.get(
                        "responsibilities",
                        []
                    )
                ),

            "keywords_count":
                len(
                    analysis.get(
                        "keywords",
                        []
                    )
                )
        }

    # ========================================================
    # TAILORING GUIDANCE
    # ========================================================

    def get_tailoring_guidance(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:

        if not isinstance(
            analysis,
            dict
        ):

            return []

        guidance = []

        job_title = analysis.get(
            "job_title",
            "target role"
        )

        skills = analysis.get(
            "skills",
            []
        )

        required = analysis.get(
            "required_skills",
            []
        )

        preferred = analysis.get(
            "preferred_skills",
            []
        )

        responsibilities = analysis.get(
            "responsibilities",
            []
        )

        if job_title:

            guidance.append(
                f"Prioritize existing resume "
                f"evidence relevant to the "
                f"{job_title} role."
            )

        if required:

            guidance.append(
                "Compare candidate's existing "
                "skills against required JD "
                "skills before tailoring."
            )

        if preferred:

            guidance.append(
                "Highlight preferred skills "
                "only when they already exist "
                "in the candidate resume."
            )

        if responsibilities:

            guidance.append(
                "Prioritize existing experience "
                "and project evidence that is "
                "semantically relevant to the "
                "JD responsibilities."
            )

        if skills:

            guidance.append(
                "Missing JD skills must not be "
                "added to the candidate resume "
                "without candidate evidence."
            )

        return guidance


# ============================================================
# MODULE-LEVEL BACKWARD COMPATIBILITY FUNCTION
# ============================================================
#
# THIS IS THE IMPORTANT FIX FOR YOUR ERROR.
#
# Some files are doing:
#
# from modules.jd_analyzer import analyze_job_description
#
# Previously this function existed only INSIDE JDAnalyzer.
# Python therefore could not import it directly from the module.
#
# Now both styles work:
#
# 1.
# analyzer = JDAnalyzer()
# analyzer.analyze_job_description(jd)
#
# 2.
# from modules.jd_analyzer import analyze_job_description
# analyze_job_description(jd)
#
# ============================================================

def analyze_job_description(
    job_description: Any
) -> Dict[str, Any]:
    """
    Module-level backward-compatible function.

    This fixes:

        ImportError:
        cannot import name 'analyze_job_description'

    Parameters
    ----------
    job_description:
        Raw Job Description text.

    Returns
    -------
    dict
        Structured JD analysis.
    """

    analyzer = JDAnalyzer(
        use_embeddings=False
    )

    return analyzer.analyze(
        job_description
    )


# ============================================================
# MODULE-LEVEL ANALYZE DICT
# ============================================================

def analyze_jd(
    job_description: Any
) -> Dict[str, Any]:
    """
    Short module-level alias.

    Example:

        from modules.jd_analyzer import analyze_jd

        result = analyze_jd(jd)
    """

    return analyze_job_description(
        job_description
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 75)
    print("AI RESUME TAILORING SYSTEM")
    print("JOB DESCRIPTION ANALYZER TEST")
    print("=" * 75)

    sample_jd = """

    Data Analyst

    We are looking for a Data Analyst
    with 3+ years of experience.

    Required Skills:

    SQL
    Power BI
    Excel
    Python
    Data Analysis
    Reporting

    Preferred Skills:

    Azure
    Tableau
    Machine Learning

    Responsibilities:

    - Analyze business data using SQL.
    - Develop reporting dashboards using Power BI.
    - Prepare business reports and data visualizations.
    - Clean and preprocess datasets.
    - Support data integration and automation.

    Nice to Have:

    Experience with Azure and Tableau.

    Qualifications:

    Bachelor's degree in Computer Science,
    Data Science, Statistics, or a related field.

    """

    # ========================================================
    # CREATE ANALYZER
    # ========================================================

    analyzer = JDAnalyzer(
        use_embeddings=False
    )

    # ========================================================
    # ANALYZE
    # ========================================================

    result = analyzer.analyze(
        sample_jd
    )

    # ========================================================
    # JOB INFORMATION
    # ========================================================

    print()
    print("=" * 75)
    print("JOB INFORMATION")
    print("=" * 75)

    print(
        "Job Title:",
        result["job_title"]
    )

    print(
        "Experience:",
        result["experience_years"],
        "years"
    )

    # ========================================================
    # ALL SKILLS
    # ========================================================

    print()
    print("=" * 75)
    print("ALL JD SKILLS")
    print("=" * 75)

    for skill in result["skills"]:

        print(
            "  ✓",
            skill
        )

    # ========================================================
    # REQUIRED
    # ========================================================

    print()
    print("=" * 75)
    print("REQUIRED SKILLS")
    print("=" * 75)

    for skill in result[
        "required_skills"
    ]:

        print(
            "  🔴",
            skill
        )

    # ========================================================
    # PREFERRED
    # ========================================================

    print()
    print("=" * 75)
    print("PREFERRED SKILLS")
    print("=" * 75)

    for skill in result[
        "preferred_skills"
    ]:

        print(
            "  🟠",
            skill
        )

    # ========================================================
    # NICE TO HAVE
    # ========================================================

    print()
    print("=" * 75)
    print("NICE TO HAVE")
    print("=" * 75)

    for skill in result[
        "nice_to_have_skills"
    ]:

        print(
            "  🟡",
            skill
        )

    # ========================================================
    # RESPONSIBILITIES
    # ========================================================

    print()
    print("=" * 75)
    print("RESPONSIBILITIES")
    print("=" * 75)

    for responsibility in result[
        "responsibilities"
    ]:

        print(
            "  •",
            responsibility
        )

    # ========================================================
    # KEYWORDS
    # ========================================================

    print()
    print("=" * 75)
    print("KEYWORDS")
    print("=" * 75)

    for keyword in result[
        "keywords"
    ]:

        print(
            "  •",
            keyword
        )

    # ========================================================
    # CATEGORIES
    # ========================================================

    print()
    print("=" * 75)
    print("SKILL CATEGORIES")
    print("=" * 75)

    for category, skills in (
        result[
            "skill_categories"
        ].items()
    ):

        print()
        print(
            category.upper(),
            ":"
        )

        for skill in skills:

            print(
                "   ✓",
                skill
            )

    # ========================================================
    # SKILL PRIORITY
    # ========================================================

    print()
    print("=" * 75)
    print("SKILL PRIORITY ANALYSIS")
    print("=" * 75)

    for detail in result[
        "skill_details"
    ]:

        print(
            f"  {detail['skill']:<30}"
            f" | Category: "
            f"{detail['category']:<25}"
            f" | Priority: "
            f"{detail['priority']}"
        )

    # ========================================================
    # GUIDANCE
    # ========================================================

    print()
    print("=" * 75)
    print("TAILORING GUIDANCE")
    print("=" * 75)

    guidance = (
        analyzer.get_tailoring_guidance(
            result
        )
    )

    for item in guidance:

        print(
            "  ✓",
            item
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 75)
    print("SUMMARY")
    print("=" * 75)

    summary = analyzer.get_summary(
        result
    )

    for key, value in (
        summary.items()
    ):

        print(
            f"{key}: {value}"
        )

    # ========================================================
    # IMPORTANT IMPORT TEST
    # ========================================================

    print()
    print("=" * 75)
    print("MODULE-LEVEL FUNCTION TEST")
    print("=" * 75)

    module_result = (
        analyze_job_description(
            sample_jd
        )
    )

    print(
        "Module-level import/function:",
        "SUCCESS"
    )

    print(
        "Detected Job Title:",
        module_result[
            "job_title"
        ]
    )

    print(
        "Detected Skills:",
        len(
            module_result[
                "skills"
            ]
        )
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("=" * 75)
    print("JD ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 75)
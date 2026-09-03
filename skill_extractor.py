"""
Skill Extraction Engine
AI Resume Tailoring System

Purpose:
- Extract technical and professional skills from Resume/JD text
- Normalize skill names
- Compare resume skills with JD skills
- Identify matched and missing skills
- Avoid false substring matches
- Independent module: does NOT import any other project module
"""

import re
from collections import Counter
from typing import Any, Dict, List


# ============================================================
# SKILL DATABASE
# ============================================================

SKILL_DATABASE = {

    # --------------------------------------------------------
    # PROGRAMMING LANGUAGES
    # --------------------------------------------------------
    "programming": [
        "Python",
        "R",
        "SQL",
        "Java",
        "JavaScript",
        "TypeScript",
        "C",
        "C++",
        "C#",
        "Go",
        "Rust",
        "Scala",
        "Kotlin",
        "Swift",
        "PHP",
        "Ruby",
        "Bash",
        "PowerShell",
    ],

    # --------------------------------------------------------
    # DATA ANALYTICS
    # --------------------------------------------------------
    "data_analytics": [
        "Excel",
        "Advanced Excel",
        "Power Query",
        "Power Pivot",
        "VBA",
        "Pandas",
        "NumPy",
        "SciPy",
        "Matplotlib",
        "Seaborn",
        "Plotly",
        "Statsmodels",
        "Jupyter",
        "Anaconda",
        "Data Analysis",
        "Data Analytics",
        "Data Cleaning",
        "Data Preprocessing",
        "Exploratory Data Analysis",
        "EDA",
        "ETL",
        "ELT",
        "Data Visualization",
        "Dashboard",
        "Dashboards",
        "Reporting",
        "KPI",
        "KPIs",
        "Statistics",
        "Statistical Analysis",
        "Hypothesis Testing",
        "A/B Testing",
        "Regression Analysis",
        "Time Series Analysis",
        "Forecasting",
    ],

    # --------------------------------------------------------
    # BUSINESS INTELLIGENCE
    # --------------------------------------------------------
    "business_intelligence": [
        "Power BI",
        "DAX",
        "Tableau",
        "Looker",
        "Looker Studio",
        "Qlik",
        "MicroStrategy",
        "SSRS",
        "Business Intelligence",
        "BI",
    ],

    # --------------------------------------------------------
    # DATABASES
    # --------------------------------------------------------
    "databases": [
        "MySQL",
        "PostgreSQL",
        "SQL Server",
        "Microsoft SQL Server",
        "Oracle",
        "SQLite",
        "MongoDB",
        "Redis",
        "Cassandra",
        "Snowflake",
        "BigQuery",
        "Amazon Redshift",
        "Redshift",
        "Databricks",
        "Database",
        "Databases",
        "Data Warehouse",
        "Data Warehousing",
        "Data Lake",
        "Data Lakehouse",
    ],

    # --------------------------------------------------------
    # MACHINE LEARNING
    # --------------------------------------------------------
    "machine_learning": [
        "Machine Learning",
        "Supervised Learning",
        "Unsupervised Learning",
        "Semi-Supervised Learning",
        "Reinforcement Learning",
        "Scikit-learn",
        "Scikit Learn",
        "sklearn",
        "XGBoost",
        "LightGBM",
        "CatBoost",
        "Random Forest",
        "Decision Tree",
        "Logistic Regression",
        "Linear Regression",
        "Support Vector Machine",
        "SVM",
        "K-Nearest Neighbors",
        "KNN",
        "Naive Bayes",
        "Gradient Boosting",
        "AdaBoost",
        "Clustering",
        "K-Means",
        "KMeans",
        "DBSCAN",
        "PCA",
        "Principal Component Analysis",
        "Feature Engineering",
        "Feature Selection",
        "Model Training",
        "Model Evaluation",
        "Cross Validation",
        "Cross-Validation",
        "Hyperparameter Tuning",
        "Ensemble Learning",
        "Anomaly Detection",
        "Recommendation Systems",
        "Predictive Modeling",
        "Classification",
        "Regression",
    ],

    # --------------------------------------------------------
    # DEEP LEARNING
    # --------------------------------------------------------
    "deep_learning": [
        "Deep Learning",
        "Neural Networks",
        "Artificial Neural Networks",
        "ANN",
        "Convolutional Neural Networks",
        "CNN",
        "Recurrent Neural Networks",
        "RNN",
        "LSTM",
        "GRU",
        "TensorFlow",
        "Keras",
        "PyTorch",
        "Torch",
        "Deep Neural Networks",
        "DNN",
        "Transfer Learning",
        "Fine Tuning",
        "Fine-Tuning",
    ],

    # --------------------------------------------------------
    # NLP / GENERATIVE AI
    # --------------------------------------------------------
    "nlp_genai": [
        "Artificial Intelligence",
        "AI",
        "Natural Language Processing",
        "NLP",
        "Natural Language Understanding",
        "NLU",
        "Text Classification",
        "Named Entity Recognition",
        "NER",
        "Sentiment Analysis",
        "Tokenization",
        "Text Mining",
        "Text Processing",
        "Word Embeddings",
        "Embeddings",
        "Transformers",
        "BERT",
        "GPT",
        "Large Language Models",
        "LLM",
        "LLMs",
        "Generative AI",
        "GenAI",
        "Prompt Engineering",
        "LangChain",
        "LlamaIndex",
        "RAG",
        "Retrieval Augmented Generation",
        "Retrieval-Augmented Generation",
        "Vector Database",
        "Vector Databases",
        "FAISS",
        "Pinecone",
        "ChromaDB",
        "OpenAI",
        "Hugging Face",
        "AI Agents",
        "Agents",
        "Function Calling",
        "Fine Tuning",
        "LoRA",
        "PEFT",
    ],

    # --------------------------------------------------------
    # COMPUTER VISION
    # --------------------------------------------------------
    "computer_vision": [
        "Computer Vision",
        "OpenCV",
        "OpenCV-Python",
        "YOLO",
        "Object Detection",
        "Image Classification",
        "Image Segmentation",
        "Image Processing",
        "OCR",
        "Optical Character Recognition",
        "CNN",
        "TorchVision",
        "Face Detection",
        "Face Recognition",
    ],

    # --------------------------------------------------------
    # DATA ENGINEERING
    # --------------------------------------------------------
    "data_engineering": [
        "Apache Spark",
        "Spark",
        "PySpark",
        "Apache Kafka",
        "Kafka",
        "Apache Airflow",
        "Airflow",
        "dbt",
        "Hadoop",
        "Hive",
        "Presto",
        "Trino",
        "Databricks",
        "Delta Lake",
        "Data Pipelines",
        "Data Pipeline",
        "Data Engineering",
        "Data Orchestration",
    ],

    # --------------------------------------------------------
    # CLOUD
    # --------------------------------------------------------
    "cloud": [
        "AWS",
        "Amazon Web Services",
        "Azure",
        "Microsoft Azure",
        "Google Cloud",
        "GCP",
        "Amazon EC2",
        "Amazon S3",
        "AWS Lambda",
        "Azure Blob Storage",
        "Azure Machine Learning",
        "Azure ML",
        "Amazon SageMaker",
        "Google Vertex AI",
        "Vertex AI",
        "Cloud Computing",
    ],

    # --------------------------------------------------------
    # DEVOPS / MLOPS
    # --------------------------------------------------------
    "devops_mlops": [
        "Git",
        "GitHub",
        "GitLab",
        "Docker",
        "Kubernetes",
        "K8s",
        "CI/CD",
        "Continuous Integration",
        "Continuous Deployment",
        "MLflow",
        "DVC",
        "MLOps",
        "DevOps",
        "REST API",
        "API",
        "FastAPI",
        "Flask",
        "Streamlit",
    ],

    # --------------------------------------------------------
    # WEB DEVELOPMENT
    # --------------------------------------------------------
    "web_development": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "NodeJS",
        "Angular",
        "Vue.js",
        "Django",
        "Flask",
        "FastAPI",
        "REST API",
        "Web Development",
        "Frontend",
        "Backend",
        "Full Stack",
    ],

    # --------------------------------------------------------
    # PROFESSIONAL / SOFT SKILLS
    # --------------------------------------------------------
    "professional": [
        "Communication",
        "Teamwork",
        "Leadership",
        "Problem Solving",
        "Critical Thinking",
        "Analytical Thinking",
        "Stakeholder Management",
        "Project Management",
        "Time Management",
        "Presentation",
        "Presentation Skills",
        "Collaboration",
        "Agile",
        "Scrum",
        "Research",
        "Documentation",
    ],

    # --------------------------------------------------------
    # MARKETING / BUSINESS
    # --------------------------------------------------------
    "business": [
        "Digital Marketing",
        "SEO",
        "Search Engine Optimization",
        "SEM",
        "Social Media Marketing",
        "Content Marketing",
        "Market Research",
        "Sales",
        "Customer Relationship Management",
        "CRM",
        "Business Analysis",
        "Business Strategy",
    ],

    # --------------------------------------------------------
    # FINANCE / ACCOUNTING
    # --------------------------------------------------------
    "finance": [
        "Financial Analysis",
        "Financial Modeling",
        "Accounting",
        "Bookkeeping",
        "Financial Reporting",
        "Budgeting",
        "Forecasting",
        "Risk Analysis",
        "Risk Management",
    ],

    # --------------------------------------------------------
    # CYBERSECURITY
    # --------------------------------------------------------
    "cybersecurity": [
        "Cybersecurity",
        "Information Security",
        "Network Security",
        "Ethical Hacking",
        "Penetration Testing",
        "Vulnerability Assessment",
        "Cryptography",
        "Firewall",
        "SIEM",
    ],
}


# ============================================================
# ALIASES
# ============================================================

ALIASES = {
    "py": "python",
    "powerbi": "power bi",
    "power bi": "power bi",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "tf": "tensorflow",
    "torch": "pytorch",
    "opencv-python": "opencv",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "genai": "generative ai",
    "llms": "llm",
    "nodejs": "node.js",
    "postgres": "postgresql",
    "gcp": "google cloud",
    "k8s": "kubernetes",
    "aws cloud": "aws",
    "eda": "exploratory data analysis",
    "nlp": "natural language processing",
    "rag": "retrieval augmented generation",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text: Any) -> str:
    """Normalize input text for reliable skill matching."""
    if text is None:
        return ""
    text = str(text).lower()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("&", " and ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    """Convert skill into canonical form."""
    skill = normalize_text(skill)
    return ALIASES.get(skill, skill)


# ============================================================
# SKILL LIST
# ============================================================

def get_all_skills() -> List[str]:
    """Return complete unique skill list."""
    skills = []
    for category_skills in SKILL_DATABASE.values():
        skills.extend(category_skills)
    return list(dict.fromkeys(skills))


# ============================================================
# SAFE SKILL MATCHING
# ============================================================

def skill_exists_in_text(skill: str, text: str) -> bool:
    """Check whether a skill exists in text using word boundaries."""
    skill_normalized = normalize_skill(skill)
    text_normalized = normalize_text(text)
    if not skill_normalized or not text_normalized:
        return False
    escaped_skill = re.escape(skill_normalized)
    escaped_skill = escaped_skill.replace(r"\ ", r"\s+")
    pattern = rf"(?<!\w){escaped_skill}(?!\w)"
    return re.search(pattern, text_normalized, flags=re.IGNORECASE) is not None


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(text: Any, categories: List[str] = None) -> List[str]:
    """Extract skills from text."""
    text = normalize_text(text)
    if not text:
        return []

    if categories is None:
        selected_categories = SKILL_DATABASE
    else:
        selected_categories = {
            cat: SKILL_DATABASE[cat]
            for cat in categories
            if cat in SKILL_DATABASE
        }

    found_skills = []
    for skill_list in selected_categories.values():
        for skill in skill_list:
            if skill_exists_in_text(skill, text):
                canonical = normalize_skill(skill)
                if canonical not in [normalize_skill(x) for x in found_skills]:
                    found_skills.append(skill)
    return found_skills


# ============================================================
# EXTRACT SKILLS WITH FREQUENCY
# ============================================================

def extract_skills_with_frequency(text: Any) -> Dict[str, int]:
    """Extract skills and count their occurrences."""
    text = normalize_text(text)
    if not text:
        return {}

    counter = Counter()
    for category_skills in SKILL_DATABASE.values():
        for skill in category_skills:
            normalized_skill = normalize_skill(skill)
            escaped_skill = re.escape(normalized_skill)
            escaped_skill = escaped_skill.replace(r"\ ", r"\s+")
            pattern = rf"(?<!\w){escaped_skill}(?!\w)"
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                counter[skill] += len(matches)
    return dict(counter)


# ============================================================
# COMPARE SKILLS
# ============================================================

def compare_skills(resume_text: Any, job_description: Any) -> Dict[str, Any]:
    """Compare resume skills against JD skills."""
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    resume_canonical = {normalize_skill(skill): skill for skill in resume_skills}
    jd_canonical = {normalize_skill(skill): skill for skill in jd_skills}

    matched = []
    missing = []
    for canonical, jd_skill in jd_canonical.items():
        if canonical in resume_canonical:
            matched.append(resume_canonical[canonical])
        else:
            missing.append(jd_skill)

    additional = []
    jd_set = set(jd_canonical.keys())
    for canonical, resume_skill in resume_canonical.items():
        if canonical not in jd_set:
            additional.append(resume_skill)

    total_jd_skills = len(jd_skills)
    coverage = (len(matched) / total_jd_skills) * 100 if total_jd_skills > 0 else 0.0

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "additional_skills": additional,
        "skill_coverage": round(coverage, 2),
        "resume_skill_count": len(resume_skills),
        "jd_skill_count": len(jd_skills),
        "matched_skill_count": len(matched),
        "missing_skill_count": len(missing),
        "match_percentage": round(coverage, 2),
    }


# ============================================================
# CATEGORY HELPERS
# ============================================================

def get_skill_category(skill: str) -> str:
    """Return category of a skill."""
    normalized = normalize_skill(skill)
    for category, skills in SKILL_DATABASE.items():
        for item in skills:
            if normalize_skill(item) == normalized:
                return category
    return "other"


def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Group skills by category."""
    result = {}
    for skill in skills:
        category = get_skill_category(skill)
        result.setdefault(category, []).append(skill)
    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    resume = """
    Data Scientist with experience in Python, SQL, Pandas,
    NumPy, Machine Learning, Scikit-learn, TensorFlow,
    Power BI and Streamlit.
    """
    jd = """
    We are looking for a Data Scientist with Python, SQL,
    Machine Learning, TensorFlow, PyTorch, Power BI,
    Docker and AWS experience.
    """

    result = compare_skills(resume, jd)
    print("\n" + "=" * 70)
    print("SKILL EXTRACTION TEST")
    print("=" * 70)
    print("\nResume Skills:", result["resume_skills"])
    print("\nJD Skills:", result["jd_skills"])
    print("\nMatched Skills:", result["matched_skills"])
    print("\nMissing Skills:", result["missing_skills"])
    print("\nAdditional Resume Skills:", result["additional_skills"])
    print(f"\nSkill Coverage: {result['skill_coverage']}%")
    print("\n" + "=" * 70)
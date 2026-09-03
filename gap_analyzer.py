"""
AI Resume Tailoring System – Gap Analyzer
=========================================

Compares master resume skills with JD skills, identifies matches and gaps.
Missing skills are NEVER added to candidate skills.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

import numpy as np

# ============================================================
# OPTIONAL SENTENCE TRANSFORMER
# ============================================================

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    ST_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    cosine_similarity = None
    ST_AVAILABLE = False


# ============================================================
# GAP ANALYZER
# ============================================================

class GapAnalyzer:
    """
    Professional skill-gap analyzer.

    Uses:
    1. Exact skill matching
    2. Semantic similarity (if SentenceTransformer available)
    3. Priority analysis (Critical/High/Medium/Low)
    4. Category coverage

    Missing skills are NEVER inserted into the resume.
    """

    # ========================================================
    # SKILL CATEGORIES
    # ========================================================

    DEFAULT_SKILL_CATEGORIES = {
        "programming": {
            "python", "r", "sql", "java", "javascript", "typescript",
            "c", "c++", "c#", "go", "rust", "scala", "kotlin", "swift",
            "php", "ruby", "bash", "powershell"
        },
        "data_analytics": {
            "excel", "advanced excel", "power query", "power pivot", "vba",
            "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
            "statsmodels", "jupyter", "anaconda", "data analysis",
            "data analytics", "data cleaning", "data preprocessing",
            "exploratory data analysis", "eda", "etl", "elt",
            "data visualization", "dashboard", "dashboards", "reporting",
            "kpi", "kpis", "statistics", "statistical analysis",
            "hypothesis testing", "a/b testing", "regression analysis",
            "time series analysis", "forecasting"
        },
        "business_intelligence": {
            "power bi", "dax", "tableau", "looker", "looker studio",
            "qlik", "microstrategy", "ssrs", "business intelligence", "bi"
        },
        "databases": {
            "mysql", "postgresql", "sql server", "microsoft sql server",
            "oracle", "sqlite", "mongodb", "redis", "cassandra",
            "snowflake", "bigquery", "amazon redshift", "redshift",
            "databricks", "database", "databases", "data warehouse",
            "data warehousing", "data lake", "data lakehouse"
        },
        "machine_learning": {
            "machine learning", "supervised learning", "unsupervised learning",
            "semi-supervised learning", "reinforcement learning",
            "scikit-learn", "xgboost", "lightgbm", "catboost",
            "random forest", "decision tree", "logistic regression",
            "linear regression", "support vector machine", "svm",
            "knn", "k-nearest neighbors", "naive bayes", "gradient boosting",
            "adaboost", "clustering", "k-means", "kmeans", "dbscan",
            "pca", "principal component analysis", "feature engineering",
            "feature selection", "model training", "model evaluation",
            "cross validation", "cross-validation", "hyperparameter tuning",
            "ensemble learning", "anomaly detection", "recommendation systems",
            "predictive modeling", "classification", "regression"
        },
        "deep_learning": {
            "deep learning", "neural networks", "artificial neural networks",
            "ann", "convolutional neural networks", "cnn",
            "recurrent neural networks", "rnn", "lstm", "gru",
            "tensorflow", "keras", "pytorch", "deep neural networks",
            "dnn", "transfer learning", "fine tuning", "fine-tuning"
        },
        "nlp_genai": {
            "artificial intelligence", "natural language processing",
            "nlp", "natural language understanding", "nlu",
            "text classification", "named entity recognition", "ner",
            "sentiment analysis", "tokenization", "text mining",
            "text processing", "word embeddings", "embeddings",
            "transformers", "bert", "gpt", "large language models",
            "llm", "generative ai", "prompt engineering", "langchain",
            "llamaindex", "rag", "retrieval augmented generation",
            "vector database", "vector databases", "faiss", "pinecone",
            "chromadb", "openai", "hugging face", "ai agents",
            "agents", "function calling", "lora", "peft"
        },
        "computer_vision": {
            "computer vision", "opencv", "yolo", "object detection",
            "image classification", "image segmentation", "image processing",
            "ocr", "optical character recognition", "face detection",
            "face recognition"
        },
        "data_engineering": {
            "apache spark", "spark", "pyspark", "apache kafka", "kafka",
            "apache airflow", "airflow", "dbt", "hadoop", "hive",
            "presto", "trino", "databricks", "delta lake",
            "data pipelines", "data pipeline", "data engineering",
            "data orchestration"
        },
        "cloud": {
            "aws", "amazon web services", "azure", "microsoft azure",
            "google cloud", "gcp", "amazon ec2", "amazon s3",
            "aws lambda", "azure blob storage", "azure machine learning",
            "azure ml", "amazon sagemaker", "google vertex ai",
            "vertex ai", "cloud computing"
        },
        "devops_mlops": {
            "git", "github", "gitlab", "docker", "kubernetes", "k8s",
            "ci/cd", "continuous integration", "continuous deployment",
            "mlflow", "dvc", "mlops", "devops", "rest api", "api",
            "fastapi", "flask", "streamlit"
        },
        "web_development": {
            "html", "css", "javascript", "react", "node.js", "nodejs",
            "angular", "vue.js", "django", "flask", "fastapi",
            "rest api", "web development", "frontend", "backend",
            "full stack"
        },
        "soft_skills": {
            "communication", "teamwork", "leadership", "problem solving",
            "critical thinking", "analytical thinking",
            "stakeholder management", "project management",
            "time management", "presentation", "presentation skills",
            "collaboration", "agile", "scrum", "research", "documentation"
        }
    }

    # ========================================================
    # ALIASES
    # ========================================================

    SKILL_ALIASES = {
        "py": "python", "powerbi": "power bi", "power-bi": "power bi",
        "scikit learn": "scikit-learn", "sklearn": "scikit-learn",
        "tf": "tensorflow", "torch": "pytorch", "opencv-python": "opencv",
        "cv": "computer vision", "js": "javascript", "ts": "typescript",
        "nodejs": "node.js", "node js": "node.js", "postgres": "postgresql",
        "gen ai": "generative ai", "genai": "generative ai",
        "llms": "llm", "large language model": "large language models",
        "retrieval-augmented generation": "retrieval augmented generation",
        "ai agent": "ai agents", "k8s": "kubernetes", "gcp": "google cloud"
    }

    # ========================================================
    # PRIORITY TERMS
    # ========================================================

    CRITICAL_TERMS = {
        "required", "must have", "must-have", "mandatory",
        "essential", "required skills", "requirements",
        "minimum requirement", "core requirement"
    }
    HIGH_TERMS = {
        "strongly preferred", "highly preferred", "strong preference",
        "preferred qualifications", "preferred skills"
    }
    MEDIUM_TERMS = {
        "preferred", "nice to have", "nice-to-have", "plus",
        "bonus", "desired", "preferred qualification"
    }

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self, similarity_threshold: float = 0.72, use_embeddings: bool = True, model_name: str = "all-MiniLM-L6-v2"):
        self.similarity_threshold = max(0.0, min(float(similarity_threshold), 1.0))
        self.use_embeddings = bool(use_embeddings) and ST_AVAILABLE
        self.model_name = model_name
        self._model = None

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def clean_skill(skill: Any) -> str:
        if skill is None:
            return ""
        text = str(skill).strip().lower()
        text = text.replace("&", " and ")
        text = text.replace("–", "-").replace("—", "-")
        text = re.sub(r"\s+", " ", text)
        text = text.strip(" ,.;:|/")
        return GapAnalyzer.SKILL_ALIASES.get(text, text)

    def normalize_skills(self, skills: Any) -> List[str]:
        if skills is None:
            return []
        if isinstance(skills, str):
            parts = re.split(r"[,;|\n]+", skills)
        elif isinstance(skills, (list, tuple, set)):
            parts = list(skills)
        else:
            parts = [skills]

        result = []
        seen = set()
        for item in parts:
            skill = self.clean_skill(item)
            if skill and skill not in seen:
                seen.add(skill)
                result.append(skill)
        return result

    # ========================================================
    # EMBEDDING MODEL
    # ========================================================

    def _get_model(self):
        if not self.use_embeddings:
            return None
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Warning: Could not load SentenceTransformer: {e}")
                self._model = None
                self.use_embeddings = False
        return self._model

    # ========================================================
    # SEMANTIC MATCHING
    # ========================================================

    def semantic_match_skills(self, resume_skills: List[str], jd_skills: List[str]) -> List[Dict[str, Any]]:
        resume_skills = self.normalize_skills(resume_skills)
        jd_skills = self.normalize_skills(jd_skills)

        if not resume_skills or not jd_skills:
            return []

        model = self._get_model()
        if model is None or cosine_similarity is None:
            return []

        try:
            resume_embeddings = model.encode(resume_skills, normalize_embeddings=True, show_progress_bar=False)
            jd_embeddings = model.encode(jd_skills, normalize_embeddings=True, show_progress_bar=False)
            sim_matrix = cosine_similarity(jd_embeddings, resume_embeddings)

            candidate_pairs = []
            for jd_idx, jd_skill in enumerate(jd_skills):
                for res_idx, res_skill in enumerate(resume_skills):
                    score = float(sim_matrix[jd_idx][res_idx])
                    if score >= self.similarity_threshold:
                        candidate_pairs.append((score, jd_idx, res_idx))

            candidate_pairs.sort(key=lambda x: x[0], reverse=True)
            used_jd, used_resume = set(), set()
            matches = []
            for score, jd_idx, res_idx in candidate_pairs:
                if jd_idx in used_jd or res_idx in used_resume:
                    continue
                matches.append({
                    "jd_skill": jd_skills[jd_idx],
                    "resume_skill": resume_skills[res_idx],
                    "score": round(score, 4),
                    "type": "semantic"
                })
                used_jd.add(jd_idx)
                used_resume.add(res_idx)
            return matches
        except Exception as e:
            print(f"Warning: Semantic skill matching failed: {e}")
            return []

    # ========================================================
    # PRIORITY
    # ========================================================

    def get_skill_priority(self, skill: str, jd_text: str = "") -> str:
        if not jd_text:
            return "Low"
        context = str(jd_text).lower()
        skill_lower = str(skill).lower()
        start = context.find(skill_lower)
        if start == -1:
            return "Low"
        start = max(0, start - 250)
        end = min(len(context), start + 500)
        ctx = context[start:end]

        if any(term in ctx for term in self.CRITICAL_TERMS):
            return "Critical"
        if any(term in ctx for term in self.HIGH_TERMS):
            return "High"
        if any(term in ctx for term in self.MEDIUM_TERMS):
            return "Medium"
        return "Low"

    # ========================================================
    # CATEGORY
    # ========================================================

    def get_skill_category(self, skill: str) -> str:
        normalized = self.clean_skill(skill)
        for category, skills in self.DEFAULT_SKILL_CATEGORIES.items():
            if normalized in {self.clean_skill(s) for s in skills}:
                return category
        return "other"

    # ========================================================
    # CATEGORY COVERAGE
    # ========================================================

    def calculate_category_coverage(self, resume_skills: List[str], jd_skills: List[str], matched_jd_skills: Optional[Set[str]] = None) -> Dict[str, Dict[str, Any]]:
        resume_set = set(self.normalize_skills(resume_skills))
        jd_list = self.normalize_skills(jd_skills)
        matched_set = {self.clean_skill(s) for s in (matched_jd_skills or set())}

        categories = {}
        for skill in jd_list:
            category = self.get_skill_category(skill)
            if category not in categories:
                categories[category] = {"required": 0, "matched": 0, "missing": 0, "coverage": 0.0}
            categories[category]["required"] += 1
            if skill in matched_set or skill in resume_set:
                categories[category]["matched"] += 1
            else:
                categories[category]["missing"] += 1

        for data in categories.values():
            if data["required"]:
                data["coverage"] = round((data["matched"] / data["required"]) * 100, 2)
        return categories

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze_skills(self, resume_skills: Any, jd_skills: Any, jd_text: str = "") -> Dict[str, Any]:
        resume = self.normalize_skills(resume_skills)
        jd = self.normalize_skills(jd_skills)
        resume_set, jd_set = set(resume), set(jd)

        exact_matches = sorted(resume_set.intersection(jd_set))
        remaining_resume = [s for s in resume if s not in exact_matches]
        remaining_jd = [s for s in jd if s not in exact_matches]
        semantic_matches = self.semantic_match_skills(remaining_resume, remaining_jd)

        semantic_jd = {self.clean_skill(m["jd_skill"]) for m in semantic_matches}
        matched_jd = set(exact_matches).union(semantic_jd)
        missing = sorted(jd_set - matched_jd)

        match_details = []
        for skill in exact_matches:
            match_details.append({
                "jd_skill": skill, "resume_skill": skill, "score": 1.0,
                "type": "exact", "priority": self.get_skill_priority(skill, jd_text),
                "supported_by_resume": True
            })
        for m in semantic_matches:
            match_details.append({
                **m, "priority": self.get_skill_priority(m["jd_skill"], jd_text),
                "supported_by_resume": True
            })

        missing_details = []
        for skill in missing:
            missing_details.append({
                "skill": skill, "priority": self.get_skill_priority(skill, jd_text),
                "category": self.get_skill_category(skill), "supported_by_resume": False
            })

        total_jd = len(jd_set)
        matched_count = len(matched_jd)
        compatibility = round((matched_count / total_jd) * 100, 2) if total_jd else 0.0

        categories = self.calculate_category_coverage(resume, jd, matched_jd)

        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        match_details.sort(key=lambda x: (priority_order.get(x.get("priority", "Low"), 4), -float(x.get("score", 0)), x.get("jd_skill", "")))

        return {
            "resume_skills": resume, "jd_skills": jd,
            "exact_matches": exact_matches, "semantic_matches": semantic_matches,
            "matched_skills": sorted(matched_jd), "missing_skills": missing,
            "missing_details": missing_details, "match_details": match_details,
            "total_jd_skills": total_jd, "matched_count": matched_count,
            "missing_count": len(missing), "compatibility_score": compatibility,
            "category_coverage": categories,
            "safety_rule": "Missing JD skills are never added to candidate skills."
        }

    def complete_analysis(self, resume_skills: Any, jd_skills: Any, jd_text: str = "") -> Dict[str, Any]:
        analysis = self.analyze_skills(resume_skills, jd_skills, jd_text)
        analysis["summary"] = f"Resume supports {analysis['matched_count']} of {analysis['total_jd_skills']} JD skills ({analysis['compatibility_score']:.1f}%). {analysis['missing_count']} skills are missing."
        analysis["skill_breakdown"] = {
            "matched": analysis["matched_skills"],
            "missing": analysis["missing_skills"],
            "critical_missing": [d["skill"] for d in analysis["missing_details"] if d.get("priority") == "Critical"],
            "high_priority_missing": [d["skill"] for d in analysis["missing_details"] if d.get("priority") == "High"],
            "medium_priority_missing": [d["skill"] for d in analysis["missing_details"] if d.get("priority") == "Medium"]
        }
        analysis["recommendations"] = self._generate_recommendations(analysis)
        return analysis

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        recs = []
        missing_details = analysis.get("missing_details", [])
        critical = [d["skill"] for d in missing_details if d.get("priority") == "Critical"]
        high = [d["skill"] for d in missing_details if d.get("priority") == "High"]
        medium = [d["skill"] for d in missing_details if d.get("priority") == "Medium"]

        if critical:
            recs.append(f"Critical JD skills missing: {', '.join(critical)}. Do not add without verified evidence.")
        if high:
            recs.append(f"High-priority JD skills missing: {', '.join(high)}. Add only with verified evidence.")
        if medium:
            recs.append(f"Medium-priority JD skills missing: {', '.join(medium)}. Consider as future learning targets.")
        if analysis.get("matched_skills"):
            recs.append("Prioritize matched skills when tailoring the resume.")
        if not recs:
            recs.append("No major skill-gap recommendation was generated.")
        return recs


# ============================================================
# BACKWARD-COMPATIBLE FUNCTION
# ============================================================

def analyze_skill_gap(resume_skills: Any, jd_skills: Any, jd_text: str = "", similarity_threshold: float = 0.72) -> Dict[str, Any]:
    analyzer = GapAnalyzer(similarity_threshold=similarity_threshold, use_embeddings=True)
    return analyzer.complete_analysis(resume_skills, jd_skills, jd_text)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    analyzer = GapAnalyzer()
    result = analyzer.complete_analysis(
        ["Python", "SQL", "Pandas", "Power BI", "Machine Learning"],
        ["Python", "SQL", "Pandas", "Power BI", "Machine Learning", "Docker", "RAG"],
        "Required: Python, SQL, Machine Learning. Preferred: Power BI, Docker. Nice to have: RAG."
    )
    print("\n" + "=" * 60)
    print("GAP ANALYZER TEST")
    print("=" * 60)
    print("Summary:", result["summary"])
    print("Matched:", result["matched_skills"])
    print("Missing:", result["missing_skills"])
    print("Recommendations:", result["recommendations"])
    print("=" * 60)
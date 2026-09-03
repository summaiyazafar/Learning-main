"""
============================================================
AI RESUME TAILORING SYSTEM
============================================================

File:
    ml_feature_engineering.py

Purpose:
    Convert Resume + Job Description information into
    numerical ML features for resume-job matching.

Features:
    1. Skill Match (overlap of extracted skills)
    2. Semantic Similarity
    3. Keyword Overlap
    4. Critical Skill Coverage
    5. Preferred Skill Coverage
    6. Experience Match
    7. Education Match
    8. Resume Length (normalized)
    9. Job Description Length (normalized)

Designed for:
    - Logistic Regression
    - Decision Tree
    - Random Forest
    - XGBoost
    - Gradient Boosting

Integration:
    - Uses skill_extractor's alias dictionary for consistency.
    - Can build features directly from matcher.MatchResult.
    - Provides a numpy array ready for scikit-learn models.
"""

from __future__ import annotations

import re
import numpy as np
from typing import Any, Dict, List, Optional, Set, Union

# Import aliases from skill_extractor to keep consistency
try:
    from modules.skill_extractor import ALIASES as SKILL_ALIASES
except ImportError:
    # Fallback local aliases if skill_extractor is not available
    SKILL_ALIASES = {
        "py": "python",
        "powerbi": "power bi",
        "power-bi": "power bi",
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "tf": "tensorflow",
        "opencv-python": "opencv",
        "gen ai": "generative ai",
        "genai": "generative ai",
        "llms": "llm",
        "nodejs": "node.js",
        "node js": "node.js",
        "postgres": "postgresql",
        "retrieval-augmented generation": "retrieval augmented generation",
        "ai agent": "ai agents"
    }

# ============================================================
# TEXT & SKILL NORMALIZATION
# ============================================================

def normalize_text(text: Any) -> str:
    """
    Clean and normalize text: lowercasing, strip, collapse whitespace.
    """
    if text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_text(text: Any) -> Set[str]:
    """
    Convert text into a set of normalized tokens.
    Keeps technical terms like c++, c#, python, power-bi, node.js.
    """
    text = normalize_text(text)
    if not text:
        return set()
    # Allow letters, digits, +, #, ., -
    pattern = r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b"
    return set(re.findall(pattern, text))


def normalize_skill(skill: Any) -> str:
    """
    Normalize a single skill name, using the shared alias dictionary.
    """
    if skill is None:
        return ""
    skill = normalize_text(skill)
    skill = skill.replace("&", "and")
    skill = re.sub(r"\s+", " ", skill)
    return SKILL_ALIASES.get(skill, skill)


def normalize_skill_list(skills: Any) -> List[str]:
    """
    Convert any input to a normalized list of unique skills.
    """
    if skills is None:
        return []
    if isinstance(skills, str):
        # split by comma, semicolon, or newline
        parts = re.split(r"[,;|\n]+", skills)
    elif isinstance(skills, (list, tuple, set)):
        parts = list(skills)
    else:
        parts = [str(skills)]
    result = []
    seen = set()
    for p in parts:
        norm = normalize_skill(p)
        if norm and norm not in seen:
            seen.add(norm)
            result.append(norm)
    return result


# ============================================================
# CORE FEATURE FUNCTIONS
# ============================================================

def keyword_overlap(resume_text: str, jd_text: str) -> float:
    """
    Jaccard-like overlap: |tokens(resume) ∩ tokens(jd)| / |tokens(jd)|.
    """
    resume_words = tokenize_text(resume_text)
    jd_words = tokenize_text(jd_text)
    if not jd_words:
        return 0.0
    overlap = resume_words.intersection(jd_words)
    return len(overlap) / len(jd_words)


def skill_overlap(resume_skills: Any, jd_skills: Any) -> float:
    """
    Percentage of JD skills that appear in resume skills.
    """
    resume_set = set(normalize_skill_list(resume_skills))
    jd_set = set(normalize_skill_list(jd_skills))
    if not jd_set:
        return 0.0
    matched = resume_set.intersection(jd_set)
    return len(matched) / len(jd_set)


def critical_skill_coverage(resume_skills: Any, critical_skills: Any) -> float:
    """
    Coverage of critical (required) skills.
    """
    resume_set = set(normalize_skill_list(resume_skills))
    critical_set = set(normalize_skill_list(critical_skills))
    if not critical_set:
        return 1.0
    matched = resume_set.intersection(critical_set)
    return len(matched) / len(critical_set)


def preferred_skill_coverage(resume_skills: Any, preferred_skills: Any) -> float:
    """
    Coverage of preferred / nice‑to‑have skills.
    """
    resume_set = set(normalize_skill_list(resume_skills))
    preferred_set = set(normalize_skill_list(preferred_skills))
    if not preferred_set:
        return 1.0
    matched = resume_set.intersection(preferred_set)
    return len(matched) / len(preferred_set)


def experience_match(resume_experience: Any, required_experience: Any) -> float:
    """
    Ratio of candidate experience to required experience, capped at 1.0.
    """
    try:
        resume_exp = float(resume_experience or 0)
    except (ValueError, TypeError):
        resume_exp = 0.0
    try:
        required_exp = float(required_experience or 0)
    except (ValueError, TypeError):
        required_exp = 0.0
    if required_exp <= 0:
        return 1.0
    return min(resume_exp / required_exp, 1.0)


def education_match(resume_text: str, jd_text: str) -> float:
    """
    Estimate education compatibility via presence of education-related terms.
    """
    resume = normalize_text(resume_text)
    jd = normalize_text(jd_text)
    education_terms = [
        "bachelor", "master", "phd", "computer science",
        "software engineering", "information technology",
        "data science", "artificial intelligence",
        "engineering", "bs", "ms"
    ]
    resume_terms = set()
    jd_terms = set()
    for term in education_terms:
        if term in resume:
            resume_terms.add(term)
        if term in jd:
            jd_terms.add(term)
    if not jd_terms:
        return 1.0
    matched = resume_terms.intersection(jd_terms)
    return len(matched) / len(jd_terms)


def length_score(text: str, max_len: int = 10000) -> float:
    """
    Normalize text length by a maximum (default 10000 characters).
    """
    length = len(normalize_text(text))
    return min(length / max_len, 1.0)


# ============================================================
# FEATURE VECTOR BUILDER
# ============================================================

FEATURE_NAMES: List[str] = [
    "skill_match",
    "semantic_similarity",
    "keyword_overlap",
    "critical_skill_coverage",
    "preferred_skill_coverage",
    "experience_match",
    "education_match",
    "resume_length",
    "jd_length"
]


def create_feature_vector(
    resume_text: str,
    jd_text: str,
    resume_skills: Any,
    jd_skills: Any,
    semantic_score: Union[float, str],
    resume_experience: Any = 0,
    required_experience: Any = 0,
    critical_skills: Any = None,
    preferred_skills: Any = None
) -> Dict[str, float]:
    """
    Create a dictionary of all ML features.

    Parameters
    ----------
    resume_text : str
        Full resume text.
    jd_text : str
        Full job description text.
    resume_skills : list, set, tuple, or string
        Candidate skills (extracted).
    jd_skills : list, set, tuple, or string
        JD skills (extracted).
    semantic_score : float or str
        Semantic similarity (0-1 or 0-100).
    resume_experience : numeric, optional
        Candidate years of experience.
    required_experience : numeric, optional
        Years required by JD.
    critical_skills : optional
        List of critical/required JD skills.
    preferred_skills : optional
        List of preferred/nice‑to‑have JD skills.

    Returns
    -------
    dict
        Feature name -> float (0-1)
    """
    # Normalize semantic score to 0-1
    try:
        sem = float(semantic_score)
    except (ValueError, TypeError):
        sem = 0.0
    if sem > 1.0:
        sem = sem / 100.0
    sem = max(0.0, min(sem, 1.0))

    resume_skills_norm = normalize_skill_list(resume_skills)
    jd_skills_norm = normalize_skill_list(jd_skills)
    critical = normalize_skill_list(critical_skills or [])
    preferred = normalize_skill_list(preferred_skills or [])

    features = {
        "skill_match": skill_overlap(resume_skills_norm, jd_skills_norm),
        "semantic_similarity": sem,
        "keyword_overlap": keyword_overlap(resume_text, jd_text),
        "critical_skill_coverage": critical_skill_coverage(resume_skills_norm, critical),
        "preferred_skill_coverage": preferred_skill_coverage(resume_skills_norm, preferred),
        "experience_match": experience_match(resume_experience, required_experience),
        "education_match": education_match(resume_text, jd_text),
        "resume_length": length_score(resume_text),
        "jd_length": length_score(jd_text)
    }
    return features


def features_to_array(features: Dict[str, float]) -> np.ndarray:
    """
    Convert feature dictionary to a 2D numpy array (1 sample x N features).
    Feature order is determined by FEATURE_NAMES.
    """
    values = []
    for name in FEATURE_NAMES:
        val = float(features.get(name, 0.0))
        val = max(0.0, min(val, 1.0))
        values.append(val)
    return np.array(values, dtype=float).reshape(1, -1)


def feature_summary(features: Dict[str, float]) -> Dict[str, float]:
    """
    Convert feature values to percentage (0-100) for display.
    """
    return {name: round(features.get(name, 0.0) * 100, 2) for name in FEATURE_NAMES}


# ============================================================
# WEAK SUPERVISION LABEL
# ============================================================

def create_training_label(features: Dict[str, float]) -> int:
    """
    Generate a heuristic label (0 or 1) for weak supervision.
    Useful when no human-labelled data is available.
    """
    weights = {
        "skill_match": 0.25,
        "semantic_similarity": 0.25,
        "keyword_overlap": 0.10,
        "critical_skill_coverage": 0.15,
        "preferred_skill_coverage": 0.05,
        "experience_match": 0.10,
        "education_match": 0.10
    }
    score = 0.0
    for name, w in weights.items():
        score += w * features.get(name, 0.0)
    return 1 if score >= 0.50 else 0


# ============================================================
# CONVENIENCE FUNCTION FOR MATCHER OUTPUT
# ============================================================

def create_feature_vector_from_matcher_result(
    match_result: Dict[str, Any],
    semantic_score: Optional[float] = None
) -> Dict[str, float]:
    """
    Build feature vector directly from the output of ResumeJobMatcher.match().

    Parameters
    ----------
    match_result : dict
        The result dictionary returned by matcher.match().
    semantic_score : float, optional
        If provided, overrides the semantic score from match_result.

    Returns
    -------
    dict
        Feature vector ready for ML.
    """
    resume_text = match_result.get("resume_text", "")
    job_text = match_result.get("job_text", "")
    resume_skills = match_result.get("resume_skills", [])
    jd_skills = match_result.get("all_jd_skills", [])
    required_skills = match_result.get("required_skills", [])
    preferred_skills = match_result.get("preferred_skills", [])
    exp_required = match_result.get("experience_required", 0)

    # Experience from resume is not directly in matcher result;
    # we can estimate from "resume_text" or use a default 0.
    # For now, we set resume_experience = 0 if not available.
    resume_experience = 0

    if semantic_score is None:
        semantic_score = match_result.get("semantic_score", 0.0)

    return create_feature_vector(
        resume_text=resume_text,
        jd_text=job_text,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        semantic_score=semantic_score,
        resume_experience=resume_experience,
        required_experience=exp_required,
        critical_skills=required_skills,
        preferred_skills=preferred_skills
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ML FEATURE ENGINEERING TEST")
    print("=" * 70)

    # Sample data
    resume_text = """
    Python developer with machine learning experience.

    Experienced with Pandas, NumPy, SQL,
    Scikit-learn and Power BI.

    Developed predictive machine learning models
    and data-driven applications.
    """

    jd_text = """
    Machine Learning Engineer required with Python,
    machine learning, SQL, Pandas, NumPy and TensorFlow.

    Candidate should develop machine learning models
    and analyze datasets.
    """

    resume_skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "Scikit-learn", "Power BI"]
    jd_skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "TensorFlow"]
    critical = ["Python", "Machine Learning", "SQL"]
    preferred = ["TensorFlow", "Power BI"]

    features = create_feature_vector(
        resume_text=resume_text,
        jd_text=jd_text,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        semantic_score=0.78,
        resume_experience=2,
        required_experience=2,
        critical_skills=critical,
        preferred_skills=preferred
    )

    print("\nFEATURES")
    for k, v in features.items():
        print(f"{k:30s}: {v:.4f}")

    vector = features_to_array(features)
    print("\nFEATURE VECTOR (numpy array):")
    print(vector)
    print(f"Shape: {vector.shape}")

    summary = feature_summary(features)
    print("\nFEATURE SUMMARY (%)")
    for k, v in summary.items():
        print(f"{k:30s}: {v:.2f}%")

    label = create_training_label(features)
    print(f"\nWEAK SUPERVISION LABEL: {label}")

    print("\n" + "=" * 70)
    print("TEST COMPLETED")
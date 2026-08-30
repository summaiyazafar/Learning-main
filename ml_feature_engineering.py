```python
"""
ML Feature Engineering
AI Resume Tailoring System

Creates numerical features from:
- Resume
- Job Description
- Skills
- Experience
- Education
- Semantic similarity

These features are used by ML models such as:
Random Forest
XGBoost
Decision Tree
Logistic Regression
"""

import re
import numpy as np


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Convert text into a clean lowercase string.
    """

    if text is None:
        return ""

    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# KEYWORD OVERLAP
# ============================================================

def extract_words(text):
    """
    Extract useful words from text.
    """

    text = normalize_text(text)

    return set(
        re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b",
            text
        )
    )


def keyword_overlap(resume_text, jd_text):
    """
    Calculate keyword overlap between resume and job description.

    Returns value between 0 and 1.
    """

    resume_words = extract_words(resume_text)
    jd_words = extract_words(jd_text)

    if not jd_words:
        return 0.0

    common_words = resume_words.intersection(jd_words)

    return len(common_words) / len(jd_words)


# ============================================================
# SKILL OVERLAP
# ============================================================

def clean_skill_list(skills):
    """
    Convert skills into normalized list.
    """

    if skills is None:
        return []

    if isinstance(skills, str):

        # Support comma-separated skills
        skills = skills.split(",")

    cleaned = []

    for skill in skills:

        skill = normalize_text(skill)

        if skill:
            cleaned.append(skill)

    return cleaned


def skill_overlap(resume_skills, jd_skills):
    """
    Calculate percentage of required JD skills
    found in the resume.
    """

    resume_set = set(
        clean_skill_list(resume_skills)
    )

    jd_set = set(
        clean_skill_list(jd_skills)
    )

    if not jd_set:
        return 0.0

    matched = resume_set.intersection(jd_set)

    return len(matched) / len(jd_set)


# ============================================================
# EXPERIENCE MATCH
# ============================================================

def experience_match(
    resume_experience,
    required_experience
):
    """
    Compare resume experience with required experience.

    Example:

    Resume = 2 years
    Required = 2 years

    Result = 1.0

    Resume = 2 year
    Required = 3 years

    Result = 0.5
    """

    try:
        resume_exp = float(
            resume_experience or 0
        )
    except Exception:
        resume_exp = 0.0

    try:
        required_exp = float(
            required_experience or 0
        )
    except Exception:
        required_exp = 0.0

    if required_exp <= 0:
        return 1.0

    score = resume_exp / required_exp

    return min(max(score, 0.0), 1.0)


# ============================================================
# EDUCATION MATCH
# ============================================================

def education_match(
    resume_text,
    jd_text
):
    """
    Estimate education compatibility.

    Education is NOT modified by this module.
    It is only used as a matching feature.
    """

    resume = normalize_text(resume_text)
    jd = normalize_text(jd_text)

    education_terms = [

        "bachelor",
        "master",
        "bs",
        "ms",
        "phd",

        "computer science",
        "software engineering",
        "information technology",
        "information systems",
        "data science",
        "artificial intelligence",
        "engineering",

        "computer engineering"
    ]

    resume_terms = {
        term
        for term in education_terms
        if term in resume
    }

    jd_terms = {
        term
        for term in education_terms
        if term in jd
    }

    # JD does not mention education
    if not jd_terms:
        return 1.0

    matched = resume_terms.intersection(
        jd_terms
    )

    return len(matched) / len(jd_terms)


# ============================================================
# RESUME LENGTH FEATURE
# ============================================================

def length_score(text):
    """
    Normalize document length between 0 and 1.
    """

    text = normalize_text(text)

    length = len(text)

    return min(
        length / 10000.0,
        1.0
    )


# ============================================================
# COMPLETE FEATURE VECTOR
# ============================================================

def create_feature_vector(
    resume_text,
    jd_text,
    resume_skills,
    jd_skills,
    semantic_score,
    resume_experience=0,
    required_experience=0
):
    """
    Create all ML features.

    Features:

    1. skill_match
    2. semantic_similarity
    3. keyword_overlap
    4. experience_match
    5. education_match
    6. resume_length
    7. jd_length
    """

    try:
        semantic_score = float(
            semantic_score
        )
    except Exception:
        semantic_score = 0.0

    # Keep semantic score between 0 and 1
    semantic_score = min(
        max(semantic_score, 0.0),
        1.0
    )

    features = {

        "skill_match":
            skill_overlap(
                resume_skills,
                jd_skills
            ),

        "semantic_similarity":
            semantic_score,

        "keyword_overlap":
            keyword_overlap(
                resume_text,
                jd_text
            ),

        "experience_match":
            experience_match(
                resume_experience,
                required_experience
            ),

        "education_match":
            education_match(
                resume_text,
                jd_text
            ),

        "resume_length":
            length_score(
                resume_text
            ),

        "jd_length":
            length_score(
                jd_text
            )
    }

    return features


# ============================================================
# FEATURES TO NUMPY ARRAY
# ============================================================

FEATURE_NAMES = [

    "skill_match",

    "semantic_similarity",

    "keyword_overlap",

    "experience_match",

    "education_match",

    "resume_length",

    "jd_length"
]


def features_to_array(features):
    """
    Convert feature dictionary into
    NumPy array for ML models.
    """

    values = []

    for feature_name in FEATURE_NAMES:

        value = features.get(
            feature_name,
            0.0
        )

        try:
            value = float(value)
        except Exception:
            value = 0.0

        values.append(value)

    return np.array(
        values,
        dtype=float
    ).reshape(1, -1)


# ============================================================
# WEAK SUPERVISION LABEL
# ============================================================

def create_training_label(features):
    """
    Create a training label when a dataset
    does not contain human-labelled
    resume-job matching results.

    1 = Good Match
    0 = Poor Match

    IMPORTANT:
    This label is used only for creating
    an initial training dataset.
    """

    skill_score = float(
        features.get(
            "skill_match",
            0.0
        )
    )

    semantic_score = float(
        features.get(
            "semantic_similarity",
            0.0
        )
    )

    keyword_score = float(
        features.get(
            "keyword_overlap",
            0.0
        )
    )

    experience_score = float(
        features.get(
            "experience_match",
            0.0
        )
    )

    education_score = float(
        features.get(
            "education_match",
            0.0
        )
    )

    # Weighted ML target
    score = (

        0.35 * skill_score

        + 0.30 * semantic_score

        + 0.15 * keyword_score

        + 0.10 * experience_score

        + 0.10 * education_score
    )

    return int(score >= 0.50)


# ============================================================
# COMPLETE FEATURE + LABEL
# ============================================================

def create_training_sample(
    resume_text,
    jd_text,
    resume_skills,
    jd_skills,
    semantic_score,
    resume_experience=0,
    required_experience=0
):
    """
    Create one complete training sample.
    """

    features = create_feature_vector(

        resume_text=resume_text,

        jd_text=jd_text,

        resume_skills=resume_skills,

        jd_skills=jd_skills,

        semantic_score=semantic_score,

        resume_experience=resume_experience,

        required_experience=required_experience
    )

    label = create_training_label(
        features
    )

    return features, label


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ML FEATURE ENGINEERING TEST")
    print("=" * 60)

    resume_text = """
    Machine Learning Engineer with Python,
    SQL, Pandas, NumPy and Scikit-learn.
    Developed machine learning models
    for predictive analytics.
    """

    jd_text = """
    We are looking for a Machine Learning Engineer
    with Python, SQL, Pandas, NumPy,
    Scikit-learn and TensorFlow experience.
    """

    resume_skills = [

        "Python",
        "Machine Learning",
        "SQL",
        "Pandas",
        "NumPy",
        "Scikit-learn"
    ]

    jd_skills = [

        "Python",
        "Machine Learning",
        "SQL",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow"
    ]

    semantic_score = 0.82

    resume_experience = 2

    required_experience = 2


    # --------------------------------------------------------
    # CREATE FEATURES
    # --------------------------------------------------------

    features = create_feature_vector(

        resume_text=resume_text,

        jd_text=jd_text,

        resume_skills=resume_skills,

        jd_skills=jd_skills,

        semantic_score=semantic_score,

        resume_experience=resume_experience,

        required_experience=required_experience
    )


    # --------------------------------------------------------
    # DISPLAY FEATURES
    # --------------------------------------------------------

    print("\nFEATURES")
    print("-" * 60)

    for name, value in features.items():

        print(
            f"{name:25} : {value:.4f}"
        )


    # --------------------------------------------------------
    # NUMPY VECTOR
    # --------------------------------------------------------

    vector = features_to_array(
        features
    )

    print("\nFEATURE VECTOR")
    print("-" * 60)

    print(vector)


    # --------------------------------------------------------
    # TRAINING LABEL
    # --------------------------------------------------------

    label = create_training_label(
        features
    )

    print("\nTRAINING LABEL")
    print("-" * 60)

    print(
        f"Label: {label}"
    )

    if label == 1:

        print(
            "Meaning: GOOD MATCH"
        )

    else:

        print(
            "Meaning: POOR MATCH"
        )


    print("\n" + "=" * 60)
    print("ML FEATURE ENGINEERING TEST COMPLETED")
    print("=" * 60)
```

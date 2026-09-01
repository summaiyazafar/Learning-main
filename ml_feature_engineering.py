import re
import numpy as np


def normalize_text(text):
    """Clean and normalize text."""
    if text is None:
        return ""

    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize_text(text):
    """Convert text into a set of normalized words."""
    text = normalize_text(text)

    if not text:
        return set()

    pattern = r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b"

    return set(re.findall(pattern, text))


def keyword_overlap(resume_text, jd_text):
    """Calculate keyword overlap between resume and job description."""

    resume_words = tokenize_text(resume_text)
    jd_words = tokenize_text(jd_text)

    if not jd_words:
        return 0.0

    overlap = resume_words.intersection(jd_words)

    return len(overlap) / len(jd_words)


def skill_overlap(resume_skills, jd_skills):
    """Calculate percentage of required JD skills found in resume."""

    resume_set = {
        normalize_text(skill)
        for skill in (resume_skills or [])
        if normalize_text(skill)
    }

    jd_set = {
        normalize_text(skill)
        for skill in (jd_skills or [])
        if normalize_text(skill)
    }

    if not jd_set:
        return 0.0

    matched = resume_set.intersection(jd_set)

    return len(matched) / len(jd_set)


def experience_match(resume_experience, required_experience):
    """
    Compare resume experience with required experience.

    Returns a value between 0 and 1.
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


def education_match(resume_text, jd_text):
    """Estimate education compatibility."""

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
        "data science",
        "artificial intelligence",
        "engineering"
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

    if not jd_terms:
        return 1.0

    matched = resume_terms.intersection(jd_terms)

    return len(matched) / len(jd_terms)


def resume_length_score(resume_text):
    """Normalize resume length."""

    length = len(normalize_text(resume_text))

    return min(length / 10000.0, 1.0)


def jd_length_score(jd_text):
    """Normalize job description length."""

    length = len(normalize_text(jd_text))

    return min(length / 10000.0, 1.0)


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
    Create ML features for resume-job matching.

    These features will later be used by ML models such as:

    - Logistic Regression
    - Decision Tree
    - Random Forest
    - XGBoost
    """

    try:
        semantic_score = float(semantic_score)
    except (ValueError, TypeError):
        semantic_score = 0.0

    semantic_score = max(0.0, min(semantic_score, 1.0))

    features = {
        "skill_match": skill_overlap(
            resume_skills,
            jd_skills
        ),

        "semantic_similarity": semantic_score,

        "keyword_overlap": keyword_overlap(
            resume_text,
            jd_text
        ),

        "experience_match": experience_match(
            resume_experience,
            required_experience
        ),

        "education_match": education_match(
            resume_text,
            jd_text
        ),

        "resume_length": resume_length_score(
            resume_text
        ),

        "jd_length": jd_length_score(
            jd_text
        )
    }

    return features


def features_to_array(features):
    """
    Convert feature dictionary into NumPy array.

    Feature order MUST remain the same during
    training and prediction.
    """

    feature_names = [
        "skill_match",
        "semantic_similarity",
        "keyword_overlap",
        "experience_match",
        "education_match",
        "resume_length",
        "jd_length"
    ]

    values = []

    for name in feature_names:
        try:
            value = float(features.get(name, 0.0))
        except (ValueError, TypeError):
            value = 0.0

        values.append(value)

    return np.array(
        values,
        dtype=float
    ).reshape(1, -1)


def create_training_label(features):
    """
    Create a weak-supervision label.

    1 = good resume-job match
    0 = poor resume-job match

    This is useful when the available dataset does not
    contain human-labelled resume/JD match pairs.
    """

    skill_score = float(
        features.get("skill_match", 0.0)
    )

    semantic_score = float(
        features.get("semantic_similarity", 0.0)
    )

    keyword_score = float(
        features.get("keyword_overlap", 0.0)
    )

    experience_score = float(
        features.get("experience_match", 0.0)
    )

    education_score = float(
        features.get("education_match", 0.0)
    )

    score = (
        0.35 * skill_score
        + 0.30 * semantic_score
        + 0.15 * keyword_score
        + 0.10 * experience_score
        + 0.10 * education_score
    )

    return int(score >= 0.50)


if __name__ == "__main__":

    print("=" * 60)
    print("ML FEATURE ENGINEERING TEST")
    print("=" * 60)

    resume_text = """
    Python developer with machine learning experience.
    Experienced with Pandas, NumPy, SQL and Scikit-learn.
    """

    jd_text = """
    Machine Learning Engineer required with Python,
    machine learning, SQL, Pandas, NumPy and TensorFlow.
    """

    resume_skills = [
        "Python",
        "Machine Learning",
        "Pandas",
        "NumPy",
        "SQL",
        "Scikit-learn"
    ]

    jd_skills = [
        "Python",
        "Machine Learning",
        "Pandas",
        "NumPy",
        "SQL",
        "TensorFlow"
    ]

    features = create_feature_vector(
        resume_text=resume_text,
        jd_text=jd_text,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        semantic_score=0.78,
        resume_experience=2,
        required_experience=2
    )

    print("\nFeatures:")

    for name, value in features.items():
        print(f"{name}: {value:.4f}")

    print("\nFeature Vector:")

    vector = features_to_array(features)

    print(vector)

    print("\nTraining Label:")

    label = create_training_label(features)

    print(label)

    print("\n" + "=" * 60)
    print("ML FEATURE ENGINEERING TEST COMPLETED")
    print("=" * 60)
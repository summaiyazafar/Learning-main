"""
============================================================
AI RESUME TAILORING SYSTEM
============================================================

File:
    ranking_engine.py

Purpose:
    ATS Ranking Engine that combines skill, semantic,
    experience, education, and keyword matching into a
    weighted final score.

Components:
    - Skill matching   (weight: 40%)
    - Semantic         (weight: 30%)
    - Experience       (weight: 15%)
    - Education        (weight: 10%)
    - Keyword          (weight: 5%)

Produces:
    - Component scores (0-100)
    - Weighted ATS score
    - Match level
    - Score breakdown
    - Actionable recommendations

IMPORTANT:
    This module ONLY calculates scores.
    It does NOT add missing skills to the candidate resume.
"""

import re
import math
from typing import Any, Dict, List, Optional, Set, Tuple

# Optionally import skill extractor for consistent normalization
try:
    from modules.skill_extractor import normalize_skill
except ImportError:
    # Fallback – define a simple normalizer if skill_extractor not available
    def normalize_skill(skill: Any) -> str:
        if skill is None:
            return ""
        return str(skill).strip().lower()


# ============================================================
# RANKING ENGINE
# ============================================================

class RankingEngine:
    """
    Professional ATS Ranking Engine.

    All component scores are normalized to 0-100.
    Weights are configurable at initialization.
    """

    # Stop words to exclude from keyword matching
    STOP_WORDS: Set[str] = {
        "the", "and", "for", "with", "you", "your", "our",
        "are", "this", "that", "from", "will", "have", "has",
        "into", "their", "they", "them", "than", "then",
        "about", "using", "used", "work", "working", "role",
        "job", "candidate", "required", "requirements",
        "responsibilities", "skills", "experience", "years",
        "ability", "strong", "good", "excellent"
    }

    # Education level hierarchy
    EDUCATION_HIERARCHY: Dict[str, int] = {
        "phd": 5,
        "master": 4,
        "bachelor": 3,
        "intermediate": 2,
        "diploma": 1,
    }

    # Education detection patterns (with word boundaries)
    EDUCATION_PATTERNS: Dict[str, List[str]] = {
        "phd": [
            r"\bph\.?d\.?\b",
            r"\bdoctorate\b",
            r"\bdoctoral\b",
        ],
        "master": [
            r"\bmaster(?:'s)?\b",
            r"\bms\b",
            r"\bm\.s\.?\b",
            r"\bmsc\b",
            r"\bm\.sc\.?\b",
            r"\bmba\b",
            r"\bm\.b\.a\.?\b",
        ],
        "bachelor": [
            r"\bbachelor(?:'s)?\b",
            r"\bbs\b",
            r"\bb\.s\.?\b",
            r"\bbsc\b",
            r"\bb\.sc\.?\b",
            r"\bba\b",
            r"\bb\.a\.?\b",
            r"\bbba\b",
        ],
        "intermediate": [
            r"\bintermediate\b",
            r"\bfsc\b",
            r"\bf\.sc\.?\b",
            r"\bics\b",
            r"\bi\.c\.s\.?\b",
        ],
        "diploma": [
            r"\bdiploma\b",
            r"\bassociate(?:'s)?\b",
            r"\bassociate degree\b",
        ],
    }

    def __init__(
        self,
        skill_weight: float = 0.40,
        semantic_weight: float = 0.30,
        experience_weight: float = 0.15,
        education_weight: float = 0.10,
        keyword_weight: float = 0.05,
    ) -> None:
        """
        Initialize ATS scoring weights.

        Default:
            Skill       = 40%
            Semantic    = 30%
            Experience  = 15%
            Education   = 10%
            Keyword     =  5%
        Total = 100%

        Parameters
        ----------
        skill_weight : float, optional
            Weight for skill matching score.
        semantic_weight : float, optional
            Weight for semantic similarity score.
        experience_weight : float, optional
            Weight for experience matching score.
        education_weight : float, optional
            Weight for education matching score.
        keyword_weight : float, optional
            Weight for keyword overlap score.

        Raises
        ------
        ValueError
            If weights are negative or do not sum to 1.0.
        """
        self.skill_weight = skill_weight
        self.semantic_weight = semantic_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight
        self.keyword_weight = keyword_weight
        self._validate_weights()

    # ============================================================
    # WEIGHT VALIDATION
    # ============================================================

    def _validate_weights(self) -> None:
        """Validate that all weights are non-negative and sum to 1.0."""
        weights = [
            self.skill_weight,
            self.semantic_weight,
            self.experience_weight,
            self.education_weight,
            self.keyword_weight,
        ]
        if any(w < 0 for w in weights):
            raise ValueError("ATS weights cannot be negative.")
        total = sum(weights)
        if not math.isclose(total, 1.0, abs_tol=1e-6):
            raise ValueError(
                f"ATS weights must sum to 1.0. Current total: {total:.4f}"
            )

    # ============================================================
    # SCORE NORMALIZATION
    # ============================================================

    @staticmethod
    def normalize_score(score: Any) -> float:
        """
        Normalize any input to a 0-100 score.

        Supports:
            - 0.0 – 1.0   (treated as fraction)
            - 0 – 100     (treated as percentage)

        Examples:
            0.75  → 75.0
            75.0  → 75.0
            120   → 100.0 (capped)
            -10   → 0.0   (floor)
        """
        try:
            score = float(score)
        except (TypeError, ValueError):
            return 0.0

        if 0.0 <= score <= 1.0:
            score *= 100.0

        return round(max(0.0, min(score, 100.0)), 2)

    # ============================================================
    # EXPERIENCE EXTRACTION
    # ============================================================

    @staticmethod
    def extract_years(text: Any) -> float:
        """
        Extract years of experience from text.

        Examples:
            "3 years experience" → 3.0
            "2+ years"           → 2.0
            "1.5 years"          → 1.5
            "5 yrs"              → 5.0

        Returns the maximum detected value (most conservative for JD requirements).
        """
        if not text:
            return 0.0

        text = str(text).lower()
        patterns = [
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
            r"(\d+(?:\.\d+)?)\s*\+?\s*yrs?",
        ]
        matches: List[float] = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            for val in found:
                try:
                    matches.append(float(val))
                except ValueError:
                    continue

        return max(matches) if matches else 0.0

    # ============================================================
    # EXPERIENCE SCORE
    # ============================================================

    def experience_score(self, resume_text: Any, job_text: Any) -> float:
        """
        Calculate experience compatibility (0-100).

        Logic:
            - No job requirement → 100
            - Candidate meets or exceeds requirement → 100
            - Partial experience → proportional score
            - No experience → 0
        """
        resume_years = self.extract_years(resume_text)
        job_years = self.extract_years(job_text)

        if job_years <= 0:
            return 100.0
        if resume_years >= job_years:
            return 100.0
        if resume_years > 0:
            score = (resume_years / job_years) * 100
            return round(min(score, 100.0), 2)
        return 0.0

    # ============================================================
    # EDUCATION EXTRACTION
    # ============================================================

    @classmethod
    def extract_education_levels(cls, text: Any) -> List[str]:
        """
        Extract education levels from text using word-boundary patterns.

        Returns a list of level names (e.g., ["bachelor", "master"]).
        """
        if not text:
            return []
        text = str(text).lower()
        found: List[str] = []
        for level, patterns in cls.EDUCATION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    found.append(level)
                    break  # one match per level is enough
        return found

    # ============================================================
    # EDUCATION SCORE
    # ============================================================

    def education_score(self, resume_text: Any, job_text: Any) -> float:
        """
        Estimate education compatibility (0-100).

        Hierarchy:
            PhD          = 5
            Master       = 4
            Bachelor     = 3
            Intermediate = 2
            Diploma      = 1

        If no education requirement is found → 100.
        If candidate has no recognized education → 0.
        If candidate meets or exceeds requirement → 100.
        If candidate is one level below → 60.
        Otherwise → 30.
        """
        resume_levels = self.extract_education_levels(resume_text)
        job_levels = self.extract_education_levels(job_text)

        if not job_levels:
            return 100.0

        resume_level = max(
            (self.EDUCATION_HIERARCHY.get(level, 0) for level in resume_levels),
            default=0
        )
        job_level = max(
            (self.EDUCATION_HIERARCHY.get(level, 0) for level in job_levels),
            default=0
        )

        if resume_level == 0:
            return 0.0
        if resume_level >= job_level:
            return 100.0
        if resume_level == job_level - 1:
            return 60.0
        return 30.0

    # ============================================================
    # TOKENIZATION
    # ============================================================

    @staticmethod
    def tokenize(text: Any) -> Set[str]:
        """
        Extract meaningful tokens (words of length ≥3) from text.
        Keeps technical terms with +, #, ., -.
        """
        if not text:
            return set()
        text = str(text).lower()
        # Match words with letters, numbers, +, #, ., -
        tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b", text)
        # Filter out very short tokens (to reduce noise)
        return {t for t in tokens if len(t) >= 3}

    # ============================================================
    # KEYWORD SCORE
    # ============================================================

    def keyword_score(self, resume_text: Any, job_text: Any) -> float:
        """
        Calculate meaningful keyword overlap (0-100).

        Stop words are removed to avoid inflating the score with common English words.
        """
        resume_words = self.tokenize(resume_text) - self.STOP_WORDS
        job_words = self.tokenize(job_text) - self.STOP_WORDS

        if not job_words:
            return 0.0

        common = resume_words.intersection(job_words)
        score = (len(common) / len(job_words)) * 100
        return round(min(score, 100.0), 2)

    # ============================================================
    # WEIGHTED ATS SCORE
    # ============================================================

    def calculate_ats_score(
        self,
        skill_score: float,
        semantic_score: float,
        experience_score: float,
        education_score: float,
        keyword_score: float,
    ) -> float:
        """
        Calculate the weighted final ATS score (0-100).

        All inputs are automatically normalized.
        """
        skill = self.normalize_score(skill_score)
        semantic = self.normalize_score(semantic_score)
        experience = self.normalize_score(experience_score)
        education = self.normalize_score(education_score)
        keyword = self.normalize_score(keyword_score)

        final = (
            skill * self.skill_weight
            + semantic * self.semantic_weight
            + experience * self.experience_weight
            + education * self.education_weight
            + keyword * self.keyword_weight
        )
        return round(max(0.0, min(final, 100.0)), 2)

    # ============================================================
    # MATCH LEVEL
    # ============================================================

    @staticmethod
    def get_match_level(score: float) -> str:
        """
        Convert an ATS score into a human-readable match level.
        """
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Strong"
        if score >= 55:
            return "Good"
        if score >= 40:
            return "Moderate"
        return "Low"

    # ============================================================
    # SCORE STATUS
    # ============================================================

    @staticmethod
    def get_score_status(score: float) -> str:
        """
        Return a qualitative status for a single component score.
        """
        if score >= 80:
            return "High"
        if score >= 60:
            return "Medium"
        if score >= 40:
            return "Low"
        return "Very Low"

    # ============================================================
    # RECOMMENDATIONS
    # ============================================================

    def generate_recommendations(
        self,
        skill_score: float,
        semantic_score: float,
        experience_score: float,
        education_score: float,
        keyword_score: float,
    ) -> List[str]:
        """
        Generate actionable recommendations without fabricating experience.

        IMPORTANT:
            Recommendations never claim the candidate has missing skills.
        """
        recommendations: List[str] = []

        if skill_score < 60:
            recommendations.append(
                "Review the job's required skills and highlight "
                "relevant skills already supported by the master resume."
            )
        elif skill_score < 80:
            recommendations.append(
                "Improve skill coverage by clearly presenting "
                "relevant existing skills from the master resume."
            )

        if semantic_score < 60:
            recommendations.append(
                "Rewrite the professional summary and relevant "
                "experience descriptions to better reflect the "
                "target role using only supported experience."
            )

        if experience_score < 60:
            recommendations.append(
                "The detected experience level is below the job "
                "requirement. Do not fabricate experience; "
                "highlight relevant existing experience instead."
            )

        if education_score < 60:
            recommendations.append(
                "Education appears below the stated job requirement. "
                "Keep the candidate's actual education unchanged."
            )

        if keyword_score < 60:
            recommendations.append(
                "Improve keyword alignment by naturally using "
                "relevant job-description terminology where it is "
                "truthfully supported by the master resume."
            )

        if not recommendations:
            recommendations.append(
                "Resume has strong overall alignment with the "
                "target job description."
            )

        return recommendations

    # ============================================================
    # SCORE BREAKDOWN
    # ============================================================

    def get_score_breakdown(
        self,
        skill_score: float,
        semantic_score: float,
        experience_score: float,
        education_score: float,
        keyword_score: float,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return detailed weighted score breakdown for each component.
        """
        scores = {
            "skill": self.normalize_score(skill_score),
            "semantic": self.normalize_score(semantic_score),
            "experience": self.normalize_score(experience_score),
            "education": self.normalize_score(education_score),
            "keyword": self.normalize_score(keyword_score),
        }

        weights = {
            "skill": self.skill_weight,
            "semantic": self.semantic_weight,
            "experience": self.experience_weight,
            "education": self.education_weight,
            "keyword": self.keyword_weight,
        }

        breakdown = {}
        for name in scores:
            contribution = scores[name] * weights[name]
            breakdown[name] = {
                "score": scores[name],
                "weight": round(weights[name] * 100, 2),
                "contribution": round(contribution, 2),
                "status": self.get_score_status(scores[name]),
            }
        return breakdown

    # ============================================================
    # COMPLETE ANALYSIS
    # ============================================================

    def analyze(
        self,
        skill_score: float,
        semantic_score: float,
        resume_text: Any,
        job_text: Any,
    ) -> Dict[str, Any]:
        """
        Perform a complete ATS analysis.

        Parameters
        ----------
        skill_score : float
            Skill compatibility score (0-100 or 0-1).
        semantic_score : float
            Overall semantic similarity (0-100 or 0-1).
        resume_text : str
            Master resume text.
        job_text : str
            Target job description.

        Returns
        -------
        dict
            Dictionary containing all ATS metrics.
        """
        skill = self.normalize_score(skill_score)
        semantic = self.normalize_score(semantic_score)

        experience = self.experience_score(resume_text, job_text)
        education = self.education_score(resume_text, job_text)
        keyword = self.keyword_score(resume_text, job_text)

        final_score = self.calculate_ats_score(
            skill_score=skill,
            semantic_score=semantic,
            experience_score=experience,
            education_score=education,
            keyword_score=keyword,
        )

        breakdown = self.get_score_breakdown(
            skill_score=skill,
            semantic_score=semantic,
            experience_score=experience,
            education_score=education,
            keyword_score=keyword,
        )

        return {
            "skill_score": skill,
            "semantic_score": semantic,
            "experience_score": round(experience, 2),
            "education_score": round(education, 2),
            "keyword_score": round(keyword, 2),
            "final_ats_score": final_score,
            "match_level": self.get_match_level(final_score),
            "score_breakdown": breakdown,
            "recommendations": self.generate_recommendations(
                skill_score=skill,
                semantic_score=semantic,
                experience_score=experience,
                education_score=education,
                keyword_score=keyword,
            ),
        }


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ATS RANKING ENGINE TEST")
    print("=" * 70)

    resume = """
    BS Computer Science graduate with 2 years
    of experience in Python, Machine Learning,
    SQL, Pandas, NumPy and Power BI.
    """

    job = """
    We are looking for a Machine Learning Engineer
    with 2 years of experience, Bachelor's degree,
    Python, Machine Learning, SQL, TensorFlow
    and Power BI.
    """

    skill_score = 80.0
    semantic_score = 75.49

    engine = RankingEngine()
    result = engine.analyze(
        skill_score=skill_score,
        semantic_score=semantic_score,
        resume_text=resume,
        job_text=job,
    )

    print("\nSkill Score:")
    print(f"{result['skill_score']:.2f}%")

    print("\nSemantic Score:")
    print(f"{result['semantic_score']:.2f}%")

    print("\nExperience Score:")
    print(f"{result['experience_score']:.2f}%")

    print("\nEducation Score:")
    print(f"{result['education_score']:.2f}%")

    print("\nKeyword Score:")
    print(f"{result['keyword_score']:.2f}%")

    print("\n" + "-" * 70)
    print("SCORE BREAKDOWN")
    print("-" * 70)

    for name, data in result["score_breakdown"].items():
        print(
            f"{name.capitalize():12} | "
            f"Score: {data['score']:6.2f}% | "
            f"Weight: {data['weight']:5.2f}% | "
            f"Contribution: {data['contribution']:6.2f}"
        )

    print("-" * 70)
    print("\nFINAL ATS SCORE:")
    print(f"{result['final_ats_score']:.2f}%")
    print("MATCH LEVEL:", result["match_level"])

    print("\nRECOMMENDATIONS:")
    for idx, rec in enumerate(result["recommendations"], start=1):
        print(f"{idx}. {rec}")

    print("\n" + "=" * 70)
    print("ATS RANKING ENGINE TEST COMPLETED")
    print("=" * 70)
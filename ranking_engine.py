"""
ATS Ranking Engine
AI Resume Tailoring System

Combines:
1. Skill matching
2. Semantic similarity
3. Experience matching
4. Education matching
5. Keyword matching

to produce a final ATS score.
"""

import re


class RankingEngine:

    def __init__(
        self,
        skill_weight=0.40,
        semantic_weight=0.30,
        experience_weight=0.15,
        education_weight=0.10,
        keyword_weight=0.05
    ):
        """
        Initialize ATS scoring weights.

        Total weights = 100%
        """

        self.skill_weight = skill_weight
        self.semantic_weight = semantic_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight
        self.keyword_weight = keyword_weight

    # --------------------------------------------------
    # EXPERIENCE MATCHING
    # --------------------------------------------------

    def extract_years(self, text):
        """
        Extract experience years from text.

        Examples:
        '3 years experience' -> 3
        '2+ years' -> 2
        """

        if not text:
            return 0

        text = str(text).lower()

        patterns = [
            r"(\d+)\s*\+?\s*years?",
            r"(\d+)\s*\+?\s*yrs?"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:
                return int(
                    match.group(1)
                )

        return 0

    def experience_score(
        self,
        resume_text,
        job_text
    ):
        """
        Calculate experience compatibility.
        """

        resume_years = self.extract_years(
            resume_text
        )

        job_years = self.extract_years(
            job_text
        )

        # If job doesn't specify experience
        if job_years == 0:
            return 100.0

        # Candidate meets requirement
        if resume_years >= job_years:
            return 100.0

        # Candidate has some experience
        if resume_years > 0:

            percentage = (
                resume_years
                / job_years
            ) * 100

            return round(
                min(percentage, 100),
                2
            )

        return 0.0

    # --------------------------------------------------
    # EDUCATION MATCHING
    # --------------------------------------------------

    def education_score(
        self,
        resume_text,
        job_text
    ):
        """
        Estimate education compatibility.
        """

        resume = str(
            resume_text
        ).lower()

        job = str(
            job_text
        ).lower()

        education_levels = [
            "phd",
            "doctorate",
            "master",
            "ms",
            "mba",
            "bachelor",
            "bs",
            "bsc",
            "ba",
            "bba",
            "intermediate",
            "fsc",
            "ics",
            "diploma"
        ]

        resume_levels = []

        job_levels = []

        for level in education_levels:

            if re.search(
                r"(?<!\w)"
                + re.escape(level)
                + r"(?!\w)",
                resume
            ):
                resume_levels.append(
                    level
                )

            if re.search(
                r"(?<!\w)"
                + re.escape(level)
                + r"(?!\w)",
                job
            ):
                job_levels.append(
                    level
                )

        # No education requirement
        if not job_levels:
            return 100.0

        # Exact education keyword match
        if set(resume_levels).intersection(
            set(job_levels)
        ):
            return 100.0

        # Related higher education
        hierarchy = {
            "phd": 5,
            "doctorate": 5,
            "master": 4,
            "ms": 4,
            "mba": 4,
            "bachelor": 3,
            "bs": 3,
            "bsc": 3,
            "ba": 3,
            "bba": 3,
            "intermediate": 2,
            "fsc": 2,
            "ics": 2,
            "diploma": 1
        }

        resume_level = max(
            [
                hierarchy.get(x, 0)
                for x in resume_levels
            ],
            default=0
        )

        job_level = max(
            [
                hierarchy.get(x, 0)
                for x in job_levels
            ],
            default=0
        )

        if resume_level >= job_level:
            return 100.0

        if resume_level == job_level - 1:
            return 60.0

        return 30.0

    # --------------------------------------------------
    # KEYWORD MATCHING
    # --------------------------------------------------

    def keyword_score(
        self,
        resume_text,
        job_text
    ):
        """
        Calculate basic keyword overlap.
        """

        resume_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                str(resume_text).lower()
            )
        )

        job_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                str(job_text).lower()
            )
        )

        if not job_words:
            return 0.0

        common_words = (
            resume_words
            .intersection(job_words)
        )

        score = (
            len(common_words)
            / len(job_words)
        ) * 100

        return round(
            min(score, 100),
            2
        )

    # --------------------------------------------------
    # FINAL ATS SCORE
    # --------------------------------------------------

    def calculate_ats_score(
        self,
        skill_score,
        semantic_score,
        experience_score,
        education_score,
        keyword_score
    ):
        """
        Calculate weighted final ATS score.
        """

        final_score = (

            skill_score
            * self.skill_weight

            +

            semantic_score
            * self.semantic_weight

            +

            experience_score
            * self.experience_weight

            +

            education_score
            * self.education_weight

            +

            keyword_score
            * self.keyword_weight
        )

        return round(
            final_score,
            2
        )

    # --------------------------------------------------
    # COMPLETE ANALYSIS
    # --------------------------------------------------

    def analyze(
        self,
        skill_score,
        semantic_score,
        resume_text,
        job_text
    ):
        """
        Complete ATS analysis.
        """

        experience = self.experience_score(
            resume_text,
            job_text
        )

        education = self.education_score(
            resume_text,
            job_text
        )

        keyword = self.keyword_score(
            resume_text,
            job_text
        )

        final_score = self.calculate_ats_score(
            skill_score,
            semantic_score,
            experience,
            education,
            keyword
        )

        if final_score >= 85:

            level = "Excellent"

        elif final_score >= 70:

            level = "Strong"

        elif final_score >= 55:

            level = "Good"

        elif final_score >= 40:

            level = "Moderate"

        else:

            level = "Low"

        return {
            "skill_score": round(
                skill_score,
                2
            ),

            "semantic_score": round(
                semantic_score,
                2
            ),

            "experience_score": round(
                experience,
                2
            ),

            "education_score": round(
                education,
                2
            ),

            "keyword_score": round(
                keyword,
                2
            ),

            "final_ats_score": final_score,

            "match_level": level
        }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("ATS RANKING ENGINE TEST")
    print("=" * 60)

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

    # Example scores from previous modules
    skill_score = 80.0

    semantic_score = 75.49

    engine = RankingEngine()

    result = engine.analyze(
        skill_score=skill_score,
        semantic_score=semantic_score,
        resume_text=resume,
        job_text=job
    )

    print("\nSkill Score:")
    print(
        result["skill_score"],
        "%"
    )

    print("\nSemantic Score:")
    print(
        result["semantic_score"],
        "%"
    )

    print("\nExperience Score:")
    print(
        result["experience_score"],
        "%"
    )

    print("\nEducation Score:")
    print(
        result["education_score"],
        "%"
    )

    print("\nKeyword Score:")
    print(
        result["keyword_score"],
        "%"
    )

    print("\n" + "-" * 60)

    print("FINAL ATS SCORE:")
    print(
        result["final_ats_score"],
        "%"
    )

    print(
        "MATCH LEVEL:",
        result["match_level"]
    )

    print("=" * 60)
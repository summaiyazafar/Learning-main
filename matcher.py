"""
Resume vs Job Description Matcher
AI Resume Tailoring System

Combines:

1. Keyword/Skill Matching
2. Semantic Matching
3. Skill Gap Analysis
4. Final Match Score
"""

from modules.jd_analyzer import JDAnalyzer
from modules.skill_extractor import compare_skills
from modules.semantic_matcher import SemanticMatcher


class ResumeJobMatcher:

    def __init__(self):

        self.jd_analyzer = JDAnalyzer()

        self.semantic_matcher = (
            SemanticMatcher()
        )

    # --------------------------------------------------
    # KEYWORD SCORE
    # --------------------------------------------------

    def calculate_keyword_score(
        self,
        resume_text,
        job_text
    ):

        result = compare_skills(
            resume_text,
            job_text
        )

        return result

    # --------------------------------------------------
    # SEMANTIC SCORE
    # --------------------------------------------------

    def calculate_semantic_score(
        self,
        resume_text,
        job_text
    ):

        result = (
            self.semantic_matcher
            .calculate_similarity(
                resume_text,
                job_text
            )
        )

        return result

    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------

    def calculate_final_score(
        self,
        keyword_score,
        semantic_score
    ):

        # Keyword/skill matching
        keyword_weight = 0.40

        # Semantic similarity
        semantic_weight = 0.60

        final_score = (
            keyword_score * keyword_weight
            +
            semantic_score * semantic_weight
        )

        return round(
            final_score,
            2
        )

    # --------------------------------------------------
    # MATCH LEVEL
    # --------------------------------------------------

    def get_match_level(
        self,
        score
    ):

        if score >= 85:

            return "Excellent Match"

        elif score >= 70:

            return "Strong Match"

        elif score >= 55:

            return "Moderate Match"

        elif score >= 40:

            return "Weak Match"

        else:

            return "Low Match"

    # --------------------------------------------------
    # COMPLETE MATCHING
    # --------------------------------------------------

    def match(
        self,
        resume_text,
        job_text
    ):

        # ----------------------------------------------
        # JD ANALYSIS
        # ----------------------------------------------

        jd_analysis = (
            self.jd_analyzer.analyze(
                job_text
            )
        )

        # ----------------------------------------------
        # SKILL MATCHING
        # ----------------------------------------------

        skill_result = (
            self.calculate_keyword_score(
                resume_text,
                job_text
            )
        )

        keyword_score = (
            skill_result[
                "match_percentage"
            ]
        )

        # ----------------------------------------------
        # SEMANTIC MATCHING
        # ----------------------------------------------

        semantic_result = (
            self.calculate_semantic_score(
                resume_text,
                job_text
            )
        )

        # Support both possible formats
        if isinstance(
            semantic_result,
            dict
        ):

            semantic_score = (
                semantic_result.get(
                    "semantic_score",
                    semantic_result.get(
                        "score",
                        0
                    )
                )
            )

        else:

            semantic_score = (
                float(
                    semantic_result
                )
            )

        # ----------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------

        final_score = (
            self.calculate_final_score(
                keyword_score,
                semantic_score
            )
        )

        # ----------------------------------------------
        # MATCH LEVEL
        # ----------------------------------------------

        match_level = (
            self.get_match_level(
                final_score
            )
        )

        # ----------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------

        return {

            "job_title":
                jd_analysis[
                    "job_title"
                ],

            "required_skills":
                jd_analysis[
                    "skills"
                ],

            "experience_required":
                jd_analysis[
                    "experience_years"
                ],

            "qualifications":
                jd_analysis[
                    "qualifications"
                ],

            "responsibilities":
                jd_analysis[
                    "responsibilities"
                ],

            "keywords":
                jd_analysis[
                    "keywords"
                ],

            "resume_skills":
                skill_result[
                    "resume_skills"
                ],

            "matched_skills":
                skill_result[
                    "matched_skills"
                ],

            "missing_skills":
                skill_result[
                    "missing_skills"
                ],

            "keyword_score":
                keyword_score,

            "semantic_score":
                round(
                    semantic_score,
                    2
                ),

            "final_score":
                final_score,

            "match_level":
                match_level
        }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("RESUME vs JOB MATCHING ENGINE TEST")
    print("=" * 60)

    resume = """

    Python developer with experience in
    machine learning, data analysis,
    SQL, Pandas, NumPy and Power BI.

    Developed predictive machine learning
    models and data-driven applications.

    """

    job_description = """

    Job Title: Machine Learning Engineer

    We are looking for a Machine Learning
    Engineer with strong Python skills.

    Required experience includes:

    Python
    SQL
    Machine Learning
    TensorFlow
    Power BI

    The candidate should develop machine
    learning models and analyze datasets.

    """

    matcher = ResumeJobMatcher()

    result = matcher.match(
        resume,
        job_description
    )

    print("\nJOB TITLE:")

    print(
        result[
            "job_title"
        ]
    )

    print("\nREQUIRED SKILLS:")

    for skill in result[
        "required_skills"
    ]:

        print(
            "  ✓",
            skill
        )

    print("\nMATCHED SKILLS:")

    for skill in result[
        "matched_skills"
    ]:

        print(
            "  ✓",
            skill
        )

    print("\nMISSING SKILLS:")

    for skill in result[
        "missing_skills"
    ]:

        print(
            "  ✗",
            skill
        )

    print("\nKEYWORD SCORE:")

    print(
        result[
            "keyword_score"
        ],
        "%"
    )

    print("\nSEMANTIC SCORE:")

    print(
        result[
            "semantic_score"
        ],
        "%"
    )

    print("\nFINAL MATCH SCORE:")

    print(
        result[
            "final_score"
        ],
        "%"
    )

    print("\nMATCH LEVEL:")

    print(
        result[
            "match_level"
        ]
    )

    print("\n" + "=" * 60)
    print("MATCHING ENGINE TEST COMPLETED")
    print("=" * 60)
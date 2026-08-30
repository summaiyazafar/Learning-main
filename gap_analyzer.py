"""
Gap Analysis Engine
AI Resume Tailoring System

Identifies:
- Matched skills
- Missing skills
- Critical missing skills
- Skill coverage
- Improvement recommendations
"""


class GapAnalyzer:

    def __init__(self):
        pass

    def analyze_skills(
        self,
        resume_skills,
        job_skills
    ):
        """
        Compare resume skills with job skills.
        """

        resume_skills = {
            skill.lower().strip()
            for skill in resume_skills
        }

        job_skills = {
            skill.lower().strip()
            for skill in job_skills
        }

        matched_skills = sorted(
            resume_skills.intersection(
                job_skills
            )
        )

        missing_skills = sorted(
            job_skills.difference(
                resume_skills
            )
        )

        if job_skills:

            coverage = (
                len(matched_skills)
                / len(job_skills)
            ) * 100

        else:

            coverage = 0

        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_coverage": round(
                coverage,
                2
            )
        }

    def classify_missing_skills(
        self,
        missing_skills
    ):
        """
        Classify missing skills by importance.
        """

        critical_keywords = {
            "python",
            "sql",
            "machine learning",
            "deep learning",
            "data analysis",
            "javascript",
            "java",
            "react",
            "aws",
            "azure",
            "tensorflow",
            "pytorch",
            "nlp",
            "computer vision"
        }

        critical = []
        recommended = []

        for skill in missing_skills:

            if skill.lower() in critical_keywords:

                critical.append(skill)

            else:

                recommended.append(skill)

        return {
            "critical": sorted(critical),
            "recommended": sorted(recommended)
        }

    def generate_recommendations(
        self,
        missing_skills
    ):
        """
        Generate recommendations for
        missing skills.
        """

        recommendations = []

        for skill in missing_skills:

            skill_lower = skill.lower()

            if skill_lower == "tensorflow":

                recommendations.append(
                    "Add TensorFlow projects or "
                    "relevant practical experience "
                    "if you genuinely have it."
                )

            elif skill_lower == "pytorch":

                recommendations.append(
                    "Highlight PyTorch-based projects "
                    "or practical experience if available."
                )

            elif skill_lower == "sql":

                recommendations.append(
                    "Highlight SQL projects, database "
                    "work, queries, and analytics experience."
                )

            elif skill_lower == "python":

                recommendations.append(
                    "Highlight Python projects and "
                    "Python-based development experience."
                )

            elif skill_lower == "machine learning":

                recommendations.append(
                    "Highlight machine learning projects, "
                    "models, algorithms and results."
                )

            elif skill_lower == "deep learning":

                recommendations.append(
                    "Highlight deep learning projects "
                    "and neural network experience."
                )

            elif skill_lower == "power bi":

                recommendations.append(
                    "Highlight Power BI dashboards, "
                    "reports and analytics projects."
                )

            else:

                recommendations.append(
                    f"Consider highlighting relevant "
                    f"{skill} experience, projects, "
                    f"or certifications if you genuinely "
                    f"have them."
                )

        return recommendations

    def complete_analysis(
        self,
        resume_skills,
        job_skills
    ):
        """
        Perform complete gap analysis.
        """

        skill_analysis = self.analyze_skills(
            resume_skills,
            job_skills
        )

        missing_skills = (
            skill_analysis[
                "missing_skills"
            ]
        )

        classification = (
            self.classify_missing_skills(
                missing_skills
            )
        )

        recommendations = (
            self.generate_recommendations(
                missing_skills
            )
        )

        return {
            "matched_skills":
                skill_analysis[
                    "matched_skills"
                ],

            "missing_skills":
                missing_skills,

            "skill_coverage":
                skill_analysis[
                    "skill_coverage"
                ],

            "critical_missing":
                classification[
                    "critical"
                ],

            "recommended_missing":
                classification[
                    "recommended"
                ],

            "recommendations":
                recommendations
        }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("GAP ANALYSIS ENGINE TEST")
    print("=" * 60)

    resume_skills = [
        "python",
        "sql",
        "machine learning",
        "pandas",
        "numpy",
        "power bi"
    ]

    job_skills = [
        "python",
        "sql",
        "machine learning",
        "tensorflow",
        "power bi",
        "deep learning"
    ]

    analyzer = GapAnalyzer()

    result = analyzer.complete_analysis(
        resume_skills,
        job_skills
    )

    print("\nMatched Skills:")

    for skill in result[
        "matched_skills"
    ]:

        print(
            "  ✓",
            skill
        )

    print("\nMissing Skills:")

    for skill in result[
        "missing_skills"
    ]:

        print(
            "  ✗",
            skill
        )

    print(
        "\nSkill Coverage:",
        result[
            "skill_coverage"
        ],
        "%"
    )

    print(
        "\nCritical Missing Skills:"
    )

    for skill in result[
        "critical_missing"
    ]:

        print(
            "  ⚠",
            skill
        )

    print(
        "\nRecommended Missing Skills:"
    )

    for skill in result[
        "recommended_missing"
    ]:

        print(
            "  →",
            skill
        )

    print(
        "\nRecommendations:"
    )

    for recommendation in result[
        "recommendations"
    ]:

        print(
            "  •",
            recommendation
        )

    print("\n" + "=" * 60)
    print("GAP ANALYSIS COMPLETED")
    print("=" * 60)
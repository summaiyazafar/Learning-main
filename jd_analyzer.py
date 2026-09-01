```python
"""
AI Resume Tailoring System
==========================

Resume Tailoring Engine

Purpose
-------
Tailor an existing resume according to a target Job Description.

PROTECTED INFORMATION
---------------------
These fields are NEVER generated, replaced, or modified:

    Name
    Phone
    Email
    LinkedIn
    GitHub
    Kaggle
    Education
    Certifications

TAILORABLE INFORMATION
----------------------
These sections are optimized according to the JD:

    Professional Summary
    Skills
    Experience
    Projects

IMPORTANT
---------
This module does NOT invent a candidate's identity,
education, certifications, or contact information.

It uses the candidate's existing resume information
and reorganizes/rephrases it toward the target role.
"""

import re
from collections import OrderedDict


class ResumeTailor:

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):
        pass

    # ==========================================================
    # TEXT CLEANING
    # ==========================================================

    def clean_text(self, text):

        if not text:
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

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    # ==========================================================
    # LIST NORMALIZATION
    # ==========================================================

    def normalize_list(self, value):

        if value is None:
            return []

        if isinstance(value, list):

            result = []

            for item in value:

                if item is None:
                    continue

                item = str(item).strip()

                if item:
                    result.append(item)

            return result

        if isinstance(value, dict):

            result = []

            for key, values in value.items():

                if isinstance(values, list):

                    for item in values:

                        if item:
                            result.append(
                                str(item).strip()
                            )

                elif values:

                    result.append(
                        str(values).strip()
                    )

            return result

        text = str(value).strip()

        if not text:
            return []

        parts = re.split(
            r"[,|;\n]+",
            text
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    # ==========================================================
    # NORMALIZE SKILL
    # ==========================================================

    def normalize_skill(self, skill):

        skill = str(skill).strip()

        skill = re.sub(
            r"\s+",
            " ",
            skill
        )

        return skill

    # ==========================================================
    # DEDUPLICATE
    # ==========================================================

    def deduplicate(
        self,
        items
    ):

        result = []

        seen = set()

        for item in items:

            item = str(item).strip()

            if not item:
                continue

            key = re.sub(
                r"[^a-z0-9+#.]",
                "",
                item.lower()
            )

            if key in seen:
                continue

            seen.add(key)

            result.append(item)

        return result

    # ==========================================================
    # PROTECTED INFORMATION
    # ==========================================================

    def get_protected_data(
        self,
        resume_data
    ):
        """
        Extract locked information.

        These values are copied directly from the original
        resume parser output.
        """

        if not isinstance(
            resume_data,
            dict
        ):
            return {
                "name": "",
                "phone": "",
                "email": "",
                "linkedin": "",
                "github": "",
                "kaggle": "",
                "education": "",
                "certifications": ""
            }

        protected = resume_data.get(
            "protected",
            {}
        )

        if not isinstance(
            protected,
            dict
        ):
            protected = {}

        return {

            "name":
                protected.get(
                    "name",
                    resume_data.get(
                        "name",
                        ""
                    )
                ),

            "phone":
                protected.get(
                    "phone",
                    resume_data.get(
                        "phone",
                        ""
                    )
                ),

            "email":
                protected.get(
                    "email",
                    resume_data.get(
                        "email",
                        ""
                    )
                ),

            "linkedin":
                protected.get(
                    "linkedin",
                    resume_data.get(
                        "linkedin",
                        ""
                    )
                ),

            "github":
                protected.get(
                    "github",
                    resume_data.get(
                        "github",
                        ""
                    )
                ),

            "kaggle":
                protected.get(
                    "kaggle",
                    resume_data.get(
                        "kaggle",
                        ""
                    )
                ),

            "education":
                protected.get(
                    "education",
                    resume_data.get(
                        "education",
                        ""
                    )
                ),

            "certifications":
                protected.get(
                    "certifications",
                    resume_data.get(
                        "certifications",
                        ""
                    )
                )
        }

    # ==========================================================
    # EDITABLE INFORMATION
    # ==========================================================

    def get_editable_data(
        self,
        resume_data
    ):

        if not isinstance(
            resume_data,
            dict
        ):
            return {
                "summary": "",
                "skills": [],
                "experience": "",
                "projects": ""
            }

        editable = resume_data.get(
            "editable",
            {}
        )

        if not isinstance(
            editable,
            dict
        ):
            editable = {}

        return {

            "summary":
                editable.get(
                    "summary",
                    resume_data.get(
                        "summary",
                        ""
                    )
                ),

            "skills":
                editable.get(
                    "skills",
                    resume_data.get(
                        "skills",
                        []
                    )
                ),

            "experience":
                editable.get(
                    "experience",
                    resume_data.get(
                        "experience",
                        ""
                    )
                ),

            "projects":
                editable.get(
                    "projects",
                    resume_data.get(
                        "projects",
                        ""
                    )
                )
        }

    # ==========================================================
    # EXTRACT WORDS FROM JD
    # ==========================================================

    def extract_jd_terms(
        self,
        job_description,
        jd_result=None
    ):

        terms = []

        if jd_result:

            skills = jd_result.get(
                "skills",
                []
            )

            terms.extend(
                self.normalize_list(
                    skills
                )
            )

            keywords = jd_result.get(
                "keywords",
                []
            )

            terms.extend(
                self.normalize_list(
                    keywords
                )
            )

        # ------------------------------------------------------
        # Extract useful technical terms from JD text
        # ------------------------------------------------------

        jd_text = self.clean_text(
            job_description
        )

        if jd_text:

            words = re.findall(
                r"\b[A-Za-z][A-Za-z0-9+#.\-/]{1,}\b",
                jd_text
            )

            # Only add reasonably useful words.
            stop_words = {

                "the",
                "and",
                "for",
                "with",
                "from",
                "that",
                "this",
                "are",
                "you",
                "your",
                "our",
                "will",
                "have",
                "has",
                "can",
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
                "role",
                "position",
                "company",
                "employees",
                "employee",
                "required",
                "requirements",
                "experience",
                "years",
                "job",
                "team",
                "work",
                "working",
                "ability",
                "skills"
            }

            for word in words:

                if word.lower() in stop_words:
                    continue

                if len(word) < 3:
                    continue

                terms.append(word)

        return self.deduplicate(
            terms
        )

    # ==========================================================
    # MATCH SKILLS
    # ==========================================================

    def match_existing_skills(
        self,
        resume_skills,
        jd_skills
    ):
        """
        Find candidate skills that are relevant to JD.

        These are SAFE because they already exist
        in the candidate's resume.
        """

        resume_skills = [
            self.normalize_skill(x)
            for x in self.normalize_list(
                resume_skills
            )
        ]

        jd_skills = [
            self.normalize_skill(x)
            for x in self.normalize_list(
                jd_skills
            )
        ]

        matched = []

        for resume_skill in resume_skills:

            resume_lower = (
                resume_skill.lower()
            )

            for jd_skill in jd_skills:

                jd_lower = (
                    jd_skill.lower()
                )

                if (
                    resume_lower == jd_lower
                    or resume_lower in jd_lower
                    or jd_lower in resume_lower
                ):

                    matched.append(
                        resume_skill
                    )

                    break

        return self.deduplicate(
            matched
        )

    # ==========================================================
    # ORDER SKILLS
    # ==========================================================

    def prioritize_skills(
        self,
        resume_skills,
        jd_result=None
    ):
        """
        Put JD-relevant existing skills first.

        Missing skills are NOT falsely added here.
        """

        resume_skills = [
            self.normalize_skill(x)
            for x in self.normalize_list(
                resume_skills
            )
        ]

        resume_skills = self.deduplicate(
            resume_skills
        )

        if not resume_skills:
            return []

        jd_skills = []

        if isinstance(
            jd_result,
            dict
        ):

            jd_skills = self.normalize_list(
                jd_result.get(
                    "skills",
                    []
                )
            )

        jd_skills = [
            self.normalize_skill(x)
            for x in jd_skills
        ]

        matched = []
        remaining = []

        for skill in resume_skills:

            is_match = False

            for jd_skill in jd_skills:

                if (
                    skill.lower()
                    == jd_skill.lower()
                    or skill.lower()
                    in jd_skill.lower()
                    or jd_skill.lower()
                    in skill.lower()
                ):

                    is_match = True
                    break

            if is_match:
                matched.append(skill)
            else:
                remaining.append(skill)

        return (
            self.deduplicate(matched)
            +
            self.deduplicate(remaining)
        )

    # ==========================================================
    # BUILD SKILLS SECTION
    # ==========================================================

    def build_skills(
        self,
        resume_data,
        jd_result
    ):
        """
        Create optimized skills section.

        Existing candidate skills are retained.

        JD-relevant skills already present in the
        resume are moved to the front.

        Missing JD skills are returned separately
        so the UI can show them as skill gaps.
        """

        editable = self.get_editable_data(
            resume_data
        )

        resume_skills = editable.get(
            "skills",
            []
        )

        resume_skills = self.normalize_list(
            resume_skills
        )

        jd_skills = []

        if isinstance(
            jd_result,
            dict
        ):

            jd_skills = self.normalize_list(
                jd_result.get(
                    "skills",
                    []
                )
            )

        ordered_skills = self.prioritize_skills(
            resume_skills,
            jd_result
        )

        matched = self.match_existing_skills(
            resume_skills,
            jd_skills
        )

        missing = []

        for jd_skill in jd_skills:

            already_present = False

            for existing in resume_skills:

                if (
                    jd_skill.lower()
                    == existing.lower()
                    or jd_skill.lower()
                    in existing.lower()
                    or existing.lower()
                    in jd_skill.lower()
                ):

                    already_present = True
                    break

            if not already_present:

                missing.append(
                    jd_skill
                )

        return {
            "all_skills":
                ordered_skills,

            "matched_skills":
                self.deduplicate(
                    matched
                ),

            "missing_skills":
                self.deduplicate(
                    missing
                )
        }

    # ==========================================================
    # EXPERIENCE TAILORING
    # ==========================================================

    def tailor_experience(
        self,
        experience_text,
        jd_result
    ):
        """
        Professionally reorganize existing experience.

        We do NOT invent a new company, job title,
        employment period, or fake employment history.

        Existing experience sentences containing
        JD-relevant concepts are prioritized.
        """

        experience_text = self.clean_text(
            experience_text
        )

        if not experience_text:
            return []

        jd_terms = []

        if isinstance(
            jd_result,
            dict
        ):

            jd_terms.extend(
                self.normalize_list(
                    jd_result.get(
                        "skills",
                        []
                    )
                )
            )

            jd_terms.extend(
                self.normalize_list(
                    jd_result.get(
                        "keywords",
                        []
                    )
                )

            jd_terms.extend(
                self.normalize_list(
                    jd_result.get(
                        "responsibilities",
                        []
                    )
                )

        jd_terms = [
            x.lower()
            for x in jd_terms
            if x
        ]

        # ------------------------------------------------------
        # Split existing experience into lines/sentences
        # ------------------------------------------------------

        parts = re.split(
            r"\n+|(?<=[.!?])\s+",
            experience_text
        )

        parts = [
            p.strip()
            for p in parts
            if p.strip()
        ]

        relevant = []
        other = []

        for part in parts:

            lower = part.lower()

            score = 0

            for term in jd_terms:

                if term in lower:
                    score += 1

            if score > 0:
                relevant.append(
                    (score, part)
                )
            else:
                other.append(part)

        relevant.sort(
            key=lambda x: x[0],
            reverse=True
        )

        result = [
            item[1]
            for item in relevant
        ]

        result.extend(
            other
        )

        return self.deduplicate(
            result
        )

    # ==========================================================
    # PROJECT TAILORING
    # ==========================================================

    def tailor_projects(
        self,
        projects_text,
        jd_result
    ):
        """
        Reorder existing projects based on JD relevance.

        Existing projects are preserved.

        The system does NOT fabricate a project
        and present it as something the candidate actually did.
        """

        projects_text = self.clean_text(
            projects_text
        )

        if not projects_text:
            return []

        jd_terms = []

        if isinstance(
            jd_result,
            dict
        ):

            jd_terms.extend(
                self.normalize_list(
                    jd_result.get(
                        "skills",
                        []
                    )
                )
            )

            jd_terms.extend(
                self.normalize_list(
                    jd_result.get(
                        "keywords",
                        []
                    )
                )
            )

        jd_terms = [
            x.lower()
            for x in jd_terms
            if x
        ]

        parts = re.split(
            r"\n+|(?<=[.!?])\s+",
            projects_text
        )

        parts = [
            p.strip()
            for p in parts
            if p.strip()
        ]

        relevant = []
        other = []

        for part in parts:

            lower = part.lower()

            score = 0

            for term in jd_terms:

                if term in lower:
                    score += 1

            if score > 0:

                relevant.append(
                    (score, part)
                )

            else:

                other.append(part)

        relevant.sort(
            key=lambda x: x[0],
            reverse=True
        )

        result = [
            item[1]
            for item in relevant
        ]

        result.extend(
            other
        )

        return self.deduplicate(
            result
        )

    # ==========================================================
    # PROFESSIONAL SUMMARY
    # ==========================================================

    def build_summary(
        self,
        resume_data,
        jd_result,
        skills_result
    ):
        """
        Build a professional JD-focused summary
        using candidate's existing information.

        Does not add unsupported personal claims.
        """

        editable = self.get_editable_data(
            resume_data
        )

        original_summary = self.clean_text(
            editable.get(
                "summary",
                ""
            )
        )

        job_title = "Target Position"

        if isinstance(
            jd_result,
            dict
        ):

            job_title = jd_result.get(
                "job_title",
                "Target Position"
            )

        matched_skills = skills_result.get(
            "matched_skills",
            []
        )

        all_skills = skills_result.get(
            "all_skills",
            []
        )

        # ------------------------------------------------------
        # Use existing summary if available, but clean it.
        # ------------------------------------------------------

        if original_summary:

            summary = original_summary

            # Add target focus only if not already present
            if job_title.lower() not in summary.lower():

                if matched_skills:

                    summary = (
                        f"{summary} "
                        f"Targeting {job_title} roles with "
                        f"relevant experience in "
                        f"{', '.join(matched_skills[:6])}."
                    )

            return summary.strip()

        # ------------------------------------------------------
        # If original summary is unavailable,
        # create a conservative summary from resume evidence.
        # ------------------------------------------------------

        useful_skills = (
            matched_skills[:6]
            if matched_skills
            else all_skills[:6]
        )

        if useful_skills:

            return (
                f"Professional targeting "
                f"{job_title} opportunities with "
                f"practical experience and skills in "
                f"{', '.join(useful_skills)}."
            )

        return (
            f"Professional targeting "
            f"{job_title} opportunities."
        )

    # ==========================================================
    # FINAL TAILORED RESUME
    # ==========================================================

    def tailor(
        self,
        resume_data,
        jd_result,
        job_description=""
    ):
        """
        Main tailoring function.

        Accepts either:

        1. Structured resume_data from ResumeParser
        2. Raw resume text

        Returns a structured tailored resume.
        """

        # ------------------------------------------------------
        # Safety
        # ------------------------------------------------------

        if not isinstance(
            resume_data,
            dict
        ):

            resume_data = {
                "text": str(
                    resume_data
                    or ""
                ),

                "protected": {},

                "editable": {

                    "summary": "",
                    "skills": [],
                    "experience": str(
                        resume_data
                        or ""
                    ),
                    "projects": ""
                }
            }

        # ------------------------------------------------------
        # 🔒 Get protected original data
        # ------------------------------------------------------

        protected = self.get_protected_data(
            resume_data
        )

        # ------------------------------------------------------
        # 🤖 Get editable original data
        # ------------------------------------------------------

        editable = self.get_editable_data(
            resume_data
        )

        # ------------------------------------------------------
        # Skills
        # ------------------------------------------------------

        skills_result = self.build_skills(
            resume_data,
            jd_result
        )

        # ------------------------------------------------------
        # Experience
        # ------------------------------------------------------

        tailored_experience = (
            self.tailor_experience(
                editable.get(
                    "experience",
                    ""
                ),
                jd_result
            )
        )

        # ------------------------------------------------------
        # Projects
        # ------------------------------------------------------

        tailored_projects = (
            self.tailor_projects(
                editable.get(
                    "projects",
                    ""
                ),
                jd_result
            )
        )

        # ------------------------------------------------------
        # Summary
        # ------------------------------------------------------

        tailored_summary = (
            self.build_summary(
                resume_data,
                jd_result,
                skills_result
            )
        )

        # ------------------------------------------------------
        # Job information
        # ------------------------------------------------------

        job_title = "Target Position"

        experience_required = 0

        if isinstance(
            jd_result,
            dict
        ):

            job_title = jd_result.get(
                "job_title",
                "Target Position"
            )

            experience_required = jd_result.get(
                "experience_years",
                0
            )

        # ======================================================
        # FINAL RESULT
        # ======================================================

        tailored_resume = OrderedDict(

            [

                # ------------------------------------------------
                # JOB
                # ------------------------------------------------

                (
                    "job_title",
                    job_title
                ),

                (
                    "experience_required",
                    experience_required
                ),

                # ------------------------------------------------
                # 🔒 PROTECTED
                # ------------------------------------------------

                (
                    "name",
                    protected["name"]
                ),

                (
                    "phone",
                    protected["phone"]
                ),

                (
                    "email",
                    protected["email"]
                ),

                (
                    "linkedin",
                    protected["linkedin"]
                ),

                (
                    "github",
                    protected["github"]
                ),

                (
                    "kaggle",
                    protected["kaggle"]
                ),

                (
                    "education",
                    protected["education"]
                ),

                (
                    "certifications",
                    protected["certifications"]
                ),

                # ------------------------------------------------
                # 🤖 AI TAILORED
                # ------------------------------------------------

                (
                    "professional_summary",
                    tailored_summary
                ),

                (
                    "skills",
                    skills_result["all_skills"]
                ),

                (
                    "matched_skills",
                    skills_result[
                        "matched_skills"
                    ]
                ),

                (
                    "missing_skills",
                    skills_result[
                        "missing_skills"
                    ]
                ),

                (
                    "experience",
                    tailored_experience
                ),

                (
                    "projects",
                    tailored_projects
                )
            ]
        )

        return tailored_resume

    # ==========================================================
    # COMPATIBILITY METHOD
    # ==========================================================

    def tailor_resume(
        self,
        resume_data,
        jd_result,
        job_description=""
    ):
        """
        Alias for compatibility with older app.py versions.
        """

        return self.tailor(
            resume_data,
            jd_result,
            job_description
        )


# ==============================================================
# TEST
# ==============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AI RESUME TAILOR TEST")
    print("=" * 70)

    # ----------------------------------------------------------
    # Simulated original resume
    # ----------------------------------------------------------

    resume_data = {

        "protected": {

            "name":
                "Summaiya Bibi",

            "phone":
                "03001234567",

            "email":
                "summaiya@example.com",

            "linkedin":
                "https://www.linkedin.com/in/summaiya-bibi",

            "github":
                "https://github.com/summaiyazafar",

            "kaggle":
                "https://www.kaggle.com/summaiya",

            "education":
                "BS Computer Science\nVirtual University of Pakistan",

            "certifications":
                "Artificial Intelligence using Python"
        },

        "editable": {

            "summary":
                "Data professional with experience in Python, SQL and Power BI.",

            "skills": [

                "Python",
                "SQL",
                "Power BI",
                "Excel",
                "Pandas",
                "NumPy",
                "Machine Learning"
            ],

            "experience":
                """
                Analyzed business data using SQL.
                Created Power BI dashboards.
                Worked with Excel reports.
                Cleaned datasets using Pandas.
                """,

            "projects":
                """
                Sales Dashboard
                Created a Power BI dashboard for sales analysis.

                Machine Learning Project
                Built a machine learning model using Python.
                """
        }
    }

    # ----------------------------------------------------------
    # Simulated JD analysis
    # ----------------------------------------------------------

    jd_result = {

        "job_title":
            "Data Analyst",

        "skills": [

            "SQL",
            "Power BI",
            "Azure",
            "Data Analysis",
            "Dashboard",
            "Reporting",
            "Problem Solving",
            "Communication"
        ],

        "experience_years":
            3,

        "keywords": [

            "analytics",
            "reporting",
            "automation",
            "data",
            "dashboard"
        ],

        "responsibilities": [

            "Develop reporting dashboards.",
            "Analyze business data.",
            "Support data integration."
        ]
    }

    # ----------------------------------------------------------
    # Run
    # ----------------------------------------------------------

    tailor = ResumeTailor()

    result = tailor.tailor(
        resume_data,
        jd_result
    )

    # ----------------------------------------------------------
    # Display protected information
    # ----------------------------------------------------------

    print()
    print("=" * 70)
    print("🔒 PROTECTED INFORMATION")
    print("=" * 70)

    print(
        "Name:",
        result["name"]
    )

    print(
        "Phone:",
        result["phone"]
    )

    print(
        "Email:",
        result["email"]
    )

    print(
        "LinkedIn:",
        result["linkedin"]
    )

    print(
        "GitHub:",
        result["github"]
    )

    print(
        "Kaggle:",
        result["kaggle"]
    )

    print(
        "Education:",
        result["education"]
    )

    print(
        "Certifications:",
        result["certifications"]
    )

    # ----------------------------------------------------------
    # Display tailored information
    # ----------------------------------------------------------

    print()
    print("=" * 70)
    print("🤖 TAILORED INFORMATION")
    print("=" * 70)

    print()
    print("SUMMARY:")
    print(
        result["professional_summary"]
    )

    print()
    print("SKILLS:")

    for skill in result["skills"]:
        print(
            "  ✓",
            skill
        )

    print()
    print("MATCHED SKILLS:")

    for skill in result["matched_skills"]:
        print(
            "  ✓",
            skill
        )

    print()
    print("MISSING JD SKILLS:")

    for skill in result["missing_skills"]:
        print(
            "  ✗",
            skill
        )

    print()
    print("EXPERIENCE:")

    for item in result["experience"]:
        print(
            "  •",
            item
        )

    print()
    print("PROJECTS:")

    for item in result["projects"]:
        print(
            "  •",
            item
        )

    print()
    print("=" * 70)
    print("RESUME TAILORING TEST COMPLETED")
    print("=" * 70)
```

"""
Job Description Analyzer
AI Resume Tailoring System

Extracts important information from a job description:
- Job title
- Skills
- Experience
- Qualifications
- Responsibilities
- Important keywords
"""

import re

from modules.skill_extractor import extract_skills


class JDAnalyzer:

    def __init__(self):
        pass

    # --------------------------------------------------
    # CLEAN TEXT
    # --------------------------------------------------

    def clean_text(self, text):

        if not text:
            return ""

        text = str(text)

        # Remove HTML
        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        # Normalize spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # --------------------------------------------------
    # JOB TITLE
    # --------------------------------------------------

    def extract_job_title(self, text):

        text = self.clean_text(text)

        patterns = [

            r"(?:job title|position|role)\s*[:\-]\s*([A-Za-z0-9 /&,+-]+)",

            r"(?:hiring|looking for|seeking)\s+(?:an?|the)?\s*"
            r"([A-Za-z0-9 /&,+-]+?)"
            r"\s+(?:with|who|to|for)",

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                title = match.group(1).strip()

                if len(title) < 80:

                    return title

        return "Target Position"

    # --------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------

    def extract_experience(self, text):

        text = self.clean_text(text)

        patterns = [

            r"(\d+)\+?\s*(?:years?|yrs?)"
            r"\s*(?:of)?\s*(?:professional\s*)?"
            r"(?:experience|work experience)",

            r"minimum\s*(?:of)?\s*(\d+)\+?\s*"
            r"(?:years?|yrs?)",

            r"at least\s*(\d+)\+?\s*"
            r"(?:years?|yrs?)"

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                return int(
                    match.group(1)
                )

        return 0

    # --------------------------------------------------
    # QUALIFICATIONS
    # --------------------------------------------------

    def extract_qualifications(self, text):

        text = self.clean_text(text)

        qualifications = []

        education_keywords = [

            "phd",
            "doctorate",
            "master",
            "master's",
            "ms",
            "mba",
            "bachelor",
            "bachelor's",
            "bs",
            "bsc",
            "ba",
            "bba",
            "computer science",
            "software engineering",
            "information technology",
            "engineering",
            "business administration",
            "data science"
        ]

        text_lower = text.lower()

        for qualification in education_keywords:

            if qualification in text_lower:

                qualifications.append(
                    qualification
                )

        return sorted(
            set(qualifications)
        )

    # --------------------------------------------------
    # RESPONSIBILITIES
    # --------------------------------------------------

    def extract_responsibilities(self, text):

        text = self.clean_text(text)

        responsibilities = []

        responsibility_keywords = [

            "responsibilities",
            "responsibility",
            "duties",
            "what you'll do",
            "what you will do",
            "role and responsibilities"
        ]

        # Try to locate responsibility section
        for keyword in responsibility_keywords:

            pattern = (
                re.escape(keyword)
                + r"\s*[:\-]?\s*(.*)"
            )

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                section = match.group(1)

                # Split sentences
                sentences = re.split(
                    r"[.!?]\s+|;\s*",
                    section
                )

                for sentence in sentences:

                    sentence = sentence.strip()

                    if len(sentence) > 20:

                        responsibilities.append(
                            sentence
                        )

                break

        # If no dedicated section,
        # identify responsibility-like sentences
        if not responsibilities:

            sentences = re.split(
                r"[.!?]\s+",
                text
            )

            action_words = [

                "develop",
                "design",
                "build",
                "create",
                "analyze",
                "manage",
                "implement",
                "maintain",
                "lead",
                "support",
                "developing",
                "designing",
                "building",
                "analyzing",
                "managing",
                "implementing"

            ]

            for sentence in sentences:

                sentence_lower = (
                    sentence.lower()
                )

                if any(
                    word in sentence_lower
                    for word in action_words
                ):

                    if len(sentence) > 20:

                        responsibilities.append(
                            sentence.strip()
                        )

        return responsibilities[:15]

    # --------------------------------------------------
    # KEYWORDS
    # --------------------------------------------------

    def extract_keywords(
        self,
        text,
        top_n=30
    ):

        text = self.clean_text(
            text
        ).lower()

        # Remove common stop words
        stop_words = {

            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "are",
            "you",
            "your",
            "our",
            "from",
            "have",
            "has",
            "will",
            "can",
            "who",
            "into",
            "their",
            "they",
            "them",
            "was",
            "were",
            "been",
            "being",
            "not",
            "but",
            "job",
            "work",
            "role",
            "looking",
            "candidate",
            "years",
            "experience"
        }

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z+#.-]{2,}\b",
            text
        )

        frequency = {}

        for word in words:

            word = word.lower()

            if word in stop_words:
                continue

            frequency[word] = (
                frequency.get(word, 0)
                + 1
            )

        sorted_keywords = sorted(
            frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            word
            for word, count
            in sorted_keywords[:top_n]
        ]

    # --------------------------------------------------
    # COMPLETE ANALYSIS
    # --------------------------------------------------

    def analyze(self, job_text):

        job_text = self.clean_text(
            job_text
        )

        job_title = (
            self.extract_job_title(
                job_text
            )
        )

        skills = extract_skills(
            job_text
        )

        experience = (
            self.extract_experience(
                job_text
            )
        )

        qualifications = (
            self.extract_qualifications(
                job_text
            )
        )

        responsibilities = (
            self.extract_responsibilities(
                job_text
            )
        )

        keywords = (
            self.extract_keywords(
                job_text
            )
        )

        return {

            "job_title":
                job_title,

            "skills":
                skills,

            "experience_years":
                experience,

            "qualifications":
                qualifications,

            "responsibilities":
                responsibilities,

            "keywords":
                keywords
        }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("JOB DESCRIPTION ANALYZER TEST")
    print("=" * 60)

    job_description = """

    Job Title: Machine Learning Engineer

    We are looking for a Machine Learning Engineer
    with 2 years of experience.

    Qualifications:
    Bachelor's degree in Computer Science,
    Software Engineering or Data Science.

    Required Skills:
    Python, SQL, Machine Learning, TensorFlow,
    Pandas, NumPy and Power BI.

    Responsibilities:
    Develop machine learning models.
    Analyze datasets and create predictive solutions.
    Build data-driven applications.
    Implement machine learning algorithms.
    """

    analyzer = JDAnalyzer()

    result = analyzer.analyze(
        job_description
    )

    print("\nJOB TITLE:")
    print(
        result["job_title"]
    )

    print("\nREQUIRED SKILLS:")

    for skill in result["skills"]:

        print(
            "  ✓",
            skill
        )

    print("\nEXPERIENCE:")

    print(
        result["experience_years"],
        "years"
    )

    print("\nQUALIFICATIONS:")

    for qualification in result[
        "qualifications"
    ]:

        print(
            "  🎓",
            qualification
        )

    print("\nRESPONSIBILITIES:")

    for responsibility in result[
        "responsibilities"
    ]:

        print(
            "  •",
            responsibility
        )

    print("\nKEYWORDS:")

    print(
        ", ".join(
            result["keywords"]
        )
    )

    print("\n" + "=" * 60)
    print("JD ANALYSIS COMPLETED")
    print("=" * 60)
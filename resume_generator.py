"""
Professional Resume Generator
AI Resume Tailoring System

Generates a structured resume and saves it as a DOCX file.
"""

import re
import os

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class ResumeGenerator:

    def __init__(self):
        pass

    # --------------------------------------------------
    # TEXT CLEANING
    # --------------------------------------------------

    def clean_text(self, text):

        if not text:
            return ""

        text = str(text)

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # --------------------------------------------------
    # BULLET CONVERSION
    # --------------------------------------------------

    def convert_to_bullets(self, text):

        if not text:
            return []

        text = str(text)

        lines = text.split("\n")

        bullets = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            line = re.sub(
                r"^[•*\-▪◦]+\s*",
                "",
                line
            )

            if line:
                bullets.append(line)

        return bullets

    # --------------------------------------------------
    # SKILL GROUPING
    # --------------------------------------------------

    def organize_skills(self, skills):

        if not skills:
            return {}

        if isinstance(skills, str):

            skills = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

        programming = []
        data = []
        ai_ml = []
        web = []
        tools = []
        cloud = []
        soft_skills = []
        other = []

        for skill in skills:

            skill_lower = skill.lower().strip()

            if skill_lower in {
                "python",
                "java",
                "javascript",
                "typescript",
                "c++",
                "c#",
                "r"
            }:

                programming.append(skill)

            elif skill_lower in {
                "sql",
                "excel",
                "power bi",
                "tableau",
                "pandas",
                "numpy",
                "data analysis",
                "data visualization",
                "statistics"
            }:

                data.append(skill)

            elif skill_lower in {
                "machine learning",
                "deep learning",
                "artificial intelligence",
                "tensorflow",
                "pytorch",
                "scikit-learn",
                "nlp",
                "natural language processing",
                "computer vision",
                "opencv",
                "langchain",
                "rag",
                "retrieval augmented generation",
                "llm",
                "generative ai"
            }:

                ai_ml.append(skill)

            elif skill_lower in {
                "fastapi",
                "flask",
                "streamlit",
                "django",
                "html",
                "css"
            }:

                web.append(skill)

            elif skill_lower in {
                "git",
                "github",
                "docker"
            }:

                tools.append(skill)

            elif skill_lower in {
                "aws",
                "azure",
                "gcp"
            }:

                cloud.append(skill)

            elif skill_lower in {
                "communication",
                "leadership",
                "teamwork",
                "problem solving",
                "time management"
            }:

                soft_skills.append(skill)

            else:

                other.append(skill)

        result = {}

        if programming:
            result["Programming"] = programming

        if data:
            result["Data & Analytics"] = data

        if ai_ml:
            result["AI & Machine Learning"] = ai_ml

        if web:
            result["Web & APIs"] = web

        if tools:
            result["Tools & Development"] = tools

        if cloud:
            result["Cloud"] = cloud

        if soft_skills:
            result["Soft Skills"] = soft_skills

        if other:
            result["Other"] = other

        return result

    # --------------------------------------------------
    # PROFESSIONAL SUMMARY
    # --------------------------------------------------

    def generate_summary(
        self,
        job_title,
        skills,
        experience=0
    ):

        job_title = self.clean_text(job_title)

        if not job_title:
            job_title = "Professional"

        if isinstance(skills, str):

            skills = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

        skills = skills or []

        selected_skills = skills[:6]

        skill_text = ", ".join(
            selected_skills
        )

        if not skill_text:
            skill_text = "relevant technical skills"

        if experience and experience > 0:

            return (
                f"Results-oriented {job_title} with "
                f"{experience} years of experience and "
                f"practical knowledge of {skill_text}. "
                f"Experienced in applying technical skills "
                f"to data-driven projects, problem solving, "
                f"and developing effective solutions."
            )

        return (
            f"Results-oriented professional targeting "
            f"a {job_title} role, with practical knowledge "
            f"of {skill_text}. Experienced in applying "
            f"technical skills to projects, data-driven "
            f"problem solving, and developing effective "
            f"solutions."
        )

    # --------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------

    def format_experience(self, experience):

        if not experience:
            return []

        return self.convert_to_bullets(
            experience
        )

    # --------------------------------------------------
    # PROJECTS
    # --------------------------------------------------

    def format_projects(self, projects):

        if not projects:
            return []

        if isinstance(projects, str):
            projects = projects.split("\n")

        formatted = []

        for project in projects:

            project = self.clean_text(project)

            if project:
                formatted.append(project)

        return formatted

    # --------------------------------------------------
    # EDUCATION
    # --------------------------------------------------

    def format_education(self, education):

        if not education:
            return []

        if isinstance(education, str):
            education = education.split("\n")

        formatted = []

        for item in education:

            item = self.clean_text(item)

            if item:
                formatted.append(item)

        return formatted

    # --------------------------------------------------
    # CERTIFICATIONS
    # --------------------------------------------------

    def format_certifications(self, certifications):

        if not certifications:
            return []

        if isinstance(certifications, str):
            certifications = certifications.split("\n")

        formatted = []

        for certificate in certifications:

            certificate = self.clean_text(
                certificate
            )

            if certificate:
                formatted.append(certificate)

        return formatted

    # --------------------------------------------------
    # GENERATE STRUCTURED RESUME
    # --------------------------------------------------

    def generate_resume(
        self,
        job_title,
        skills,
        experience=0,
        experience_details=None,
        projects=None,
        education=None,
        certifications=None
    ):

        return {

            "job_title":
                self.clean_text(job_title),

            "professional_summary":
                self.generate_summary(
                    job_title,
                    skills,
                    experience
                ),

            "skills":
                self.organize_skills(skills),

            "experience_years":
                experience,

            "experience":
                self.format_experience(
                    experience_details
                ),

            "projects":
                self.format_projects(
                    projects
                ),

            "education":
                self.format_education(
                    education
                ),

            "certifications":
                self.format_certifications(
                    certifications
                )
        }

    # --------------------------------------------------
    # ADD HEADING
    # --------------------------------------------------

    def add_heading(self, document, text):

        paragraph = document.add_paragraph()

        paragraph.paragraph_format.space_before = Pt(10)
        paragraph.paragraph_format.space_after = Pt(4)

        run = paragraph.add_run(text)

        run.bold = True
        run.font.size = Pt(12)

        return paragraph

    # --------------------------------------------------
    # ADD BULLET
    # --------------------------------------------------

    def add_bullet(self, document, text):

        paragraph = document.add_paragraph(
            style="List Bullet"
        )

        paragraph.paragraph_format.space_after = Pt(2)

        run = paragraph.add_run(
            self.clean_text(text)
        )

        run.font.size = Pt(10)

        return paragraph

    # --------------------------------------------------
    # GENERATE DOCX
    # --------------------------------------------------

    def generate_docx(
        self,
        resume,
        output_path="output/Tailored_Resume.docx"
    ):

        document = Document()

        # --------------------------------------------------
        # PAGE SETTINGS
        # --------------------------------------------------

        section = document.sections[0]

        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

        # --------------------------------------------------
        # DEFAULT FONT
        # --------------------------------------------------

        styles = document.styles

        styles["Normal"].font.name = "Arial"
        styles["Normal"].font.size = Pt(10)

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        title = document.add_paragraph()

        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = title.add_run(
            resume.get(
                "job_title",
                "Professional"
            )
        )

        run.bold = True
        run.font.size = Pt(20)

        # --------------------------------------------------
        # PROFESSIONAL SUMMARY
        # --------------------------------------------------

        self.add_heading(
            document,
            "PROFESSIONAL SUMMARY"
        )

        paragraph = document.add_paragraph()

        paragraph.paragraph_format.space_after = Pt(5)

        run = paragraph.add_run(
            resume.get(
                "professional_summary",
                ""
            )
        )

        run.font.size = Pt(10)

        # --------------------------------------------------
        # SKILLS
        # --------------------------------------------------

        self.add_heading(
            document,
            "SKILLS"
        )

        skills = resume.get(
            "skills",
            {}
        )

        for category, skill_list in skills.items():

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(2)

            category_run = paragraph.add_run(
                category + ": "
            )

            category_run.bold = True
            category_run.font.size = Pt(10)

            skill_run = paragraph.add_run(
                ", ".join(skill_list)
            )

            skill_run.font.size = Pt(10)

        # --------------------------------------------------
        # EXPERIENCE
        # --------------------------------------------------

        experience = resume.get(
            "experience",
            []
        )

        if experience:

            self.add_heading(
                document,
                "EXPERIENCE"
            )

            for item in experience:

                self.add_bullet(
                    document,
                    item
                )

        # --------------------------------------------------
        # PROJECTS
        # --------------------------------------------------

        projects = resume.get(
            "projects",
            []
        )

        if projects:

            self.add_heading(
                document,
                "PROJECTS"
            )

            for project in projects:

                self.add_bullet(
                    document,
                    project
                )

        # --------------------------------------------------
        # EDUCATION
        # --------------------------------------------------

        education = resume.get(
            "education",
            []
        )

        if education:

            self.add_heading(
                document,
                "EDUCATION"
            )

            for item in education:

                self.add_bullet(
                    document,
                    item
                )

        # --------------------------------------------------
        # CERTIFICATIONS
        # --------------------------------------------------

        certifications = resume.get(
            "certifications",
            []
        )

        if certifications:

            self.add_heading(
                document,
                "CERTIFICATIONS"
            )

            for certificate in certifications:

                self.add_bullet(
                    document,
                    certificate
                )

        # --------------------------------------------------
        # CREATE OUTPUT DIRECTORY
        # --------------------------------------------------

        output_directory = os.path.dirname(
            output_path
        )

        if output_directory:

            os.makedirs(
                output_directory,
                exist_ok=True
            )

        # --------------------------------------------------
        # SAVE DOCUMENT
        # --------------------------------------------------

        document.save(
            output_path
        )

        return output_path

    # --------------------------------------------------
    # PRINT RESUME
    # --------------------------------------------------

    def print_resume(self, resume):

        print()
        print("=" * 60)
        print("TAILORED RESUME")
        print("=" * 60)

        print()
        print("TARGET POSITION")
        print("-" * 40)

        print(
            resume.get(
                "job_title",
                "Professional"
            )
        )

        print()
        print("PROFESSIONAL SUMMARY")
        print("-" * 40)

        print(
            resume.get(
                "professional_summary",
                ""
            )
        )

        print()
        print("SKILLS")
        print("-" * 40)

        skills = resume.get(
            "skills",
            {}
        )

        for category, skill_list in skills.items():

            print(
                f"{category}: "
                + ", ".join(skill_list)
            )

        print()
        print("EXPERIENCE")
        print("-" * 40)

        experience = resume.get(
            "experience",
            []
        )

        if experience:

            for item in experience:
                print("•", item)

        else:

            print(
                "No experience details available."
            )

        print()
        print("PROJECTS")
        print("-" * 40)

        projects = resume.get(
            "projects",
            []
        )

        if projects:

            for project in projects:
                print("•", project)

        else:

            print(
                "No projects available."
            )

        print()
        print("EDUCATION")
        print("-" * 40)

        education = resume.get(
            "education",
            []
        )

        if education:

            for item in education:
                print("•", item)

        else:

            print(
                "No education information available."
            )

        print()
        print("CERTIFICATIONS")
        print("-" * 40)

        certifications = resume.get(
            "certifications",
            []
        )

        if certifications:

            for certificate in certifications:
                print("•", certificate)

        else:

            print(
                "No certifications available."
            )

        print()
        print("=" * 60)
        print("RESUME GENERATION COMPLETED")
        print("=" * 60)


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PROFESSIONAL RESUME GENERATOR TEST")
    print("=" * 60)

    generator = ResumeGenerator()

    job_title = "Machine Learning Engineer"

    skills = [

        "machine learning",
        "python",
        "sql",
        "pandas",
        "numpy",
        "power bi",
        "scikit-learn"

    ]

    experience = 2

    experience_details = """

    Developed machine learning models for predictive analytics.

    Analyzed datasets using Python, Pandas and NumPy.

    Created data visualizations and dashboards using Power BI.

    """

    projects = [

        "Machine Learning Prediction System using Python and Scikit-learn",

        "Data Analytics Dashboard using Power BI",

        "AI Resume Tailoring System"

    ]

    education = [

        "BS Computer Science"

    ]

    certifications = [

        "Artificial Intelligence using Python",

        "Data Analytics & Business Intelligence"

    ]

    # Generate structured resume

    resume = generator.generate_resume(

        job_title=job_title,

        skills=skills,

        experience=experience,

        experience_details=experience_details,

        projects=projects,

        education=education,

        certifications=certifications

    )

    # Print resume

    generator.print_resume(
        resume
    )

    # Generate DOCX

    output_file = generator.generate_docx(
        resume,
        "output/Tailored_Resume.docx"
    )

    print()
    print("DOCX FILE CREATED:")
    print(output_file)
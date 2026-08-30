"""
Professional PDF Resume Generator
AI Resume Tailoring System

Converts tailored resume information into
a professional PDF resume.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem,
)


class PDFResumeGenerator:

    def __init__(self, output_folder="output"):

        self.output_folder = output_folder

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

    # ==================================================
    # TEXT CLEANING
    # ==================================================

    def clean_text(self, text):

        if text is None:
            return ""

        text = str(text)

        return " ".join(
            text.split()
        ).strip()

    # ==================================================
    # ESCAPE HTML
    # ==================================================

    def escape_text(self, text):

        text = self.clean_text(text)

        text = (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        return text

    # ==================================================
    # NORMALIZE LIST
    # ==================================================

    def normalize_list(self, value):

        if not value:
            return []

        if isinstance(value, str):

            lines = value.split("\n")

            result = []

            for line in lines:

                line = self.clean_text(line)

                if line:
                    result.append(line)

            return result

        if isinstance(value, (list, tuple, set)):

            result = []

            for item in value:

                item = self.clean_text(item)

                if item:
                    result.append(item)

            return result

        return [self.clean_text(value)]

    # ==================================================
    # CREATE STYLES
    # ==================================================

    def create_styles(self):

        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="ResumeName",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=26,
                alignment=TA_CENTER,
                spaceAfter=5,
            )
        )

        styles.add(
            ParagraphStyle(
                name="ResumeTitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=11,
                leading=14,
                alignment=TA_CENTER,
                spaceAfter=10,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                spaceBefore=10,
                spaceAfter=5,
                textColor=colors.black,
            )
        )

        styles.add(
            ParagraphStyle(
                name="BodyResume",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                spaceAfter=4,
            )
        )

        styles.add(
            ParagraphStyle(
                name="BulletResume",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                leftIndent=12,
                firstLineIndent=0,
                spaceAfter=3,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SkillResume",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                spaceAfter=3,
            )
        )

        return styles

    # ==================================================
    # ADD SECTION HEADING
    # ==================================================

    def add_heading(
        self,
        story,
        title,
        styles
    ):

        story.append(
            Paragraph(
                self.escape_text(title),
                styles["SectionHeading"]
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                spaceBefore=0,
                spaceAfter=5,
            )
        )

    # ==================================================
    # ADD BULLETS
    # ==================================================

    def add_bullets(
        self,
        story,
        items,
        styles
    ):

        items = self.normalize_list(items)

        if not items:
            return

        bullet_items = []

        for item in items:

            bullet_items.append(
                ListItem(
                    Paragraph(
                        self.escape_text(item),
                        styles["BulletResume"]
                    ),
                    leftIndent=8
                )
            )

        story.append(
            ListFlowable(
                bullet_items,
                bulletType="bullet",
                start="circle",
                leftIndent=18,
            )
        )

        story.append(
            Spacer(1, 2)
        )

    # ==================================================
    # GENERATE PDF
    # ==================================================

    def generate_pdf(
        self,
        resume,
        filename="Tailored_Resume.pdf"
    ):

        if not isinstance(resume, dict):

            raise TypeError(
                "resume must be a dictionary"
            )

        if not filename.lower().endswith(".pdf"):

            filename += ".pdf"

        filepath = os.path.join(
            self.output_folder,
            filename
        )

        styles = self.create_styles()

        document = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title="Tailored Resume",
            author="AI Resume Tailoring System",
        )

        story = []

        # ==================================================
        # NAME
        # ==================================================

        name = resume.get(
            "name",
            "Candidate"
        )

        name = self.escape_text(name)

        story.append(
            Paragraph(
                name,
                styles["ResumeName"]
            )
        )

        # ==================================================
        # TARGET POSITION
        # ==================================================

        job_title = resume.get(
            "job_title",
            "Professional"
        )

        story.append(
            Paragraph(
                self.escape_text(job_title),
                styles["ResumeTitle"]
            )
        )

        # ==================================================
        # CONTACT INFORMATION
        # ==================================================

        email = resume.get(
            "email",
            ""
        )

        phone = resume.get(
            "phone",
            ""
        )

        linkedin = resume.get(
            "linkedin",
            ""
        )

        github = resume.get(
            "github",
            ""
        )

        contact_parts = []

        if email:
            contact_parts.append(
                self.escape_text(email)
            )

        if phone:
            contact_parts.append(
                self.escape_text(phone)
            )

        if linkedin:
            contact_parts.append(
                self.escape_text(linkedin)
            )

        if github:
            contact_parts.append(
                self.escape_text(github)
            )

        if contact_parts:

            story.append(
                Paragraph(
                    " | ".join(contact_parts),
                    styles["BodyResume"]
                )
            )

            story.append(
                Spacer(1, 5)
            )

        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                spaceBefore=2,
                spaceAfter=8,
            )
        )

        # ==================================================
        # PROFESSIONAL SUMMARY
        # ==================================================

        summary = resume.get(
            "professional_summary",
            ""
        )

        if summary:

            self.add_heading(
                story,
                "PROFESSIONAL SUMMARY",
                styles
            )

            story.append(
                Paragraph(
                    self.escape_text(summary),
                    styles["BodyResume"]
                )
            )

        # ==================================================
        # TECHNICAL SKILLS
        # ==================================================

        skills = resume.get(
            "skills",
            {}
        )

        if skills:

            self.add_heading(
                story,
                "TECHNICAL SKILLS",
                styles
            )

            if isinstance(skills, dict):

                for category, skill_list in skills.items():

                    skill_list = self.normalize_list(
                        skill_list
                    )

                    if not skill_list:
                        continue

                    category_text = (
                        f"<b>{self.escape_text(category)}:</b> "
                    )

                    skill_text = ", ".join(
                        self.escape_text(skill)
                        for skill in skill_list
                    )

                    story.append(
                        Paragraph(
                            category_text + skill_text,
                            styles["SkillResume"]
                        )
                    )

            else:

                skill_list = self.normalize_list(
                    skills
                )

                story.append(
                    Paragraph(
                        ", ".join(
                            self.escape_text(skill)
                            for skill in skill_list
                        ),
                        styles["SkillResume"]
                    )
                )

        # ==================================================
        # EXPERIENCE
        # ==================================================

        experience = resume.get(
            "experience",
            []
        )

        experience_years = resume.get(
            "experience_years",
            0
        )

        if experience or experience_years:

            self.add_heading(
                story,
                "EXPERIENCE",
                styles
            )

            if experience_years:

                story.append(
                    Paragraph(
                        f"<b>Experience:</b> "
                        f"{self.escape_text(experience_years)} years",
                        styles["BodyResume"]
                    )
                )

            self.add_bullets(
                story,
                experience,
                styles
            )

        # ==================================================
        # PROJECTS
        # ==================================================

        projects = resume.get(
            "projects",
            []
        )

        if projects:

            self.add_heading(
                story,
                "PROJECTS",
                styles
            )

            projects = self.normalize_list(
                projects
            )

            for project in projects:

                story.append(
                    Paragraph(
                        "• "
                        + self.escape_text(project),
                        styles["BulletResume"]
                    )
                )

        # ==================================================
        # EDUCATION
        # ==================================================

        education = resume.get(
            "education",
            []
        )

        if education:

            self.add_heading(
                story,
                "EDUCATION",
                styles
            )

            education = self.normalize_list(
                education
            )

            for item in education:

                story.append(
                    Paragraph(
                        "• "
                        + self.escape_text(item),
                        styles["BulletResume"]
                    )
                )

        # ==================================================
        # CERTIFICATIONS
        # ==================================================

        certifications = resume.get(
            "certifications",
            []
        )

        if certifications:

            self.add_heading(
                story,
                "CERTIFICATIONS",
                styles
            )

            certifications = self.normalize_list(
                certifications
            )

            for certificate in certifications:

                story.append(
                    Paragraph(
                        "• "
                        + self.escape_text(certificate),
                        styles["BulletResume"]
                    )
                )

        # ==================================================
        # BUILD PDF
        # ==================================================

        document.build(story)

        return filepath

    # ==================================================
    # TEST
    # ==================================================

    def test(self):

        sample_resume = {

            "name":
                "Summaiya Bibi",

            "email":
                "summaiya@example.com",

            "phone":
                "03001234567",

            "job_title":
                "Machine Learning Engineer",

            "professional_summary":
                "AI and Machine Learning professional with "
                "practical knowledge of Python, SQL, Machine "
                "Learning, Pandas, NumPy and Power BI. "
                "Experienced in developing data-driven solutions "
                "and predictive models.",

            "skills": {

                "Programming":
                    [
                        "Python"
                    ],

                "Data & Analytics":
                    [
                        "SQL",
                        "Pandas",
                        "NumPy",
                        "Power BI"
                    ],

                "AI & Machine Learning":
                    [
                        "Machine Learning",
                        "Scikit-learn"
                    ]

            },

            "experience_years":
                2,

            "experience":
                [
                    "Developed machine learning models "
                    "for predictive analytics.",

                    "Analyzed datasets using Python, "
                    "Pandas and NumPy.",

                    "Created data visualizations and "
                    "dashboards using Power BI."
                ],

            "projects":
                [
                    "Machine Learning Prediction System "
                    "using Python and Scikit-learn",

                    "Data Analytics Dashboard using Power BI",

                    "AI Resume Tailoring System"
                ],

            "education":
                [
                    "BS Computer Science"
                ],

            "certifications":
                [
                    "Artificial Intelligence using Python",

                    "Data Analytics & Business Intelligence"
                ]
        }

        output_file = self.generate_pdf(
            sample_resume,
            "Tailored_Resume.pdf"
        )

        return output_file


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PROFESSIONAL PDF RESUME GENERATOR TEST")
    print("=" * 60)

    generator = PDFResumeGenerator()

    try:

        output_file = generator.test()

        print()
        print("PDF FILE CREATED:")
        print(output_file)

        print()
        print("=" * 60)
        print("PDF GENERATION COMPLETED")
        print("=" * 60)

    except Exception as error:

        print()
        print("ERROR:")
        print(error)

        print()
        print("=" * 60)
        print("PDF GENERATION FAILED")
        print("=" * 60)
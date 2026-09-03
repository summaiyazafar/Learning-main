"""
============================================================
AI RESUME TAILORING SYSTEM
============================================================

File:
    pdf_generator.py

Purpose:
    Convert tailored resume information into a
    professional ATS-friendly PDF resume.

IMPORTANT RESUME RULE:
    Personal information such as:
        - Name
        - Email
        - Phone
        - LinkedIn
        - GitHub
        - Kaggle
        - Location
        - Education
        - Certifications

    should be preserved from the master resume.

    Tailoring should primarily affect:
        - Professional Summary
        - Skills
        - Experience wording/order
        - Projects wording/order

    This module ONLY renders the supplied resume data.
    It does not invent candidate information.
"""

import os
import re
from xml.sax.saxutils import escape
from typing import Any, Dict, List, Optional, Union

# ============================================================
# REPORTLAB – CHECK IF INSTALLED
# ============================================================

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        ParagraphStyle,
        getSampleStyleSheet
    )
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        HRFlowable,
        ListFlowable,
        ListItem,
        PageBreak
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    raise ImportError(
        "reportlab is required to generate PDFs. "
        "Please install it: pip install reportlab"
    )


# ============================================================
# PDF RESUME GENERATOR
# ============================================================

class PDFResumeGenerator:
    """
    Generate a professional PDF resume from structured data.

    The generator preserves all personal information and only
    updates the sections that are meant to be tailored:
        - Professional Summary
        - Skills
        - Experience (order/wording)
        - Projects (order/wording)
    """

    def __init__(self, output_folder: str = "output"):
        """
        Initialize the PDF generator.

        Parameters
        ----------
        output_folder : str
            Directory where generated PDFs will be stored.
        """
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    # ========================================================
    # TEXT CLEANING
    # ========================================================

    def clean_text(self, text: Any) -> str:
        """
        Clean unnecessary whitespace and convert to string.
        """
        if text is None:
            return ""
        text = str(text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ========================================================
    # HTML ESCAPING
    # ========================================================

    def escape_text(self, text: Any) -> str:
        """
        Escape text before inserting it into ReportLab Paragraph markup.
        """
        text = self.clean_text(text)
        return escape(text)

    # ========================================================
    # NORMALIZE LIST
    # ========================================================

    def normalize_list(self, value: Any) -> List[str]:
        """
        Convert various input types into a clean list of strings.

        Supports:
            - None → []
            - str → split by newline, comma, or semicolon; remove bullets.
            - list/tuple/set → flatten and clean each item.
            - any other → single-item list if non-empty.
        """
        if value is None:
            return []

        # If it's a string, split by common delimiters and bullets
        if isinstance(value, str):
            # Split by newline, comma, semicolon, or bullet characters
            parts = re.split(r"[\n,;|•●▪◦*-]+", value)
            result = []
            for part in parts:
                part = self.clean_text(part)
                # Remove common bullet characters from the start
                part = re.sub(r"^[•●▪◦*-]\s*", "", part)
                if part:
                    result.append(part)
            return result

        # If it's a collection
        if isinstance(value, (list, tuple, set)):
            result = []
            for item in value:
                item = self.clean_text(item)
                if item:
                    result.append(item)
            return result

        # Single value
        value = self.clean_text(value)
        return [value] if value else []

    # ========================================================
    # NORMALIZE DICTIONARY
    # ========================================================

    def normalize_dict(self, value: Any) -> Dict[str, List[str]]:
        """
        Safely normalize dictionary-like data.
        """
        if not isinstance(value, dict):
            return {}
        result = {}
        for key, items in value.items():
            key = self.clean_text(key)
            normalized_items = self.normalize_list(items)
            if key and normalized_items:
                result[key] = normalized_items
        return result

    # ========================================================
    # CREATE STYLES
    # ========================================================

    def create_styles(self):
        """
        Create professional ATS-friendly PDF styles.
        """
        styles = getSampleStyleSheet()

        # Name
        styles.add(
            ParagraphStyle(
                name="ResumeName",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=20,
                leading=24,
                alignment=TA_CENTER,
                spaceAfter=3,
                textColor=colors.black
            )
        )

        # Job Title
        styles.add(
            ParagraphStyle(
                name="ResumeTitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10.5,
                leading=13,
                alignment=TA_CENTER,
                spaceAfter=6,
                textColor=colors.black
            )
        )

        # Contact
        styles.add(
            ParagraphStyle(
                name="Contact",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=11,
                alignment=TA_CENTER,
                spaceAfter=6
            )
        )

        # Section Heading
        styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=10.5,
                leading=13,
                alignment=TA_LEFT,
                spaceBefore=8,
                spaceAfter=3,
                textColor=colors.black,
                keepWithNext=True
            )
        )

        # Body
        styles.add(
            ParagraphStyle(
                name="BodyResume",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                alignment=TA_LEFT,
                spaceAfter=3
            )
        )

        # Bullet
        styles.add(
            ParagraphStyle(
                name="BulletResume",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                alignment=TA_LEFT,
                leftIndent=10,
                firstLineIndent=0,
                spaceAfter=2
            )
        )

        # Skills
        styles.add(
            ParagraphStyle(
                name="SkillResume",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                alignment=TA_LEFT,
                spaceAfter=2
            )
        )

        # Experience Title
        styles.add(
            ParagraphStyle(
                name="ExperienceTitle",
                parent=styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=9.5,
                leading=12,
                spaceAfter=1,
                keepWithNext=True
            )
        )

        # Experience Meta
        styles.add(
            ParagraphStyle(
                name="ExperienceMeta",
                parent=styles["BodyText"],
                fontName="Helvetica-Oblique",
                fontSize=8.5,
                leading=11,
                spaceAfter=2
            )
        )

        # Project Title
        styles.add(
            ParagraphStyle(
                name="ProjectTitle",
                parent=styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=9.3,
                leading=12,
                spaceAfter=1,
                keepWithNext=True
            )
        )

        return styles

    # ========================================================
    # PAGE FOOTER
    # ========================================================

    def add_page_number(self, canvas, document):
        """
        Add page number to every page.
        """
        canvas.saveState()
        page_number = canvas.getPageNumber()
        canvas.setFont("Helvetica", 7.5)
        canvas.drawCentredString(
            A4[0] / 2,
            8 * mm,
            f"Page {page_number}"
        )
        canvas.restoreState()

    # ========================================================
    # SECTION HEADING
    # ========================================================

    def add_heading(self, story: List, title: str, styles):
        """
        Add a section heading with a horizontal line.
        """
        title = self.clean_text(title)
        if not title:
            return
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
                spaceAfter=4,
                color=colors.black
            )
        )

    # ========================================================
    # BULLET LIST
    # ========================================================

    def add_bullets(self, story: List, items: Any, styles):
        """
        Add a clean bullet list.
        """
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
                leftIndent=15,
                bulletFontName="Helvetica",
                bulletFontSize=6
            )
        )
        story.append(Spacer(1, 2))

    # ========================================================
    # CREATE CLICKABLE LINK
    # ========================================================

    def make_link(self, label: str, url: str) -> str:
        """
        Create a clickable ReportLab hyperlink.
        """
        label = self.escape_text(label)
        url = self.clean_text(url)
        if not url:
            return label
        if not re.match(r"^https?://", url, re.IGNORECASE):
            return label
        safe_url = escape(url, {'"': "&quot;"})
        return f'<link href="{safe_url}"><u>{label}</u></link>'

    # ========================================================
    # CONTACT INFORMATION
    # ========================================================

    def add_contact_information(self, story: List, resume: Dict, styles):
        """
        Add contact details. Personal information is READ ONLY here.
        """
        contact_parts = []

        # Email
        email = self.clean_text(resume.get("email", ""))
        if email:
            safe_email = self.escape_text(email)
            email_link = f'<link href="mailto:{safe_email}"><u>{safe_email}</u></link>'
            contact_parts.append(email_link)

        # Phone
        phone = self.clean_text(resume.get("phone", ""))
        if phone:
            contact_parts.append(self.escape_text(phone))

        # Location
        location = self.clean_text(resume.get("location", ""))
        if location:
            contact_parts.append(self.escape_text(location))

        # LinkedIn
        linkedin = self.clean_text(resume.get("linkedin", ""))
        if linkedin:
            contact_parts.append(self.make_link("LinkedIn", linkedin))

        # GitHub
        github = self.clean_text(resume.get("github", ""))
        if github:
            contact_parts.append(self.make_link("GitHub", github))

        # Kaggle
        kaggle = self.clean_text(resume.get("kaggle", ""))
        if kaggle:
            contact_parts.append(self.make_link("Kaggle", kaggle))

        if not contact_parts:
            return

        story.append(
            Paragraph(
                " | ".join(contact_parts),
                styles["Contact"]
            )
        )
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.8,
                spaceBefore=1,
                spaceAfter=7,
                color=colors.black
            )
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    def add_summary(self, story: List, resume: Dict, styles):
        """
        Add professional summary.
        """
        summary = self.clean_text(resume.get("professional_summary", ""))
        if not summary:
            return
        self.add_heading(story, "PROFESSIONAL SUMMARY", styles)
        story.append(
            Paragraph(
                self.escape_text(summary),
                styles["BodyResume"]
            )
        )

    # ========================================================
    # SKILLS
    # ========================================================

    def add_skills(self, story: List, resume: Dict, styles):
        """
        Add technical skills.

        Supports:
            - dict: { "Programming": ["Python", "SQL"], ... }
            - list: ["Python", "SQL", "Power BI"]
        """
        skills = resume.get("skills", {})
        if not skills:
            return

        self.add_heading(story, "TECHNICAL SKILLS", styles)

        if isinstance(skills, dict):
            normalized_skills = self.normalize_dict(skills)
            for category, skill_list in normalized_skills.items():
                category_text = f"<b>{self.escape_text(category)}:</b> "
                skill_text = ", ".join(
                    self.escape_text(skill) for skill in skill_list
                )
                story.append(
                    Paragraph(
                        category_text + skill_text,
                        styles["SkillResume"]
                    )
                )
        else:
            skill_list = self.normalize_list(skills)
            if skill_list:
                story.append(
                    Paragraph(
                        ", ".join(self.escape_text(s) for s in skill_list),
                        styles["SkillResume"]
                    )
                )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    def add_experience(self, story: List, resume: Dict, styles):
        """
        Add professional experience.

        Supports:
            Simple list:
                ["Developed ML models...", "Analyzed datasets..."]

            Structured list:
                [
                    {
                        "company": "...",
                        "title": "...",
                        "location": "...",
                        "dates": "...",
                        "bullets": [...]
                    }
                ]
        """
        experience = resume.get("experience", [])
        if not experience:
            return

        self.add_heading(story, "EXPERIENCE", styles)

        # Structured experience
        if isinstance(experience, list) and all(isinstance(item, dict) for item in experience):
            for item in experience:
                title = self.clean_text(item.get("title", item.get("role", "")))
                company = self.clean_text(item.get("company", ""))
                location = self.clean_text(item.get("location", ""))
                dates = self.clean_text(item.get("dates", item.get("duration", "")))

                heading_parts = []
                if title:
                    heading_parts.append(self.escape_text(title))
                if company:
                    heading_parts.append(self.escape_text(company))
                if heading_parts:
                    story.append(
                        Paragraph(
                            " — ".join(heading_parts),
                            styles["ExperienceTitle"]
                        )
                    )

                meta_parts = []
                if location:
                    meta_parts.append(self.escape_text(location))
                if dates:
                    meta_parts.append(self.escape_text(dates))
                if meta_parts:
                    story.append(
                        Paragraph(
                            " | ".join(meta_parts),
                            styles["ExperienceMeta"]
                        )
                    )

                bullets = item.get("bullets", item.get("description", []))
                self.add_bullets(story, bullets, styles)

        else:
            self.add_bullets(story, experience, styles)

    # ========================================================
    # PROJECTS
    # ========================================================

    def add_projects(self, story: List, resume: Dict, styles):
        """
        Add projects.

        Supports:
            Simple list:
                ["Project description"]

            Structured list:
                [
                    {
                        "name": "...",
                        "description": "...",
                        "technologies": [...]
                    }
                ]
        """
        projects = resume.get("projects", [])
        if not projects:
            return

        self.add_heading(story, "PROJECTS", styles)

        if isinstance(projects, list) and all(isinstance(item, dict) for item in projects):
            for project in projects:
                name = self.clean_text(project.get("name", project.get("title", "")))
                description = self.clean_text(project.get("description", ""))
                technologies = self.normalize_list(
                    project.get("technologies", project.get("tech_stack", []))
                )

                if name:
                    story.append(
                        Paragraph(
                            self.escape_text(name),
                            styles["ProjectTitle"]
                        )
                    )

                if description:
                    story.append(
                        Paragraph(
                            self.escape_text(description),
                            styles["BodyResume"]
                        )
                    )

                if technologies:
                    tech_text = "<b>Technologies:</b> " + ", ".join(
                        self.escape_text(t) for t in technologies
                    )
                    story.append(
                        Paragraph(
                            tech_text,
                            styles["BodyResume"]
                        )
                    )

                story.append(Spacer(1, 2))

        else:
            self.add_bullets(story, projects, styles)

    # ========================================================
    # EDUCATION
    # ========================================================

    def add_education(self, story: List, resume: Dict, styles):
        """
        Add education exactly as supplied.
        """
        education = resume.get("education", [])
        if not education:
            return

        self.add_heading(story, "EDUCATION", styles)

        if isinstance(education, list) and all(isinstance(item, dict) for item in education):
            for item in education:
                degree = self.clean_text(item.get("degree", item.get("title", "")))
                institution = self.clean_text(item.get("institution", item.get("university", "")))
                dates = self.clean_text(item.get("dates", ""))

                parts = []
                if degree:
                    parts.append(self.escape_text(degree))
                if institution:
                    parts.append(self.escape_text(institution))
                if dates:
                    parts.append(self.escape_text(dates))

                if parts:
                    story.append(
                        Paragraph(
                            " — ".join(parts),
                            styles["BodyResume"]
                        )
                    )
        else:
            self.add_bullets(story, education, styles)

    # ========================================================
    # CERTIFICATIONS
    # ========================================================

    def add_certifications(self, story: List, resume: Dict, styles):
        """
        Add certifications exactly as supplied.
        """
        certifications = resume.get("certifications", [])
        if not certifications:
            return
        self.add_heading(story, "CERTIFICATIONS", styles)
        self.add_bullets(story, certifications, styles)

    # ========================================================
    # ADD OPTIONAL SECTION
    # ========================================================

    def add_optional_section(
        self,
        story: List,
        resume: Dict,
        field_name: str,
        heading: str,
        styles
    ):
        """
        Add an optional list-based section (e.g., Awards, Languages, Achievements).
        """
        values = self.normalize_list(resume.get(field_name, []))
        if not values:
            return
        self.add_heading(story, heading, styles)
        self.add_bullets(story, values, styles)

    # ========================================================
    # GENERATE PDF
    # ========================================================

    def generate_pdf(
        self,
        resume: Dict[str, Any],
        filename: str = "Tailored_Resume.pdf"
    ) -> str:
        """
        Generate a professional ATS-friendly PDF resume.

        Parameters
        ----------
        resume : dict
            Resume data with keys: name, email, phone, location,
            linkedin, github, kaggle, professional_summary,
            skills, experience, projects, education, certifications,
            languages, achievements, etc.
        filename : str
            Output PDF filename.

        Returns
        -------
        str
            Full path to the generated PDF file.
        """
        if not isinstance(resume, dict):
            raise TypeError("resume must be a dictionary")

        # Clean filename
        filename = self.clean_text(filename)
        if not filename:
            filename = "Tailored_Resume.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        # Remove unsafe characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

        filepath = os.path.join(self.output_folder, filename)

        styles = self.create_styles()

        document = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=17 * mm,
            leftMargin=17 * mm,
            topMargin=13 * mm,
            bottomMargin=14 * mm,
            title="Tailored Resume",
            author="AI Resume Tailoring System",
            subject="AI Generated Tailored Resume",
            creator="AI Resume Tailoring System"
        )

        story = []

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------
        name = self.clean_text(resume.get("name", "Candidate"))
        if not name:
            name = "Candidate"

        story.append(
            Paragraph(
                self.escape_text(name),
                styles["ResumeName"]
            )
        )

        job_title = self.clean_text(
            resume.get("job_title", resume.get("target_position", ""))
        )
        if job_title:
            story.append(
                Paragraph(
                    self.escape_text(job_title),
                    styles["ResumeTitle"]
                )
            )

        self.add_contact_information(story, resume, styles)

        # ----------------------------------------------------
        # SECTIONS
        # ----------------------------------------------------
        self.add_summary(story, resume, styles)
        self.add_skills(story, resume, styles)
        self.add_experience(story, resume, styles)
        self.add_projects(story, resume, styles)
        self.add_education(story, resume, styles)
        self.add_certifications(story, resume, styles)
        self.add_optional_section(story, resume, "achievements", "ACHIEVEMENTS", styles)
        self.add_optional_section(story, resume, "languages", "LANGUAGES", styles)

        if not story:
            raise ValueError(
                "Resume does not contain enough information "
                "to generate a PDF."
            )

        document.build(
            story,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number
        )

        return filepath

    # ========================================================
    # TEST DATA
    # ========================================================

    def test(self) -> str:
        """
        Generate a sample resume PDF to verify functionality.
        """
        sample_resume = {
            "name": "Summaiya Bibi",
            "email": "summaiya4545@gmail.com",
            "phone": "03466577540",
            "location": "Taxila, Rawalpindi, Pakistan",
            "linkedin": "https://www.linkedin.com/in/example",
            "github": "https://github.com/example",
            "kaggle": "https://www.kaggle.com/example",
            "job_title": "Machine Learning Engineer",
            "professional_summary": (
                "AI and Machine Learning professional with "
                "practical experience in Python, SQL, Machine "
                "Learning, Pandas, NumPy and Scikit-learn. "
                "Experienced in developing data-driven solutions, "
                "predictive models and analytical applications."
            ),
            "skills": {
                "Programming": ["Python", "SQL"],
                "Data & Analytics": ["Pandas", "NumPy", "Power BI"],
                "Machine Learning": ["Machine Learning", "Scikit-learn", "Predictive Modeling"],
                "Tools & Frameworks": ["Streamlit", "Git", "GitHub"]
            },
            "experience": [
                {
                    "title": "Machine Learning Developer",
                    "company": "Sample Organization",
                    "location": "Islamabad, Pakistan",
                    "dates": "2025 – 2026",
                    "bullets": [
                        "Developed machine learning models for predictive analytics.",
                        "Analyzed structured datasets using Python, Pandas and NumPy.",
                        "Built data-driven applications using Streamlit."
                    ]
                }
            ],
            "projects": [
                {
                    "name": "Machine Learning Prediction System",
                    "description": "Developed a machine learning prediction system using Python and Scikit-learn.",
                    "technologies": ["Python", "Scikit-learn", "Pandas", "NumPy"]
                },
                {
                    "name": "Power BI Analytics Dashboard",
                    "description": "Created an interactive analytics dashboard for data-driven reporting.",
                    "technologies": ["Power BI", "Excel", "SQL"]
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "institution": "Virtual University of Pakistan",
                    "dates": "2021 – 2025"
                }
            ],
            "certifications": [
                "Artificial Intelligence using Python",
                "Data Analytics & Business Intelligence",
                "Machine Learning Specialization"
            ],
            "languages": ["English", "Urdu"]
        }

        return self.generate_pdf(sample_resume, "Tailored_Resume_Test.pdf")


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PROFESSIONAL PDF RESUME GENERATOR TEST")
    print("=" * 70)

    generator = PDFResumeGenerator()

    try:
        output_file = generator.test()
        print()
        print("PDF FILE CREATED SUCCESSFULLY")
        print(f"Location: {output_file}")
        print()
        print("=" * 70)
        print("PDF GENERATION COMPLETED")
        print("=" * 70)

    except Exception as error:
        print()
        print("ERROR:")
        print(str(error))
        print()
        print("=" * 70)
        print("PDF GENERATION FAILED")
        print("=" * 70)
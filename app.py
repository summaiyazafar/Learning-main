import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ============================================================
# IMPORT EXISTING MODULES
# ============================================================

from modules.resume_parser import ResumeParser
from modules.jd_analyzer import JDAnalyzer
from modules.skill_extractor import extract_skills
from modules.matcher import ResumeJobMatcher
from modules.gap_analyzer import GapAnalyzer
from modules.resume_tailor import ResumeTailor


# ============================================================
# OPTIONAL GENERATORS
# ============================================================

try:
    from modules.resume_generator import ResumeGenerator
except Exception:
    ResumeGenerator = None

try:
    from modules.pdf_generator import PDFGenerator
except Exception:
    PDFGenerator = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Tailoring System",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #666;
        margin-bottom: 30px;
    }

    .score-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #ddd;
        background: #f8f9fa;
    }

    .score-number {
        font-size: 36px;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 AI Resume Tailoring System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'ML/DL-powered Resume Analysis, ATS Matching & Resume Tailoring'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ System")

    st.write("AI Resume Tailoring Pipeline")

    st.markdown(
        """
        **Pipeline**

        📄 Resume Upload  
        ↓  
        🔍 Resume Parsing  
        ↓  
        📝 Job Description Analysis  
        ↓  
        🧠 Semantic Matching  
        ↓  
        📊 ATS Score  
        ↓  
        🔎 Skill Gap Analysis  
        ↓  
        ✨ Resume Tailoring  
        ↓  
        📥 DOCX / PDF
        """
    )

    st.divider()

    st.info(
        "Only add skills, experience or projects "
        "that are genuinely supported by the candidate."
    )


# ============================================================
# INPUT SECTION
# ============================================================

st.header("1️⃣ Upload Your Resume")

resume_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)


st.header("2️⃣ Enter Job Description")

job_description = st.text_area(
    "Paste the complete Job Description here",
    height=300,
    placeholder=(
        "Example:\n\n"
        "We are looking for a Machine Learning Engineer "
        "with strong Python, SQL, TensorFlow and Machine "
        "Learning experience..."
    )
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze_button = st.button(
    "🚀 Analyze Resume & Job",
    type="primary",
    use_container_width=True
)


# ============================================================
# MAIN PIPELINE
# ============================================================

if analyze_button:

    if resume_file is None:

        st.error("❌ Please upload your resume PDF.")

        st.stop()

    if not job_description.strip():

        st.error("❌ Please enter the Job Description.")

        st.stop()


    # --------------------------------------------------------
    # SAVE TEMPORARY RESUME
    # --------------------------------------------------------

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(
                resume_file.getbuffer()
            )

            temp_path = temp_file.name


        # ====================================================
        # STEP 1 — RESUME PARSING
        # ====================================================

        with st.spinner("📄 Parsing resume..."):

            parser = ResumeParser()

            parsed_resume = parser.parse(
                temp_path
            )


        st.success("✅ Resume parsed successfully.")


        # ====================================================
        # EXTRACT RESUME TEXT
        # ====================================================

        if isinstance(parsed_resume, dict):

            resume_text = (
                parsed_resume.get("text")
                or parsed_resume.get("resume_text")
                or parsed_resume.get("content")
                or ""
            )

        else:

            resume_text = str(
                parsed_resume
            )


        # Fallback

        if not resume_text.strip():

            st.warning(
                "Resume text could not be extracted."
            )

            resume_text = ""


        # ====================================================
        # STEP 2 — JOB DESCRIPTION ANALYSIS
        # ====================================================

        with st.spinner(
            "🔍 Analyzing Job Description..."
        ):

            jd_analyzer = JDAnalyzer()

            jd_result = jd_analyzer.analyze(
                job_description
            )


        # ====================================================
        # JD INFORMATION
        # ====================================================

        job_title = jd_result.get(
            "job_title",
            "Target Position"
        )

        required_skills = jd_result.get(
            "skills",
            []
        )

        experience_required = jd_result.get(
            "experience_years",
            0
        )

        qualifications = jd_result.get(
            "qualifications",
            []
        )

        responsibilities = jd_result.get(
            "responsibilities",
            []
        )

        keywords = jd_result.get(
            "keywords",
            []
        )


        # ====================================================
        # STEP 3 — RESUME SKILLS
        # ====================================================

        with st.spinner(
            "🧠 Extracting resume skills..."
        ):

            resume_skills = extract_skills(
                resume_text
            )


        # ====================================================
        # STEP 4 — MATCHING
        # ====================================================

        with st.spinner(
            "🤖 Running ML semantic matching..."
        ):

            matcher = ResumeJobMatcher()

            match_result = matcher.match(
                resume_text,
                job_description
            )


        # ====================================================
        # MATCH RESULTS
        # ====================================================

        matched_skills = match_result.get(
            "matched_skills",
            []
        )

        missing_skills = match_result.get(
            "missing_skills",
            []
        )

        keyword_score = float(
            match_result.get(
                "keyword_score",
                0
            )
        )

        semantic_score = float(
            match_result.get(
                "semantic_score",
                0
            )
        )

        final_score = float(
            match_result.get(
                "final_match_score",
                match_result.get(
                    "final_score",
                    0
                )
            )
        )

        match_level = match_result.get(
            "match_level",
            "Unknown"
        )


        # ====================================================
        # RESULTS
        # ====================================================

        st.divider()

        st.header("📊 Resume Analysis Results")


        # ----------------------------------------------------
        # SCORE CARDS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "ATS Score",
                f"{final_score:.2f}%"
            )


        with col2:

            st.metric(
                "Semantic Score",
                f"{semantic_score:.2f}%"
            )


        with col3:

            st.metric(
                "Keyword Score",
                f"{keyword_score:.2f}%"
            )


        with col4:

            st.metric(
                "Match Level",
                match_level
            )


        # ====================================================
        # JOB INFORMATION
        # ====================================================

        st.subheader("🎯 Target Job")

        st.write(
            f"**Job Title:** {job_title}"
        )

        st.write(
            f"**Experience Required:** "
            f"{experience_required} years"
        )


        # ====================================================
        # SKILLS
        # ====================================================

        col1, col2 = st.columns(2)


        with col1:

            st.subheader(
                "✅ Matched Skills"
            )

            if matched_skills:

                for skill in matched_skills:

                    st.success(
                        f"✓ {skill}"
                    )

            else:

                st.write(
                    "No matched skills found."
                )


        with col2:

            st.subheader(
                "❌ Missing Skills"
            )

            if missing_skills:

                for skill in missing_skills:

                    st.error(
                        f"✗ {skill}"
                    )

            else:

                st.success(
                    "No major missing skills."
                )


        # ====================================================
        # JD DETAILS
        # ====================================================

        with st.expander(
            "🔎 View Job Description Analysis"
        ):

            st.write(
                "**Required Skills**"
            )

            st.write(
                ", ".join(required_skills)
                if required_skills
                else "None"
            )

            st.write(
                "**Qualifications**"
            )

            st.write(
                ", ".join(qualifications)
                if qualifications
                else "None"
            )

            st.write(
                "**Responsibilities**"
            )

            for responsibility in responsibilities:

                st.write(
                    f"• {responsibility}"
                )

            st.write(
                "**Important Keywords**"
            )

            st.write(
                ", ".join(keywords)
                if keywords
                else "None"
            )


        # ====================================================
        # STEP 5 — GAP ANALYSIS
        # ====================================================

        st.divider()

        st.header(
            "🔎 Skill Gap Analysis"
        )

        try:

            gap_analyzer = GapAnalyzer()

            gap_result = gap_analyzer.analyze(
                resume_skills,
                required_skills
            )

            gap_matched = gap_result.get(
                "matched_skills",
                matched_skills
            )

            gap_missing = gap_result.get(
                "missing_skills",
                missing_skills
            )

            critical_skills = gap_result.get(
                "critical_missing_skills",
                []
            )

            recommendations = gap_result.get(
                "recommendations",
                []
            )

        except Exception:

            gap_matched = matched_skills

            gap_missing = missing_skills

            critical_skills = []

            recommendations = []


        col1, col2 = st.columns(2)


        with col1:

            st.write(
                "### Matched"
            )

            for skill in gap_matched:

                st.write(
                    f"✓ {skill}"
                )


        with col2:

            st.write(
                "### Missing"
            )

            for skill in gap_missing:

                st.write(
                    f"✗ {skill}"
                )


        if critical_skills:

            st.warning(
                "⚠️ Critical Missing Skills: "
                + ", ".join(
                    critical_skills
                )
            )


        if recommendations:

            st.subheader(
                "💡 Recommendations"
            )

            for recommendation in recommendations:

                st.write(
                    f"• {recommendation}"
                )


        # ====================================================
        # STEP 6 — RESUME TAILORING
        # ====================================================

        st.divider()

        st.header(
            "✨ Tailored Resume"
        )


        with st.spinner(
            "✨ Creating tailored resume..."
        ):

            tailor = ResumeTailor()

            try:

                tailored_result = tailor.tailor(
                    resume_text,
                    jd_result
                )

            except Exception:

                tailored_result = None


        # ----------------------------------------------------
        # HANDLE TAILORING RESULT
        # ----------------------------------------------------

        if isinstance(
            tailored_result,
            dict
        ):

            tailored_resume = tailored_result

        else:

            tailored_resume = {

                "job_title": job_title,

                "professional_summary":
                    f"Results-oriented professional "
                    f"targeting a {job_title} role with "
                    f"practical knowledge of "
                    f"{', '.join(matched_skills)}.",

                "skills":
                    matched_skills,

                "experience":
                    [],

                "projects":
                    [],

                "education":
                    [],

                "certifications":
                    []

            }


        # ====================================================
        # DISPLAY TAILORED RESUME
        # ====================================================

        st.subheader(
            "Professional Summary"
        )

        st.write(
            tailored_resume.get(
                "professional_summary",
                ""
            )
        )


        st.subheader(
            "Skills"
        )

        skills_data = tailored_resume.get(
            "skills",
            {}
        )


        if isinstance(
            skills_data,
            dict
        ):

            for category, skills in skills_data.items():

                st.write(
                    f"**{category}:** "
                    + ", ".join(skills)
                )

        elif skills_data:

            st.write(
                ", ".join(skills_data)
                if isinstance(
                    skills_data,
                    list
                )
                else str(skills_data)
            )


        # ====================================================
        # EXPERIENCE
        # ====================================================

        st.subheader(
            "Experience"
        )

        experience_data = tailored_resume.get(
            "experience",
            []
        )

        if experience_data:

            for item in experience_data:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                "No experience details available."
            )


        # ====================================================
        # PROJECTS
        # ====================================================

        st.subheader(
            "Projects"
        )

        projects_data = tailored_resume.get(
            "projects",
            []
        )

        if projects_data:

            for project in projects_data:

                st.write(
                    f"• {project}"
                )

        else:

            st.write(
                "No projects available."
            )


        # ====================================================
        # EDUCATION
        # ====================================================

        st.subheader(
            "Education"
        )

        education_data = tailored_resume.get(
            "education",
            []
        )

        if education_data:

            for education in education_data:

                st.write(
                    f"• {education}"
                )

        else:

            st.write(
                "No education information available."
            )


        # ====================================================
        # CERTIFICATIONS
        # ====================================================

        st.subheader(
            "Certifications"
        )

        certifications_data = tailored_resume.get(
            "certifications",
            []
        )

        if certifications_data:

            for certificate in certifications_data:

                st.write(
                    f"• {certificate}"
                )

        else:

            st.write(
                "No certifications available."
            )


        # ====================================================
        # SAVE RESULTS IN SESSION
        # ====================================================

        st.session_state[
            "tailored_resume"
        ] = tailored_resume

        st.session_state[
            "job_title"
        ] = job_title

        st.session_state[
            "resume_text"
        ] = resume_text

        st.session_state[
            "job_description"
        ] = job_description


        # ====================================================
        # DOWNLOAD SECTION
        # ====================================================

        st.divider()

        st.header(
            "📥 Download Tailored Resume"
        )


        output_dir = BASE_DIR / "output"

        output_dir.mkdir(
            exist_ok=True
        )


        # ----------------------------------------------------
        # DOCX
        # ----------------------------------------------------

        docx_path = (
            output_dir
            / "Tailored_Resume.docx"
        )


        try:

            if ResumeGenerator:

                generator = ResumeGenerator()

                generated_resume = (
                    generator.generate_resume(
                        job_title=job_title,
                        skills=matched_skills,
                        experience=experience_required,
                        experience_details=
                            tailored_resume.get(
                                "experience",
                                []
                            ),
                        projects=
                            tailored_resume.get(
                                "projects",
                                []
                            ),
                        education=
                            tailored_resume.get(
                                "education",
                                []
                            ),
                        certifications=
                            tailored_resume.get(
                                "certifications",
                                []
                            )
                    )
                )

                # Some generators have different
                # saving methods, therefore only
                # use existing file if available.

                if docx_path.exists():

                    with open(
                        docx_path,
                        "rb"
                    ) as file:

                        st.download_button(
                            label=
                                "📄 Download DOCX",
                            data=file.read(),
                            file_name=
                                "Tailored_Resume.docx",
                            mime=
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

        except Exception as e:

            st.warning(
                f"DOCX generation requires the "
                f"existing generator configuration: {e}"
            )


        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        pdf_path = (
            output_dir
            / "Tailored_Resume.pdf"
        )


        if pdf_path.exists():

            with open(
                pdf_path,
                "rb"
            ) as file:

                st.download_button(
                    label=
                        "📕 Download PDF",
                    data=file.read(),
                    file_name=
                        "Tailored_Resume.pdf",
                    mime=
                        "application/pdf"
                )

        else:

            st.info(
                "PDF generator has not created the "
                "latest file yet."
            )


        # ====================================================
        # FINAL STATUS
        # ====================================================

        st.success(
            "🎉 Resume analysis and tailoring completed!"
        )


    except Exception as e:

        st.error(
            "❌ An error occurred while running "
            "the AI Resume Tailoring pipeline."
        )

        st.exception(e)


    finally:

        # ----------------------------------------------------
        # REMOVE TEMP FILE
        # ----------------------------------------------------

        if temp_path:

            try:

                os.remove(
                    temp_path
                )

            except Exception:

                pass


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Resume Tailoring System | "
    "Semantic Matching + ATS Analysis + Skill Gap Analysis"
)
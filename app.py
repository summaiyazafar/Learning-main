"""
AI Resume Tailoring System – Complete Standalone App
PDF is generated automatically after analysis.
"""

import os
import sys
import tempfile
import re
from pathlib import Path
import streamlit as st
from datetime import datetime

# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Tailoring System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# MODULE IMPORTS
# ============================================================

try:
    from modules.resume_parser import ResumeParser
except Exception as e:
    st.error(f"❌ ResumeParser import failed: {e}")
    st.stop()

try:
    from modules.jd_analyzer import JDAnalyzer
except Exception as e:
    st.error(f"❌ JDAnalyzer import failed: {e}")
    st.stop()

try:
    from modules.skill_extractor import extract_skills, compare_skills
except Exception as e:
    st.error(f"❌ Skill extractor import failed: {e}")
    st.stop()

try:
    from modules.matcher import ResumeJobMatcher
except Exception as e:
    st.error(f"❌ Matcher import failed: {e}")
    st.stop()

try:
    from modules.resume_tailor import ResumeTailor
except Exception as e:
    st.error(f"❌ ResumeTailor import failed: {e}")
    st.stop()

try:
    from modules.gap_analyzer import GapAnalyzer
except Exception:
    GapAnalyzer = None

# ============================================================
# PDF GENERATION (built-in)
# ============================================================

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def generate_pdf_resume(resume_data, job_title, output_path=None):
    """Generate a professional PDF resume using reportlab."""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required. Run: pip install reportlab")

    if output_path is None:
        output_path = Path("output/Tailored_Resume.pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=17*mm,
        leftMargin=17*mm,
        topMargin=13*mm,
        bottomMargin=14*mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='ResumeName',
        parent=styles['Title'],
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=3,
        textColor=colors.black
    ))
    styles.add(ParagraphStyle(
        name='ResumeTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=5,
        textColor=colors.black
    ))
    styles.add(ParagraphStyle(
        name='ContactLine',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=2,
        textColor=colors.black
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=3,
        textColor=colors.black,
        keepWithNext=True,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='BodyResume',
        parent=styles['BodyText'],
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='BulletResume',
        parent=styles['BodyText'],
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        leftIndent=12,
        firstLineIndent=0,
        spaceAfter=2
    ))

    story = []

    # ---- NAME ----
    name = resume_data.get('name', 'Candidate')
    story.append(Paragraph(name, styles['ResumeName']))

    # ---- JOB TITLE ----
    if job_title:
        story.append(Paragraph(job_title, styles['ResumeTitle']))

    # ---- CONTACT BLOCK ----
    # Line 1: Phone | Email
    contact_parts = []
    phone = resume_data.get('phone', '')
    email = resume_data.get('email', '')
    if phone:
        contact_parts.append(phone)
    if email:
        contact_parts.append(email)
    if contact_parts:
        story.append(Paragraph(' | '.join(contact_parts), styles['ContactLine']))

    # Line 2: Location
    location = resume_data.get('location', '')
    if location:
        story.append(Paragraph(location, styles['ContactLine']))

    # Line 3: Social links with labels
    social_parts = []
    linkedin = resume_data.get('linkedin', '')
    github = resume_data.get('github', '')
    kaggle = resume_data.get('kaggle', '')
    if linkedin:
        social_parts.append(f"LinkedIn: {linkedin}")
    if github:
        social_parts.append(f"GitHub: {github}")
    if kaggle:
        social_parts.append(f"Kaggle: {kaggle}")
    if social_parts:
        story.append(Paragraph(' | '.join(social_parts), styles['ContactLine']))

    story.append(HRFlowable(width="100%", thickness=0.8, spaceBefore=1, spaceAfter=8, color=colors.black))

    # ---- SUMMARY ----
    summary = resume_data.get('professional_summary', '')
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionHeading']))
        story.append(Paragraph(summary, styles['BodyResume']))

    # ---- SKILLS ----
    skills = resume_data.get('skills', [])
    if skills:
        story.append(Paragraph("SKILLS", styles['SectionHeading']))
        if isinstance(skills, list):
            skill_text = ', '.join(skills)
            story.append(Paragraph(skill_text, styles['BodyResume']))
        elif isinstance(skills, dict):
            for cat, skill_list in skills.items():
                if skill_list:
                    story.append(Paragraph(f"<b>{cat}:</b> {', '.join(skill_list)}", styles['BodyResume']))

    # ---- EXPERIENCE ----
    exp = resume_data.get('experience', [])
    if exp:
        story.append(Paragraph("EXPERIENCE", styles['SectionHeading']))
        if isinstance(exp, list):
            for item in exp:
                if isinstance(item, dict):
                    title = item.get('title', '')
                    company = item.get('company', '')
                    dates = item.get('dates', '')
                    bullets = item.get('bullets', [])
                    if title or company:
                        story.append(Paragraph(f"<b>{title}</b> | {company} {dates if dates else ''}".strip(), styles['BodyResume']))
                    if bullets:
                        bullet_items = []
                        for b in bullets:
                            bullet_items.append(ListItem(Paragraph(b, styles['BulletResume']), leftIndent=8))
                        story.append(ListFlowable(bullet_items, bulletType='bullet', start='circle', leftIndent=15, bulletFontSize=6))
                else:
                    story.append(Paragraph(f"• {item}", styles['BodyResume']))

    # ---- PROJECTS ----
    projects = resume_data.get('projects', [])
    if projects:
        story.append(Paragraph("PROJECTS", styles['SectionHeading']))
        if isinstance(projects, list):
            for proj in projects:
                if isinstance(proj, dict):
                    name = proj.get('name', '')
                    desc = proj.get('description', '')
                    tech = proj.get('technologies', [])
                    if name:
                        story.append(Paragraph(f"<b>{name}</b>", styles['BodyResume']))
                    if desc:
                        story.append(Paragraph(desc, styles['BodyResume']))
                    if tech:
                        story.append(Paragraph(f"<i>Technologies:</i> {', '.join(tech)}", styles['BodyResume']))
                else:
                    story.append(Paragraph(f"• {proj}", styles['BodyResume']))

    # ---- EDUCATION ----
    edu = resume_data.get('education', '')
    if edu:
        story.append(Paragraph("EDUCATION", styles['SectionHeading']))
        if isinstance(edu, list):
            for item in edu:
                story.append(Paragraph(f"• {item}", styles['BodyResume']))
        else:
            story.append(Paragraph(edu, styles['BodyResume']))

    # ---- CERTIFICATIONS ----
    certs = resume_data.get('certifications', '')
    if certs:
        story.append(Paragraph("CERTIFICATIONS", styles['SectionHeading']))
        if isinstance(certs, list):
            for c in certs:
                story.append(Paragraph(f"• {c}", styles['BodyResume']))
        else:
            story.append(Paragraph(certs, styles['BodyResume']))

    doc.build(story)
    return output_path

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()

def safe_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [clean_text(x) for x in value if clean_text(x)]
    if isinstance(value, str):
        return [clean_text(x) for x in value.splitlines() if clean_text(x)]
    return [clean_text(value)] if clean_text(value) else []

def normalize_score(value):
    try:
        v = float(value)
        if 0 <= v <= 1:
            v *= 100
        return max(0.0, min(100.0, v))
    except:
        return 0.0

def get_match_level(score):
    s = normalize_score(score)
    if s >= 85:
        return "Excellent Match"
    if s >= 70:
        return "Strong Match"
    if s >= 55:
        return "Good Match"
    if s >= 40:
        return "Moderate Match"
    return "Low Match"

def display_skill_list(skills, matched=True):
    skills = safe_list(skills)
    if not skills:
        if matched:
            st.info("No matched skills found.")
        else:
            st.success("No missing skills detected.")
        return
    symbol = "✓" if matched else "✗"
    for skill in skills:
        st.markdown(f"**{symbol}** {skill}")

def display_resume_items(items):
    items = safe_list(items)
    if not items:
        st.info("No information available.")
        return
    for item in items:
        if isinstance(item, dict):
            title = item.get('title') or item.get('name') or ''
            desc = item.get('description') or item.get('details') or ''
            if title:
                st.markdown(f"**{clean_text(title)}**")
            if desc:
                st.write(f"  {clean_text(desc)}")
        else:
            st.write(f"• {clean_text(item)}")

# ============================================================
# CACHED COMPONENTS
# ============================================================

@st.cache_resource
def get_matcher():
    return ResumeJobMatcher()

@st.cache_resource
def get_tailor():
    return ResumeTailor()

# ============================================================
# UI
# ============================================================

st.markdown("""
    <style>
    .hero { background: linear-gradient(135deg, #111827 0%, #1e3a5f 100%); padding: 2rem; border-radius: 20px; margin-bottom: 1.5rem; }
    .hero-title { color: white; font-size: 2rem; font-weight: 800; }
    .hero-subtitle { color: #dbeafe; font-size: 1rem; }
    .section-title { font-size: 1.3rem; font-weight: 700; color: #1e3a5f; margin-top: 1.5rem; margin-bottom: 0.5rem; }
    .protected-box { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 1rem; margin: 1rem 0; }
    .protected-title { color: #1d4ed8; font-weight: 700; }
    .validation-success { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 1rem; color: #166534; font-weight: 600; }
    .download-box { background: #f0fdf4; border: 2px solid #22c55e; border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0; }
    .download-box-title { font-size: 1.2rem; font-weight: 700; color: #15803d; }
    .score-card { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; text-align: center; }
    .score-value { font-size: 1.8rem; font-weight: 800; color: #111827; }
    .score-label { color: #64748b; font-size: 0.8rem; font-weight: 600; }
    .stButton > button { border-radius: 10px; font-weight: 700; min-height: 44px; }
    </style>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
    <div class="hero">
        <div class="hero-title">🤖 AI Resume Tailoring System</div>
        <div class="hero-subtitle">ML/DL-powered Resume Analysis, Semantic Matching, ATS Optimization & Skill Gap Analysis</div>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR – Protected Information Manual Input
# ============================================================

with st.sidebar:
    st.markdown("### 🔒 Protected Information")
    st.caption("Enter your personal details (these will be used in the final resume).")

    name = st.text_input("Full Name", placeholder="e.g., Summaiya Bibi")
    phone = st.text_input("Phone", placeholder="+92 300 1234567")
    email = st.text_input("Email", placeholder="summaiya@example.com")
    linkedin = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/yourprofile")
    github = st.text_input("GitHub URL", placeholder="https://github.com/yourusername")
    kaggle = st.text_input("Kaggle URL", placeholder="https://kaggle.com/yourusername")
    location = st.text_input("Location", placeholder="Islamabad, Pakistan")
    education = st.text_area("Education (one per line)", placeholder="BS Computer Science\nVirtual University of Pakistan\n2021–2025")
    certifications = st.text_area("Certifications (one per line)", placeholder="Machine Learning Specialization\nGenerative AI Specialization")

    st.caption("These fields are **never** generated by AI – they are copied exactly as you type them.")

# ============================================================
# MAIN INPUT
# ============================================================

st.markdown('<div class="section-title">1️⃣ Upload Your Master Resume</div>', unsafe_allow_html=True)
resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

st.markdown('<div class="section-title">2️⃣ Enter Target Job Description</div>', unsafe_allow_html=True)
job_description = st.text_area("Paste the complete Job Description here", height=250)

st.markdown("""
    <div class="protected-box">
        <div class="protected-title">🔒 Resume Protection Policy</div>
        <div style="color:#475569;font-size:0.9rem;">
            The information you enter in the sidebar is used as your protected data.
            <br><b>Missing JD skills are reported separately and are NOT added to your resume.</b>
        </div>
    </div>
""", unsafe_allow_html=True)

analyze_button = st.button("🚀 Analyze & Tailor Resume", type="primary", use_container_width=True)

# ============================================================
# MAIN PIPELINE
# ============================================================

if analyze_button:
    if resume_file is None:
        st.error("⚠️ Please upload your resume PDF.")
        st.stop()
    if not job_description.strip():
        st.error("⚠️ Please enter the job description.")
        st.stop()

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(resume_file.getbuffer())
            temp_path = f.name

        # ---------- PARSE RESUME ----------
        st.divider()
        st.markdown('<div class="section-title">🔍 Step 1 — Resume Parsing</div>', unsafe_allow_html=True)
        parser = ResumeParser()
        with st.spinner("Parsing resume..."):
            if hasattr(parser, "parse_resume"):
                parsed = parser.parse_resume(temp_path)
            else:
                text = parser.parse(temp_path)
                if hasattr(parser, "extract_information"):
                    parsed = parser.extract_information(text)
                else:
                    parsed = {"text": text}

        if not isinstance(parsed, dict):
            parsed = {"text": str(parsed)}

        resume_text = parsed.get("text") or parsed.get("resume_text") or ""
        if not resume_text:
            st.error("Could not extract text from resume.")
            st.stop()

        st.success("✅ Resume parsed successfully.")

        # ---------- PROTECTED DATA – use manual input or fallback ----------
        protected = {
            "name": name.strip() or parsed.get("name", "Candidate"),
            "phone": phone.strip() or parsed.get("phone", ""),
            "email": email.strip() or parsed.get("email", ""),
            "linkedin": linkedin.strip() or parsed.get("linkedin", ""),
            "github": github.strip() or parsed.get("github", ""),
            "kaggle": kaggle.strip() or parsed.get("kaggle", ""),
            "location": location.strip() or parsed.get("location", ""),
            "education": education.strip() or parsed.get("education", ""),
            "certifications": certifications.strip() or parsed.get("certifications", ""),
        }

        with st.expander("🔒 Protected Information Used"):
            for k, v in protected.items():
                st.write(f"**{k.capitalize()}:** {v if v else '—'}")

        # ---------- JD ANALYSIS ----------
        st.markdown('<div class="section-title">📝 Step 2 — Job Description Analysis</div>', unsafe_allow_html=True)
        with st.spinner("Analyzing JD..."):
            jd_analyzer = JDAnalyzer()
            jd_result = jd_analyzer.analyze(job_description) if hasattr(jd_analyzer, "analyze") else {}

        job_title = jd_result.get("job_title") or "Target Position"
        st.success(f"✅ Target position: {job_title}")

        # ---------- SKILL EXTRACTION ----------
        st.markdown('<div class="section-title">🧠 Step 3 — Skill Extraction</div>', unsafe_allow_html=True)
        with st.spinner("Extracting skills..."):
            resume_skills = safe_list(extract_skills(resume_text))
            skill_comp = compare_skills(resume_text, job_description) or {}
            matched_skills = safe_list(skill_comp.get("matched_skills", []))
            missing_skills = safe_list(skill_comp.get("missing_skills", []))
            keyword_score = normalize_score(skill_comp.get("match_percentage", 0))

        # ---------- SEMANTIC MATCHING ----------
        st.markdown('<div class="section-title">🔗 Step 4 — Semantic & ML Matching</div>', unsafe_allow_html=True)
        with st.spinner("Running matcher..."):
            matcher = get_matcher()
            if hasattr(matcher, "match"):
                match_result = matcher.match(resume_text, job_description)
            else:
                match_result = {}
        semantic_score = normalize_score(match_result.get("semantic_score", 0))
        final_score = normalize_score(match_result.get("final_score", keyword_score))
        match_level = get_match_level(final_score)

        # ---------- TAILOR RESUME ----------
        st.markdown('<div class="section-title">✨ Step 5 — Resume Tailoring</div>', unsafe_allow_html=True)
        with st.spinner("Tailoring resume..."):
            tailor = get_tailor()
            tailored = tailor.tailor(parsed, jd_result)

        if not isinstance(tailored, dict):
            tailored = {}

        # Force our protected data
        for k, v in protected.items():
            tailored[k] = v
        # Explicitly set phone/email again to be safe
        tailored["phone"] = phone.strip() or tailored.get("phone", "")
        tailored["email"] = email.strip() or tailored.get("email", "")

        candidate_skills = [s for s in safe_list(resume_skills) if s.lower() not in {m.lower() for m in safe_list(missing_skills)}]
        tailored["skills"] = candidate_skills
        tailored["matched_skills"] = matched_skills
        tailored["missing_skills"] = missing_skills
        tailored["job_title"] = job_title

        # ---------- DISPLAY RESULTS ----------
        st.divider()
        st.markdown('<div class="section-title">📊 Resume Analysis Results</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        with cols[0]:
            st.markdown(f"""<div class="score-card"><div class="score-label">🎯 ATS Score</div><div class="score-value">{final_score:.1f}%</div></div>""", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""<div class="score-card"><div class="score-label">🔗 Semantic</div><div class="score-value">{semantic_score:.1f}%</div></div>""", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"""<div class="score-card"><div class="score-label">🧠 Skill Match</div><div class="score-value">{keyword_score:.1f}%</div></div>""", unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f"""<div class="score-card"><div class="score-label">📈 Match Level</div><div class="score-value" style="font-size:1.1rem;">{match_level}</div></div>""", unsafe_allow_html=True)

        # Skills
        st.markdown('<div class="section-title">🎯 Skill Matching</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Matched Skills**")
            display_skill_list(matched_skills, matched=True)
        with c2:
            st.markdown("**❌ Missing Skills**")
            display_skill_list(missing_skills, matched=False)

        st.markdown('<div class="section-title">📈 Skill Gap Summary</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.metric("Resume Skills", len(resume_skills))
        with g2:
            st.metric("Matched Skills", len(matched_skills))
        with g3:
            st.metric("Missing Skills", len(missing_skills))

        if missing_skills:
            st.warning("⚠️ Missing skills are shown only for gap analysis. They are NOT added to your resume.")

        # ---------- TAILORED RESUME PREVIEW ----------
        st.divider()
        st.markdown('<div class="section-title">📄 Tailored Resume Preview</div>', unsafe_allow_html=True)

        name_display = clean_text(tailored.get("name", "Candidate"))
        st.markdown(f"## {name_display}")
        st.caption(f"🎯 {job_title}")

        contact = []
        for key in ["phone", "email", "location"]:
            val = clean_text(tailored.get(key, ""))
            if val:
                contact.append(val)
        if contact:
            st.write(" • ".join(contact))

        social = []
        for key in ["linkedin", "github", "kaggle"]:
            val = clean_text(tailored.get(key, ""))
            if val:
                social.append(val)
        if social:
            st.write(" • ".join(social))

        st.markdown("### Professional Summary")
        summary = clean_text(tailored.get("professional_summary", ""))
        st.write(summary if summary else "No summary available.")

        st.markdown("### Skills")
        if candidate_skills:
            st.write(", ".join(candidate_skills))
        else:
            st.info("No skills available.")

        st.markdown("### Professional Experience")
        display_resume_items(tailored.get("experience", []))

        st.markdown("### Projects")
        display_resume_items(tailored.get("projects", []))

        st.markdown("### Education 🔒")
        edu = tailored.get("education")
        if edu:
            if isinstance(edu, list):
                for item in edu:
                    st.write(f"• {clean_text(item)}")
            else:
                st.write(clean_text(edu))
        else:
            st.info("No education listed.")

        st.markdown("### Certifications 🔒")
        certs = tailored.get("certifications")
        if certs:
            if isinstance(certs, list):
                for item in certs:
                    st.write(f"• {clean_text(item)}")
            else:
                st.write(clean_text(certs))
        else:
            st.info("No certifications listed.")

        # ---------- DOWNLOAD SECTION – PDF PRIMARY ----------
        st.divider()
        st.markdown('<div class="section-title">📥 Download Your Tailored Resume</div>', unsafe_allow_html=True)

        # ---- BUILD TXT CONTENT (always defined) ----
        def format_txt_list(items):
            if not items:
                return "None"
            if isinstance(items, list):
                return "\n".join([f"• {clean_text(item)}" for item in items if clean_text(item)])
            return clean_text(items)

        txt_content = f"""
================================================================================
                          TAILORED RESUME
================================================================================

PERSONAL INFORMATION (PROTECTED – UNCHANGED)
---------------------------------------------
Name         : {clean_text(tailored.get('name', ''))}
Phone        : {clean_text(tailored.get('phone', ''))}
Email        : {clean_text(tailored.get('email', ''))}
LinkedIn     : {clean_text(tailored.get('linkedin', ''))}
GitHub       : {clean_text(tailored.get('github', ''))}
Kaggle       : {clean_text(tailored.get('kaggle', ''))}
Location     : {clean_text(tailored.get('location', ''))}

JOB TARGET
---------------------------------------------
Job Title    : {clean_text(job_title)}
Experience Required: {jd_result.get('experience_years', 0)} years

PROFESSIONAL SUMMARY
---------------------------------------------
{clean_text(tailored.get('professional_summary', 'N/A'))}

SKILLS
---------------------------------------------
{', '.join(candidate_skills) if candidate_skills else 'None'}

PROJECTS
---------------------------------------------
{format_txt_list(tailored.get('projects', []))}

EXPERIENCE
---------------------------------------------
{format_txt_list(tailored.get('experience', []))}

EDUCATION (PROTECTED)
---------------------------------------------
{format_txt_list(tailored.get('education', []))}

CERTIFICATIONS (PROTECTED)
---------------------------------------------
{format_txt_list(tailored.get('certifications', []))}

================================================================================
MATCHED SKILLS: {', '.join(matched_skills) if matched_skills else 'None'}
MISSING SKILLS: {', '.join(missing_skills) if missing_skills else 'None'}
================================================================================
"""

        if not REPORTLAB_AVAILABLE:
            st.warning("⚠️ PDF generation requires reportlab. Run: pip install reportlab")
            st.markdown("""
                <div class="download-box">
                    <div class="download-box-title">📝 Download as Text File</div>
                    <p style="color:#475569;">PDF not available – download TXT instead.</p>
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Download TXT Resume",
                data=txt_content,
                file_name=f"Tailored_Resume_{clean_text(tailored.get('name', 'Candidate')).replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_txt_primary"
            )
        else:
            # ---- Generate PDF automatically ----
            with st.spinner("Generating professional PDF..."):
                try:
                    pdf_path = Path("output/Tailored_Resume.pdf")
                    generate_pdf_resume(tailored, job_title, pdf_path)
                    if pdf_path.exists():
                        with open(pdf_path, "rb") as f:
                            pdf_data = f.read()

                        st.markdown("""
                            <div class="download-box" style="border-color:#1e3a5f; background:#eff6ff;">
                                <div class="download-box-title" style="color:#1e3a5f;">📄 Download Professional PDF Resume</div>
                                <p style="color:#475569;">Your tailored resume as a professional PDF – ready to send to employers.</p>
                            </div>
                        """, unsafe_allow_html=True)

                        st.download_button(
                            label="⬇️ Download PDF Resume (Recommended)",
                            data=pdf_data,
                            file_name=f"Tailored_Resume_{clean_text(tailored.get('name', 'Candidate')).replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="download_pdf_primary"
                        )

                        st.markdown("""
                            <p style="color:#94a3b8;font-size:0.8rem;margin-top:0.5rem;">
                                <b>Need a text version?</b> Click below for TXT fallback.
                            </p>
                        """, unsafe_allow_html=True)

                        with st.expander("📝 Download TXT (fallback)"):
                            st.download_button(
                                label="⬇️ Download TXT",
                                data=txt_content,
                                file_name=f"Tailored_Resume_{clean_text(tailored.get('name', 'Candidate')).replace(' ', '_')}.txt",
                                mime="text/plain",
                                use_container_width=True,
                                key="download_txt_fallback"
                            )
                    else:
                        st.error("❌ PDF generation failed.")
                        st.download_button(
                            label="⬇️ Download TXT (fallback)",
                            data=txt_content,
                            file_name=f"Tailored_Resume_{clean_text(tailored.get('name', 'Candidate')).replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key="download_txt_fallback_error"
                        )
                except Exception as e:
                    st.error(f"❌ PDF generation error: {e}")
                    st.download_button(
                        label="⬇️ Download TXT (fallback)",
                        data=txt_content,
                        file_name=f"Tailored_Resume_{clean_text(tailored.get('name', 'Candidate')).replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key="download_txt_fallback_error2"
                    )

        st.success("🎉 Resume analysis and tailoring completed successfully!")

    except Exception as e:
        st.error(f"❌ Error: {e}")
        import traceback
        with st.expander("🔧 Details"):
            st.code(traceback.format_exc())

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
    <div style="text-align:center;color:#94a3b8;font-size:0.8rem;padding-top:2rem;">
        AI Resume Tailoring System &bull; Sentence Transformers &bull; Semantic Matching &bull; ML/DL
    </div>
""", unsafe_allow_html=True)
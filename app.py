import streamlit as st
from src.pdf_parser import extract_text_from_pdf

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.title("📄 AI Resume Analyzer & ATS Score")

st.markdown("""
Analyze your resume against any job description using AI.

### Features
- 📄 Resume Upload
- 💼 Job Description Analysis
- 📊 ATS Score
- 🧠 Skill Matching
- 🤖 AI Feedback
- 📈 Resume Improvement Suggestions
""")

st.divider()

# -----------------------------
# Upload Resume
# -----------------------------
resume_file = st.file_uploader(
    "📄 Upload Your Resume (PDF)",
    type=["pdf"]
)

# -----------------------------
# Job Description
# -----------------------------
job_description = st.text_area(
    "💼 Paste Job Description",
    height=220,
    placeholder="Paste the complete job description here..."
)

# -----------------------------
# Analyze Button
# -----------------------------
if st.button("🚀 Analyze Resume"):

    if resume_file is None:
        st.warning("Please upload your resume.")
        st.stop()

    if job_description.strip() == "":
        st.warning("Please paste a job description.")
        st.stop()

    # Extract Resume Text
    resume_text, total_pages = extract_text_from_pdf(resume_file)

    st.success("✅ Resume analyzed successfully!")

    st.divider()

    # Dashboard
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Total Pages", total_pages)

    with col2:
        st.metric("📝 Total Words", len(resume_text.split()))

    with col3:
        st.metric("🔤 Total Characters", len(resume_text))

    st.divider()

    st.subheader("📄 Resume Information")

    st.write("**Uploaded File:**", resume_file.name)

    st.text_area(
        "Extracted Resume Text",
        value=resume_text,
        height=450
    )

    st.download_button(
        label="📥 Download Resume Text",
        data=resume_text,
        file_name="resume.txt",
        mime="text/plain"
    )
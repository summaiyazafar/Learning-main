import streamlit as st
import fitz
import re


st.set_page_config(
    page_title="AI Career Interviewer",
    page_icon="🤖",
    layout="wide"
)


st.title("🤖 AI Career Interviewer")
st.subheader("AI-Powered Live Interview & Career Assessment Platform")

st.write(
    "Upload your resume to begin your AI-powered career assessment."
)

st.divider()

# Resume Upload
st.header("📄 Step 1: Upload Your Resume")

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"]
)


def extract_resume_text(pdf_file):
    """Extract text from uploaded PDF."""
    
    text = ""

    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

    for page in pdf_document:
        text += page.get_text()

    pdf_document.close()

    return text


def extract_skills(text):
    """Extract common technical skills from resume text."""

    skill_list = [
        "Python",
        "SQL",
        "Excel",
        "Power BI",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Pandas",
        "NumPy",
        "NLP",
        "OpenCV",
        "LangChain",
        "RAG",
        "Docker",
        "AWS",
        "FastAPI",
        "Flask",
        "Streamlit",
        "Git",
        "GitHub"
    ]

    found_skills = []

    text_lower = text.lower()

    for skill in skill_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


if uploaded_file is not None:

    st.success("Resume uploaded successfully! ✅")

    resume_text = extract_resume_text(uploaded_file)

    if resume_text.strip():

        st.header("📋 Extracted Resume Information")

        with st.expander("View Resume Text"):
            st.write(resume_text)

        skills = extract_skills(resume_text)

        st.subheader("🧠 Detected Skills")

        if skills:

            cols = st.columns(3)

            for index, skill in enumerate(skills):
                with cols[index % 3]:
                    st.success(f"✓ {skill}")

        else:
            st.warning(
                "No predefined technical skills were detected."
            )

    else:

        st.error(
            "Could not extract text from this PDF. "
            "Please upload a text-based PDF resume."
        )
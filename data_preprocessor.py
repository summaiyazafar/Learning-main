"""
Data Preprocessor for Resume and Job Description Datasets
"""

import pandas as pd
import os
import re
import html

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)


def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode HTML entities
    text = html.unescape(text)
    # Replace escaped characters
    text = text.replace("\\n", " ")
    text = text.replace("\\t", " ")
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills_from_text(text):
    """Extract technical skills from text."""
    skill_patterns = [
        r'\b(Python|Java|C\+\+|JavaScript|TypeScript|SQL|R|Scala|Go|Ruby|PHP)\b',
        r'\b(Machine Learning|Deep Learning|NLP|Computer Vision|AI|Data Science)\b',
        r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Matplotlib)\b',
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI/CD)\b',
        r'\b(React|Angular|Vue|Node\.js|Django|Flask|FastAPI|Spring Boot)\b',
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|Cassandra)\b',
        r'\b(Hadoop|Spark|Kafka|Airflow|Tableau|Power BI)\b'
    ]
    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)
    return list(set(skills))


def process_resumes():
    input_file = os.path.join(RAW_DIR, "Resume.csv")
    output_file = os.path.join(PROCESSED_DIR, "resumes_clean.csv")

    print("\nProcessing Resume.csv...")

    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found. Skipping.")
        return

    df = pd.read_csv(input_file, encoding="utf-8", low_memory=False)
    print("Original shape:", df.shape)

    possible_columns = ["Resume", "resume", "Resume_str", "resume_str", "Resume_html", "resume_html"]
    resume_column = None
    for col in possible_columns:
        if col in df.columns:
            resume_column = col
            break

    if resume_column is None:
        object_columns = df.select_dtypes(include=["object"]).columns
        if len(object_columns) > 0:
            resume_column = object_columns[0]
        else:
            raise ValueError("Could not find resume text column.")

    print("Using resume column:", resume_column)

    df["resume_text"] = df[resume_column].apply(clean_text)
    df["extracted_skills"] = df["resume_text"].apply(extract_skills_from_text)

    # Remove empty resumes
    df = df[df["resume_text"].str.len() > 20]

    output_columns = ["resume_text", "extracted_skills"]
    for col in ["Category", "category", "Job Title", "job_title"]:
        if col in df.columns:
            output_columns.append(col)

    df = df[output_columns]
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Clean resumes saved to: {output_file}")
    print("Processed shape:", df.shape)


def process_jobs():
    input_file = os.path.join(RAW_DIR, "job_descriptions.csv")
    output_file = os.path.join(PROCESSED_DIR, "jobs_clean.csv")

    print("\nProcessing job_descriptions.csv...")

    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found. Skipping.")
        return

    required_columns = ["Job Id", "Experience", "Qualifications", "location", "Country",
                        "Work Type", "Job Title", "Role", "Job Description", "skills",
                        "Responsibilities", "Company"]
    header = pd.read_csv(input_file, nrows=0)
    available_columns = [col for col in required_columns if col in header.columns]
    print("Using columns:", available_columns)

    first_chunk = True
    for chunk_number, chunk in enumerate(pd.read_csv(input_file, usecols=available_columns,
                                                     chunksize=10000, low_memory=False)):
        print(f"Processing job chunk {chunk_number + 1}...")
        text_columns = ["Job Description", "skills", "Responsibilities"]
        existing_text_columns = [col for col in text_columns if col in chunk.columns]

        for col in existing_text_columns:
            chunk[col] = chunk[col].apply(clean_text)

        chunk["job_text"] = ""
        for col in existing_text_columns:
            chunk["job_text"] += " " + chunk[col]
        chunk["job_text"] = chunk["job_text"].apply(clean_text)

        chunk = chunk[chunk["job_text"].str.len() > 20]

        output_columns = [col for col in ["Job Id", "Experience", "Qualifications",
                                          "location", "Country", "Work Type", "Job Title",
                                          "Role", "Company", "job_text"] if col in chunk.columns]
        chunk = chunk[output_columns]

        chunk.to_csv(output_file, mode="w" if first_chunk else "a",
                     header=first_chunk, index=False, encoding="utf-8")
        first_chunk = False

    print(f"Clean jobs saved to: {output_file}")


if __name__ == "__main__":
    print("=" * 60)
    print("AI RESUME TAILORING SYSTEM")
    print("DATA PREPROCESSING")
    print("=" * 60)
    process_resumes()
    process_jobs()
    print("\nDATA PREPROCESSING COMPLETED!")
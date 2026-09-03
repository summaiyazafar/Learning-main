"""
AI Resume Tailoring System
==========================

Data Preprocessor
-----------------
Cleans and prepares:

1. Resume.csv
2. job_descriptions.csv

Output:
    data/processed/resumes_clean.csv
    data/processed/jobs_clean.csv

Important:
- Large job dataset is processed in chunks.
- Resume skills are extracted using skill_extractor.
- Job skills are NOT pre-extracted here because JDAnalyzer
  handles job-description skill extraction later.
- No personal resume information is modified.
"""

import os
import re
import html
import sys

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ============================================================
# IMPORT ADVANCED SKILL EXTRACTOR
# ============================================================

try:
    from modules.skill_extractor import extract_skills as advanced_extract_skills

    SKILL_EXTRACTOR_AVAILABLE = True

except Exception as e:
    SKILL_EXTRACTOR_AVAILABLE = False
    advanced_extract_skills = None

    print(
        f"Warning: Advanced skill extractor could not be loaded.\n"
        f"Reason: {e}\n"
        f"Fallback skill extraction will be used."
    )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Clean raw text.

    Operations:
    - Handle missing values
    - Convert to string
    - Remove HTML tags
    - Decode HTML entities
    - Replace escaped newline/tab characters
    - Normalize whitespace
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # --------------------------------------------------------
    # Remove HTML tags
    # --------------------------------------------------------

    text = re.sub(r"<[^>]+>", " ", text)

    # --------------------------------------------------------
    # Decode HTML entities
    # Example: &amp; -> &
    # --------------------------------------------------------

    text = html.unescape(text)

    # --------------------------------------------------------
    # Replace escaped characters
    # --------------------------------------------------------

    text = text.replace("\\n", " ")
    text = text.replace("\\r", " ")
    text = text.replace("\\t", " ")

    # Also handle actual newline/tab characters
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")

    # --------------------------------------------------------
    # Remove repeated whitespace
    # --------------------------------------------------------

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# FALLBACK SKILL EXTRACTION
# ============================================================

def fallback_extract_skills(text):
    """
    Lightweight fallback skill extractor.

    Used only when the advanced skill_extractor module
    cannot be imported or fails.
    """

    if not text:
        return []

    skill_patterns = [
        # Programming
        r"\b(Python|Java|C\+\+|JavaScript|TypeScript|SQL|R|Scala|Go|Ruby|PHP)\b",

        # Data / AI
        r"\b(Machine Learning|Deep Learning|NLP|Natural Language Processing|Computer Vision|AI|Artificial Intelligence|Data Science)\b",

        # ML frameworks
        r"\b(TensorFlow|PyTorch|Keras|Scikit-learn|Scikit Learn|Pandas|NumPy|SciPy|Matplotlib|Seaborn)\b",

        # Cloud / DevOps
        r"\b(AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Jenkins|Git|GitHub|CI/CD)\b",

        # Web
        r"\b(React|Angular|Vue|Node\.js|Django|Flask|FastAPI|Spring Boot)\b",

        # Databases
        r"\b(MySQL|PostgreSQL|SQL Server|Microsoft SQL Server|MongoDB|Redis|Elasticsearch|Cassandra|Oracle|SQLite)\b",

        # Data Engineering / BI
        r"\b(Hadoop|Spark|PySpark|Kafka|Airflow|Tableau|Power BI|Power Query|Power Pivot|Excel)\b",

        # GenAI
        r"\b(LangChain|LlamaIndex|RAG|Retrieval Augmented Generation|LLM|LLMs|Generative AI|Prompt Engineering|OpenAI|FAISS|Pinecone)\b",
    ]

    skills = []

    for pattern in skill_patterns:
        try:
            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            skills.extend(matches)

        except re.error:
            continue

    # --------------------------------------------------------
    # Normalize and remove duplicates
    # --------------------------------------------------------

    unique_skills = []
    seen = set()

    for skill in skills:

        if isinstance(skill, tuple):
            skill = skill[0]

        skill = str(skill).strip()

        key = skill.lower()

        if key not in seen:
            seen.add(key)
            unique_skills.append(skill)

    return unique_skills


# ============================================================
# ADVANCED SKILL EXTRACTION
# ============================================================

def extract_skills_from_text(text):
    """
    Extract skills from text.

    First attempts to use the project's advanced
    skill_extractor module.

    If that fails, uses the lightweight fallback.
    """

    if not text:
        return []

    # --------------------------------------------------------
    # Advanced extractor
    # --------------------------------------------------------

    if SKILL_EXTRACTOR_AVAILABLE:

        try:
            skills = advanced_extract_skills(text)

            if skills is None:
                return []

            if isinstance(skills, str):
                return [skills]

            return list(skills)

        except Exception as e:

            print(
                f"Warning: Advanced skill extraction failed. "
                f"Using fallback extractor. Reason: {e}"
            )

    # --------------------------------------------------------
    # Fallback extractor
    # --------------------------------------------------------

    return fallback_extract_skills(text)


# ============================================================
# FIND RESUME TEXT COLUMN
# ============================================================

def find_resume_column(df):
    """
    Automatically detect the resume text column.
    """

    possible_columns = [
        "Resume",
        "resume",
        "Resume_str",
        "resume_str",
        "Resume_html",
        "resume_html",
        "Text",
        "text",
        "resume_text",
    ]

    # --------------------------------------------------------
    # Preferred columns
    # --------------------------------------------------------

    for column in possible_columns:

        if column in df.columns:
            return column

    # --------------------------------------------------------
    # Fallback to object column
    # --------------------------------------------------------

    object_columns = df.select_dtypes(
        include=["object"]
    ).columns

    if len(object_columns) > 0:

        selected_column = object_columns[0]

        print(
            f"Warning: No standard resume column found. "
            f"Using '{selected_column}'."
        )

        return selected_column

    raise ValueError(
        "Could not find a resume text column in Resume.csv."
    )


# ============================================================
# PROCESS RESUME DATASET
# ============================================================

def process_resumes():
    """
    Process Resume.csv.

    Input:
        data/raw/Resume.csv

    Output:
        data/processed/resumes_clean.csv
    """

    input_file = os.path.join(
        RAW_DIR,
        "Resume.csv"
    )

    output_file = os.path.join(
        PROCESSED_DIR,
        "resumes_clean.csv"
    )

    print("\n" + "=" * 60)
    print("PROCESSING RESUME DATASET")
    print("=" * 60)

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not os.path.exists(input_file):

        print(
            f"Warning: Resume dataset not found:\n"
            f"{input_file}"
        )

        return False

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    print(f"Input file: {input_file}")

    try:

        df = pd.read_csv(
            input_file,
            encoding="utf-8",
            low_memory=False
        )

    except UnicodeDecodeError:

        print(
            "UTF-8 decoding failed. "
            "Trying latin-1 encoding..."
        )

        df = pd.read_csv(
            input_file,
            encoding="latin-1",
            low_memory=False
        )

    print("Original shape:", df.shape)
    print("Original columns:", list(df.columns))

    # --------------------------------------------------------
    # Find resume column
    # --------------------------------------------------------

    resume_column = find_resume_column(df)

    print(
        f"Using resume column: {resume_column}"
    )

    # --------------------------------------------------------
    # Clean resume text
    # --------------------------------------------------------

    df["resume_text"] = df[
        resume_column
    ].apply(clean_text)

    # --------------------------------------------------------
    # Remove empty resumes
    # --------------------------------------------------------

    before_count = len(df)

    df = df[
        df["resume_text"].str.len() > 20
    ].copy()

    removed_count = before_count - len(df)

    print(
        f"Removed empty/very short resumes: "
        f"{removed_count}"
    )

    # --------------------------------------------------------
    # Extract skills
    # --------------------------------------------------------

    print(
        "Extracting resume skills..."
    )

    df["extracted_skills"] = (
        df["resume_text"]
        .apply(extract_skills_from_text)
    )

    # --------------------------------------------------------
    # Select useful columns
    # --------------------------------------------------------

    output_columns = [
        "resume_text",
        "extracted_skills"
    ]

    optional_columns = [
        "ID",
        "id",
        "Category",
        "category",
        "Job Title",
        "job_title",
        "title"
    ]

    for column in optional_columns:

        if column in df.columns:
            output_columns.append(column)

    # Remove duplicate column names
    output_columns = list(
        dict.fromkeys(output_columns)
    )

    df = df[output_columns]

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Clean resumes saved to:\n"
        f"{output_file}"
    )

    print(
        "Processed shape:",
        df.shape
    )

    print(
        "Resume preprocessing completed successfully."
    )

    return True


# ============================================================
# PROCESS JOB DATASET
# ============================================================

def process_jobs():
    """
    Process the large job_descriptions.csv dataset.

    The dataset is processed in chunks to avoid loading
    the entire file into RAM.

    Input:
        data/raw/job_descriptions.csv

    Output:
        data/processed/jobs_clean.csv
    """

    input_file = os.path.join(
        RAW_DIR,
        "job_descriptions.csv"
    )

    output_file = os.path.join(
        PROCESSED_DIR,
        "jobs_clean.csv"
    )

    print("\n" + "=" * 60)
    print("PROCESSING JOB DESCRIPTION DATASET")
    print("=" * 60)

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not os.path.exists(input_file):

        print(
            f"Warning: Job dataset not found:\n"
            f"{input_file}"
        )

        return False

    print(f"Input file: {input_file}")

    # --------------------------------------------------------
    # Expected columns
    # --------------------------------------------------------

    required_columns = [
        "Job Id",
        "Experience",
        "Qualifications",
        "location",
        "Country",
        "Work Type",
        "Job Title",
        "Role",
        "Job Description",
        "skills",
        "Responsibilities",
        "Company",
    ]

    # --------------------------------------------------------
    # Read only header first
    # --------------------------------------------------------

    try:

        header = pd.read_csv(
            input_file,
            nrows=0,
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        header = pd.read_csv(
            input_file,
            nrows=0,
            encoding="latin-1"
        )

    available_columns = [
        column
        for column in required_columns
        if column in header.columns
    ]

    print(
        "Available columns:",
        available_columns
    )

    if not available_columns:

        raise ValueError(
            "No expected columns were found "
            "in job_descriptions.csv."
        )

    # --------------------------------------------------------
    # Text columns
    # --------------------------------------------------------

    text_columns = [
        "Job Description",
        "skills",
        "Responsibilities"
    ]

    existing_text_columns = [
        column
        for column in text_columns
        if column in available_columns
    ]

    if not existing_text_columns:

        raise ValueError(
            "No job text columns were found. "
            "Expected one of: "
            "Job Description, skills, Responsibilities"
        )

    # --------------------------------------------------------
    # Remove previous output
    # --------------------------------------------------------

    if os.path.exists(output_file):

        try:
            os.remove(output_file)

        except PermissionError:

            raise PermissionError(
                f"Cannot overwrite {output_file}.\n"
                f"Please close the file if it is open in Excel "
                f"or another program."
            )

    # --------------------------------------------------------
    # Process in chunks
    # --------------------------------------------------------

    chunk_size = 10000

    first_chunk = True
    total_rows = 0
    total_valid_rows = 0

    print(
        f"Chunk size: {chunk_size}"
    )

    try:

        reader = pd.read_csv(
            input_file,
            usecols=available_columns,
            chunksize=chunk_size,
            low_memory=False,
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        reader = pd.read_csv(
            input_file,
            usecols=available_columns,
            chunksize=chunk_size,
            low_memory=False,
            encoding="latin-1"
        )

    # --------------------------------------------------------
    # Iterate over chunks
    # --------------------------------------------------------

    for chunk_number, chunk in enumerate(
        reader,
        start=1
    ):

        print(
            f"\nProcessing job chunk "
            f"{chunk_number}..."
        )

        total_rows += len(chunk)

        # ----------------------------------------------------
        # Clean text columns
        # ----------------------------------------------------

        for column in existing_text_columns:

            chunk[column] = (
                chunk[column]
                .apply(clean_text)
            )

        # ----------------------------------------------------
        # Build combined job text
        # ----------------------------------------------------

        job_text_parts = []

        for column in existing_text_columns:

            job_text_parts.append(
                chunk[column].fillna("")
            )

        if job_text_parts:

            combined = job_text_parts[0].copy()

            for part in job_text_parts[1:]:

                combined = (
                    combined
                    + " "
                    + part
                )

            chunk["job_text"] = (
                combined.apply(clean_text)
            )

        else:

            chunk["job_text"] = ""

        # ----------------------------------------------------
        # Remove empty jobs
        # ----------------------------------------------------

        chunk = chunk[
            chunk["job_text"].str.len() > 20
        ].copy()

        total_valid_rows += len(chunk)

        # ----------------------------------------------------
        # Select output columns
        # ----------------------------------------------------

        output_columns = [
            "Job Id",
            "Experience",
            "Qualifications",
            "location",
            "Country",
            "Work Type",
            "Job Title",
            "Role",
            "Company",
            "job_text",
        ]

        output_columns = [
            column
            for column in output_columns
            if column in chunk.columns
        ]

        chunk = chunk[
            output_columns
        ]

        # ----------------------------------------------------
        # Save chunk
        # ----------------------------------------------------

        chunk.to_csv(
            output_file,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
            encoding="utf-8"
        )

        first_chunk = False

        print(
            f"Chunk {chunk_number} saved."
        )

        print(
            f"Valid jobs in chunk: {len(chunk)}"
        )

    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    if first_chunk:

        print(
            "\nNo valid job records were found."
        )

        return False

    print("\n" + "=" * 60)
    print("JOB PREPROCESSING COMPLETED")
    print("=" * 60)

    print(
        f"Total rows read: {total_rows}"
    )

    print(
        f"Valid job rows: {total_valid_rows}"
    )

    print(
        f"Clean jobs saved to:\n"
        f"{output_file}"
    )

    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("AI RESUME TAILORING SYSTEM")
    print("DATA PREPROCESSING")
    print("=" * 70)

    print(
        f"\nProject directory:\n{BASE_DIR}"
    )

    print(
        f"\nRaw data directory:\n{RAW_DIR}"
    )

    print(
        f"\nProcessed data directory:\n{PROCESSED_DIR}"
    )

    # --------------------------------------------------------
    # Resume processing
    # --------------------------------------------------------

    resume_success = process_resumes()

    # --------------------------------------------------------
    # Job processing
    # --------------------------------------------------------

    job_success = process_jobs()

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    if resume_success and job_success:

        print(
            "DATA PREPROCESSING COMPLETED SUCCESSFULLY!"
        )

    else:

        print(
            "DATA PREPROCESSING FINISHED "
            "WITH WARNINGS."
        )

    print("=" * 70)
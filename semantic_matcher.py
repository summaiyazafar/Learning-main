"""
Semantic Matching Engine
AI Resume Tailoring System

Purpose:
    Compare a resume with a job description using
    Sentence Transformers and Cosine Similarity.

Important:
    This module ONLY measures semantic similarity.

    It does NOT:
    - Add missing skills to a resume
    - Modify personal information
    - Invent experience
    - Generate fake projects
    - Change education/certifications

Model:
    all-MiniLM-L6-v2

Output:
    Semantic similarity score from 0 to 100.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union

# ============================================================
# DEPENDENCY CHECKS
# ============================================================

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    DEPENDENCIES_INSTALLED = True
except ImportError:
    SentenceTransformer = None
    cosine_similarity = None
    DEPENDENCIES_INSTALLED = False


class SemanticMatcher:
    """
    Semantic matching engine using Sentence Transformers.

    The model converts resume/JD text into embeddings and
    compares them using cosine similarity.

    If dependencies are missing, the class will return 0.0
    for all similarity calculations and log a warning.
    """

    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        chunk_size: int = 512,
        overlap: int = 100
    ) -> None:
        """
        Initialize the semantic matching engine.

        Parameters
        ----------
        model_name : str
            Sentence Transformer model name.
        chunk_size : int
            Maximum approximate number of words in each chunk.
        overlap : int
            Number of overlapping words between chunks.
        """
        self.model_name = model_name
        self.chunk_size = max(100, int(chunk_size))
        self.overlap = max(0, min(int(overlap), self.chunk_size - 1))
        self.model = None

        if not DEPENDENCIES_INSTALLED:
            print("=" * 60)
            print("WARNING: Semantic Matcher dependencies missing.")
            print("Please install: pip install sentence-transformers scikit-learn")
            print("Semantic matching will return 0.0.")
            print("=" * 60)
            return

        print("=" * 60)
        print("INITIALIZING SEMANTIC MATCHING ENGINE")
        print("=" * 60)
        print(f"Loading Sentence Transformer model: {self.model_name}")

        try:
            self.model = SentenceTransformer(self.model_name)
            print("Semantic model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
            print("Semantic matching will be disabled.")

        print("=" * 60)

    # ==========================================================
    # CLASSMETHOD: CHECK AVAILABILITY
    # ==========================================================

    @classmethod
    def is_available(cls) -> bool:
        """Return True if semantic matching dependencies are installed."""
        return DEPENDENCIES_INSTALLED and SentenceTransformer is not None

    # ==========================================================
    # TEXT CLEANING
    # ==========================================================

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """
        Clean input text.

        Returns
        -------
        str
            Cleaned text.
        """
        if text is None:
            return ""
        try:
            text = str(text)
        except Exception:
            return ""
        text = text.replace("\x00", " ")
        return " ".join(text.split()).strip()

    # ==========================================================
    # TEXT VALIDATION
    # ==========================================================

    @staticmethod
    def is_valid_text(text: str) -> bool:
        """
        Check whether text contains meaningful content.
        """
        text = SemanticMatcher.clean_text(text)
        return bool(text) and len(text) >= 10

    # ==========================================================
    # TEXT CHUNKING
    # ==========================================================

    def split_into_chunks(self, text: str) -> List[str]:
        """
        Split long text into overlapping chunks.

        This helps semantic matching when a resume or JD
        is longer than the model's ideal input size.
        """
        text = self.clean_text(text)
        if not text:
            return []

        words = text.split()
        if len(words) <= self.chunk_size:
            return [text]

        chunks = []
        step = self.chunk_size - self.overlap
        if step <= 0:
            step = self.chunk_size

        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            if chunk_words:
                chunks.append(" ".join(chunk_words))
            if end >= len(words):
                break
            start += step

        return chunks

    # ==========================================================
    # EMBEDDING CREATION
    # ==========================================================

    def create_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Convert text into a normalized numerical vector.

        Returns
        -------
        numpy.ndarray or None
        """
        if self.model is None:
            return None

        text = self.clean_text(text)
        if not text:
            return None

        try:
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return np.asarray(embedding, dtype=np.float32)
        except Exception as error:
            print(f"Embedding creation error: {error}")
            return None

    def create_chunk_embeddings(self, text: str) -> List[np.ndarray]:
        """Create embeddings for all text chunks."""
        if self.model is None:
            return []

        chunks = self.split_into_chunks(text)
        if not chunks:
            return []

        try:
            embeddings = self.model.encode(
                chunks,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return [np.asarray(e, dtype=np.float32) for e in embeddings]
        except Exception as error:
            print(f"Chunk embedding error: {error}")
            return []

    # ==========================================================
    # SIMILARITY CALCULATIONS
    # ==========================================================

    def calculate_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Calculate semantic similarity between resume and job description.

        Returns
        -------
        float
            Score from 0 to 100.
        """
        if not self.is_available() or self.model is None:
            return 0.0

        resume_text = self.clean_text(resume_text)
        job_text = self.clean_text(job_text)

        if not self.is_valid_text(resume_text) or not self.is_valid_text(job_text):
            return 0.0

        resume_emb = self.create_embedding(resume_text)
        job_emb = self.create_embedding(job_text)

        if resume_emb is None or job_emb is None:
            return 0.0

        try:
            similarity = cosine_similarity(
                resume_emb.reshape(1, -1),
                job_emb.reshape(1, -1)
            )[0][0]
            similarity = float(np.clip(similarity, -1.0, 1.0))
            score = ((similarity + 1.0) / 2.0) * 100.0
            return round(float(np.clip(score, 0, 100)), 2)
        except Exception as error:
            print(f"Similarity calculation error: {error}")
            return 0.0

    def calculate_chunk_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Calculate semantic similarity using chunks.

        Each resume chunk is compared with the complete
        job description embedding.

        The best relevant resume chunks are emphasized
        instead of relying only on one huge embedding.
        """
        if not self.is_available() or self.model is None:
            return 0.0

        resume_text = self.clean_text(resume_text)
        job_text = self.clean_text(job_text)

        if not self.is_valid_text(resume_text) or not self.is_valid_text(job_text):
            return 0.0

        resume_chunks = self.split_into_chunks(resume_text)
        job_chunks = self.split_into_chunks(job_text)

        if not resume_chunks or not job_chunks:
            return 0.0

        try:
            resume_embeddings = self.model.encode(
                resume_chunks,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            job_embeddings = self.model.encode(
                job_chunks,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            similarity_matrix = cosine_similarity(
                resume_embeddings,
                job_embeddings
            )

            # Best match for each resume chunk
            best_resume_matches = np.max(similarity_matrix, axis=1)
            if len(best_resume_matches) == 0:
                return 0.0

            # Weighted average: 70% top chunks, 30% overall average
            top_k = max(1, int(np.ceil(len(best_resume_matches) * 0.30)))
            top_scores = np.sort(best_resume_matches)[-top_k:]
            best_score = float(np.mean(top_scores))
            overall_score = float(np.mean(best_resume_matches))

            combined_similarity = 0.70 * best_score + 0.30 * overall_score
            combined_similarity = float(np.clip(combined_similarity, -1.0, 1.0))
            score = ((combined_similarity + 1.0) / 2.0) * 100.0
            return round(float(np.clip(score, 0, 100)), 2)

        except Exception as error:
            print(f"Chunk similarity error: {error}")
            return 0.0

    def calculate_best_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Calculate the final semantic similarity score.

        For normal-sized text:
            Uses direct embedding comparison.

        For long text:
            Uses chunk-based comparison.
        """
        resume_text = self.clean_text(resume_text)
        job_text = self.clean_text(job_text)

        if not self.is_valid_text(resume_text) or not self.is_valid_text(job_text):
            return 0.0

        resume_word_count = len(resume_text.split())
        job_word_count = len(job_text.split())

        if resume_word_count > self.chunk_size or job_word_count > self.chunk_size:
            return self.calculate_chunk_similarity(resume_text, job_text)
        return self.calculate_similarity(resume_text, job_text)

    # ==========================================================
    # MATCH LEVEL
    # ==========================================================

    @staticmethod
    def get_match_level(score: float) -> str:
        """Convert semantic score into a human-readable level."""
        if score >= 85:
            return "Excellent Match"
        if score >= 70:
            return "Strong Match"
        if score >= 55:
            return "Good Match"
        if score >= 40:
            return "Moderate Match"
        return "Low Match"

    # ==========================================================
    # COMPLETE COMPARISON
    # ==========================================================

    def compare(self, resume_text: str, job_text: str) -> Dict[str, Union[float, str, int]]:
        """
        Perform complete semantic comparison.

        Returns
        -------
        dict
            Contains score, match level, word counts, and status.
        """
        resume_text = self.clean_text(resume_text)
        job_text = self.clean_text(job_text)

        if not resume_text:
            return {
                "semantic_score": 0.0,
                "match_level": "No Resume Text",
                "resume_words": 0,
                "job_words": len(job_text.split()),
                "status": "invalid_resume"
            }
        if not job_text:
            return {
                "semantic_score": 0.0,
                "match_level": "No Job Description",
                "resume_words": len(resume_text.split()),
                "job_words": 0,
                "status": "invalid_job_description"
            }

        score = self.calculate_best_similarity(resume_text, job_text)
        return {
            "semantic_score": score,
            "match_level": self.get_match_level(score),
            "resume_words": len(resume_text.split()),
            "job_words": len(job_text.split()),
            "status": "success"
        }


# ============================================================
# SIMPLE HELPER FUNCTION
# ============================================================

def semantic_similarity(resume_text: str, job_text: str) -> float:
    """
    Simple helper function for direct similarity calculation.

    Other modules can use this function directly.
    """
    matcher = SemanticMatcher()
    return matcher.calculate_best_similarity(resume_text, job_text)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("SEMANTIC MATCHING ENGINE TEST")
    print("=" * 70)

    resume = """
    Python developer with experience in machine learning,
    data analysis, SQL, Pandas, NumPy and Power BI.
    I have worked on predictive models and data-driven
    applications using Python and machine learning algorithms.
    """

    job_description = """
    We are looking for a Machine Learning Engineer with
    strong Python programming skills, experience in
    data analytics, SQL and machine learning algorithms.
    Knowledge of TensorFlow and Power BI is preferred.
    The candidate should understand predictive modeling,
    data processing and machine learning workflows.
    """

    try:
        matcher = SemanticMatcher()
        result = matcher.compare(resume, job_description)

        print("\nResume:")
        print("-" * 70)
        print(resume.strip())

        print("\nJob Description:")
        print("-" * 70)
        print(job_description.strip())

        print("\nSemantic Match Result:")
        print("-" * 70)
        print(f"Semantic Score : {result['semantic_score']}%")
        print(f"Match Level    : {result['match_level']}")
        print(f"Resume Words   : {result['resume_words']}")
        print(f"JD Words       : {result['job_words']}")
        print(f"Status         : {result['status']}")

        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as error:
        print("\n" + "=" * 70)
        print("SEMANTIC MATCHING TEST FAILED")
        print("=" * 70)
        print(f"Error: {error}")
        print("\nPossible solution:")
        print("pip install sentence-transformers scikit-learn numpy")
"""
AI Resume Tailoring System – Skill Extraction Module
=====================================================

This package provides skill extraction and comparison utilities.
All other components are loaded on demand to avoid circular imports.
"""

# ============================================================
# SKILL EXTRACTION – from skill_extractor.py
# ============================================================

from .skill_extractor import (
    extract_skills,
    extract_skills_with_frequency,
    compare_skills,
    normalize_text,
    normalize_skill,
    get_all_skills,
    get_skill_category,
    categorize_skills,
)

# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "extract_skills",
    "extract_skills_with_frequency",
    "compare_skills",
    "normalize_text",
    "normalize_skill",
    "get_all_skills",
    "get_skill_category",
    "categorize_skills",
]

__version__ = "2.0.0"
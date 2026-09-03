"""
AI Resume Tailoring System – Resume Matcher
===========================================

Professional Resume vs Job Description matching engine.
Combines keyword/skill matching with semantic matching.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.jd_analyzer import JDAnalyzer
from modules.skill_extractor import compare_skills

try:
    from modules.semantic_matcher import SemanticMatcher
except ImportError:
    SemanticMatcher = None

try:
    from modules.gap_analyzer import GapAnalyzer
except Exception:
    GapAnalyzer = None


class ResumeJobMatcher:
    """
    Resume vs Job Description matching engine.

    Combines:
        - Keyword/skill matching (40%)
        - Semantic matching (60%)
        - Optional GapAnalyzer for detailed analysis
    """

    def __init__(self, keyword_weight: float = 0.40, semantic_weight: float = 0.60):
        try:
            keyword_weight = float(keyword_weight)
        except (TypeError, ValueError):
            keyword_weight = 0.40
        try:
            semantic_weight = float(semantic_weight)
        except (TypeError, ValueError):
            semantic_weight = 0.60

        keyword_weight = max(0.0, keyword_weight)
        semantic_weight = max(0.0, semantic_weight)
        total = keyword_weight + semantic_weight
        if total <= 0:
            keyword_weight, semantic_weight = 0.40, 0.60
            total = 1.0

        self.keyword_weight = keyword_weight / total
        self.semantic_weight = semantic_weight / total

        self.jd_analyzer = JDAnalyzer()
        self.semantic_matcher = None
        if SemanticMatcher is not None:
            try:
                self.semantic_matcher = SemanticMatcher()
            except Exception:
                self.semantic_matcher = None

        self.gap_analyzer = None
        if GapAnalyzer is not None:
            try:
                self.gap_analyzer = GapAnalyzer()
            except Exception:
                self.gap_analyzer = None

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def normalize_score(score: Any) -> float:
        try:
            value = float(score)
        except (TypeError, ValueError):
            return 0.0
        if 0.0 <= value <= 1.0:
            value *= 100.0
        return round(max(0.0, min(100.0, value)), 2)

    @staticmethod
    def safe_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            value = value.strip()
            return [value] if value else []
        if isinstance(value, (list, tuple, set)):
            return [str(v).strip() for v in value if v is not None and str(v).strip()]
        return [str(value).strip()] if str(value).strip() else []

    @staticmethod
    def unique(items: List[str]) -> List[str]:
        result, seen = [], set()
        for item in items:
            text = str(item).strip()
            if not text:
                continue
            key = text.lower()
            if key not in seen:
                seen.add(key)
                result.append(text)
        return result

    # ==========================================================
    # KEYWORD / SKILL MATCHING
    # ==========================================================

    def calculate_keyword_score(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        resume_text, job_text = str(resume_text or "").strip(), str(job_text or "").strip()
        if not resume_text or not job_text:
            return {"match_percentage": 0.0, "resume_skills": [], "job_skills": [], "matched_skills": [], "missing_skills": []}

        try:
            result = compare_skills(resume_text, job_text)
        except Exception:
            return {"match_percentage": 0.0, "resume_skills": [], "job_skills": [], "matched_skills": [], "missing_skills": []}

        if not isinstance(result, dict):
            return {"match_percentage": 0.0, "resume_skills": [], "job_skills": [], "matched_skills": [], "missing_skills": []}

        result["resume_skills"] = self.unique(self.safe_list(result.get("resume_skills", [])))
        result["job_skills"] = self.unique(self.safe_list(result.get("job_skills", [])))
        result["matched_skills"] = self.unique(self.safe_list(result.get("matched_skills", [])))
        result["missing_skills"] = self.unique(self.safe_list(result.get("missing_skills", [])))
        result["match_percentage"] = self.normalize_score(result.get("match_percentage", result.get("score", 0)))
        return result

    # ==========================================================
    # SEMANTIC MATCHING
    # ==========================================================

    def calculate_semantic_score(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        resume_text, job_text = str(resume_text or "").strip(), str(job_text or "").strip()
        if not resume_text or not job_text:
            return {"semantic_score": 0.0, "raw_score": 0.0}

        if self.semantic_matcher is None:
            return {"semantic_score": 0.0, "raw_score": 0.0}

        try:
            if hasattr(self.semantic_matcher, "calculate_best_similarity"):
                result = self.semantic_matcher.calculate_best_similarity(resume_text, job_text)
                score = self.normalize_score(result)
                return {"semantic_score": score, "raw_score": result}
            elif hasattr(self.semantic_matcher, "calculate_similarity"):
                result = self.semantic_matcher.calculate_similarity(resume_text, job_text)
                score = self.normalize_score(result)
                return {"semantic_score": score, "raw_score": result}
        except Exception:
            pass
        return {"semantic_score": 0.0, "raw_score": 0.0}

    # ==========================================================
    # GAP ANALYSIS
    # ==========================================================

    def calculate_gap_analysis(self, resume_skills: List[str], job_skills: List[str], jd_text: str = "") -> Dict[str, Any]:
        if self.gap_analyzer is None:
            return {"available": False, "matched_skills": [], "missing_skills": [], "critical_missing_skills": [], "recommendations": []}

        try:
            if hasattr(self.gap_analyzer, "complete_analysis"):
                result = self.gap_analyzer.complete_analysis(resume_skills, job_skills, jd_text)
            elif hasattr(self.gap_analyzer, "analyze"):
                result = self.gap_analyzer.analyze(resume_skills, job_skills, jd_text)
            else:
                return {"available": False, "matched_skills": [], "missing_skills": [], "critical_missing_skills": [], "recommendations": []}
        except Exception:
            return {"available": False, "matched_skills": [], "missing_skills": [], "critical_missing_skills": [], "recommendations": []}

        if not isinstance(result, dict):
            return {"available": False, "matched_skills": [], "missing_skills": [], "critical_missing_skills": [], "recommendations": []}

        return {
            "available": True,
            "matched_skills": self.unique(self.safe_list(result.get("matched_skills", []))),
            "missing_skills": self.unique(self.safe_list(result.get("missing_skills", []))),
            "critical_missing_skills": self.unique(self.safe_list(result.get("critical_missing_skills", result.get("critical_missing", [])))),
            "recommendations": self.unique(self.safe_list(result.get("recommendations", [])))
        }

    # ==========================================================
    # FINAL SCORE
    # ==========================================================

    def calculate_final_score(self, keyword_score: float, semantic_score: float) -> float:
        keyword = self.normalize_score(keyword_score)
        semantic = self.normalize_score(semantic_score)
        score = keyword * self.keyword_weight + semantic * self.semantic_weight
        return round(max(0.0, min(100.0, score)), 2)

    def get_match_level(self, score: float) -> str:
        score = self.normalize_score(score)
        if score >= 85:
            return "Excellent Match"
        if score >= 70:
            return "Strong Match"
        if score >= 55:
            return "Good Match"
        if score >= 40:
            return "Moderate Match"
        return "Low Match"

    def get_match_status(self, score: float) -> str:
        score = self.normalize_score(score)
        if score >= 85:
            return "excellent"
        if score >= 70:
            return "strong"
        if score >= 55:
            return "moderate"
        if score >= 40:
            return "weak"
        return "low"

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    def build_recommendations(self, keyword_score: float, semantic_score: float, matched_skills: List[str], missing_skills: List[str], required_skills: List[str], critical_missing: Optional[List[str]] = None) -> List[str]:
        recs = []
        keyword, semantic = self.normalize_score(keyword_score), self.normalize_score(semantic_score)
        matched, missing, required = self.unique(self.safe_list(matched_skills)), self.unique(self.safe_list(missing_skills)), self.unique(self.safe_list(required_skills))
        critical = self.unique(self.safe_list(critical_missing or []))

        if critical:
            recs.append("Critical JD skills are missing. Do not add them unless the candidate has verified evidence.")
        elif missing:
            recs.append("Review missing JD skills and gain real experience before claiming them.")

        if keyword < 40:
            recs.append("Skill alignment is low. Highlight relevant existing skills.")
        elif keyword < 70:
            recs.append("Several relevant skills exist. Prioritize matched skills in the resume.")
        else:
            recs.append("Existing skills show strong alignment with the JD.")

        if semantic < 40:
            recs.append("Semantic alignment is low. Reorder experience around JD responsibilities.")
        elif semantic < 70:
            recs.append("Improve semantic alignment by emphasizing relevant experience.")
        else:
            recs.append("Resume content has strong semantic alignment with the JD.")

        if matched:
            recs.append("Place strongest matched skills near the top of the Skills section.")
        else:
            recs.append("No reliable skill match found. Review manually.")

        return self.unique(recs)

    # ==========================================================
    # MAIN MATCH
    # ==========================================================

    def match(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        resume_text, job_text = str(resume_text or "").strip(), str(job_text or "").strip()
        if not resume_text:
            return self._empty_result("Resume text is empty.")
        if not job_text:
            return self._empty_result("Job Description is empty.")

        # JD Analysis
        try:
            jd_analysis = self.jd_analyzer.analyze(job_text)
            if not isinstance(jd_analysis, dict):
                jd_analysis = {}
        except Exception:
            jd_analysis = {}

        # Skill matching
        skill_result = self.calculate_keyword_score(resume_text, job_text)
        keyword_score = skill_result.get("match_percentage", 0.0)

        # Semantic matching
        semantic_result = self.calculate_semantic_score(resume_text, job_text)
        semantic_score = semantic_result.get("semantic_score", 0.0)

        # Gap analysis
        resume_skills = self.unique(self.safe_list(skill_result.get("resume_skills", [])))
        jd_skills = self.unique(self.safe_list(skill_result.get("job_skills", [])))
        jd_skills_from_analysis = self.unique(self.safe_list(jd_analysis.get("skills", [])))
        if jd_skills_from_analysis:
            jd_skills = self.unique(jd_skills + jd_skills_from_analysis)

        gap_analysis = self.calculate_gap_analysis(resume_skills, jd_skills, job_text)

        # Extract skills
        matched_skills = self.unique(self.safe_list(skill_result.get("matched_skills", [])))
        missing_skills = self.unique(self.safe_list(skill_result.get("missing_skills", [])))

        if gap_analysis.get("matched_skills"):
            matched_skills = self.unique(gap_analysis.get("matched_skills", []))
        if gap_analysis.get("missing_skills"):
            missing_skills = self.unique(gap_analysis.get("missing_skills", []))

        # JD Skills
        all_jd_skills = self.unique(self.safe_list(jd_analysis.get("skills", skill_result.get("job_skills", []))))
        required_skills = self.unique(self.safe_list(jd_analysis.get("required_skills", [])))
        preferred_skills = self.unique(self.safe_list(jd_analysis.get("preferred_skills", [])))
        nice_to_have_skills = self.unique(self.safe_list(jd_analysis.get("nice_to_have_skills", [])))

        if not all_jd_skills:
            all_jd_skills = self.unique(skill_result.get("job_skills", []))

        if not required_skills and not preferred_skills and not nice_to_have_skills:
            required_skills = list(all_jd_skills)

        # Required skill coverage
        required_set = {s.lower() for s in required_skills}
        matched_set = {s.lower() for s in matched_skills}
        coverage = round((len(required_set.intersection(matched_set)) / len(required_set)) * 100, 2) if required_set else 0.0

        # Critical missing
        critical_missing = self.unique(self.safe_list(gap_analysis.get("critical_missing_skills", [])))
        if not critical_missing:
            critical_missing = [s for s in required_skills if s.lower() not in matched_set]

        # Final score
        final_score = self.calculate_final_score(keyword_score, semantic_score)

        # Recommendations
        recommendations = self.build_recommendations(keyword_score, semantic_score, matched_skills, missing_skills, required_skills, critical_missing)
        gap_recs = self.unique(self.safe_list(gap_analysis.get("recommendations", [])))
        recommendations = self.unique(recommendations + gap_recs)

        return {
            "job_title": jd_analysis.get("job_title", "Target Position"),
            "experience_required": jd_analysis.get("experience_years", 0),
            "qualifications": self.unique(self.safe_list(jd_analysis.get("qualifications", []))),
            "responsibilities": self.unique(self.safe_list(jd_analysis.get("responsibilities", []))),
            "keywords": self.unique(self.safe_list(jd_analysis.get("keywords", []))),
            "required_skills": required_skills,
            "all_jd_skills": all_jd_skills,
            "preferred_skills": preferred_skills,
            "nice_to_have_skills": nice_to_have_skills,
            "resume_skills": resume_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "critical_missing_skills": critical_missing,
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "final_score": final_score,
            "ats_score": final_score,
            "match_level": self.get_match_level(final_score),
            "match_status": self.get_match_status(final_score),
            "required_skill_coverage": coverage,
            "skill_analysis": skill_result,
            "semantic_analysis": semantic_result,
            "gap_analysis": gap_analysis,
            "jd_analysis": jd_analysis,
            "recommendations": recommendations,
            "keyword_weight": self.keyword_weight,
            "semantic_weight": self.semantic_weight,
            "resume_text": resume_text,
            "job_text": job_text,
            "safety_rule": "Missing JD skills are analysis items only and must not be added without real evidence."
        }

    def _empty_result(self, reason: str = "") -> Dict[str, Any]:
        return {
            "job_title": "Target Position", "experience_required": 0,
            "qualifications": [], "responsibilities": [], "keywords": [],
            "required_skills": [], "all_jd_skills": [], "preferred_skills": [],
            "nice_to_have_skills": [], "resume_skills": [], "matched_skills": [],
            "missing_skills": [], "critical_missing_skills": [],
            "keyword_score": 0.0, "semantic_score": 0.0, "final_score": 0.0, "ats_score": 0.0,
            "match_level": "Low Match", "match_status": "low",
            "required_skill_coverage": 0.0,
            "skill_analysis": {}, "semantic_analysis": {}, "gap_analysis": {}, "jd_analysis": {},
            "recommendations": [reason] if reason else [],
            "keyword_weight": self.keyword_weight, "semantic_weight": self.semantic_weight,
            "resume_text": "", "job_text": "",
            "safety_rule": "Missing JD skills are never automatically added.",
            "error": reason
        }

    def compare(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        return self.match(resume_text, job_text)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    matcher = ResumeJobMatcher()
    result = matcher.match(
        "Python developer with SQL, Power BI, and Machine Learning experience.",
        "We need a Data Scientist with Python, SQL, Machine Learning, TensorFlow, and Power BI."
    )
    print("\n" + "=" * 60)
    print("MATCHER TEST")
    print("=" * 60)
    print(f"Final Score: {result['final_score']}%")
    print(f"Match Level: {result['match_level']}")
    print(f"Matched Skills: {result['matched_skills']}")
    print(f"Missing Skills: {result['missing_skills']}")
    print("=" * 60)
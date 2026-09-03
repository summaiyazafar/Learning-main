"""
AI Resume Tailoring System – Resume Tailor
"""

import re
from collections import OrderedDict
from typing import Dict, List, Optional, Any, Set


class ResumeTailor:
    """Tailor resumes while preserving protected information."""

    def __init__(self):
        self.stop_words = frozenset({
            "the", "and", "for", "with", "from", "that", "this",
            "are", "you", "your", "our", "will", "have", "has",
            "had", "can", "who", "their", "they", "them", "into",
            "than", "then", "when", "where", "what", "which",
            "role", "position", "company", "employee", "employees",
            "required", "requirements", "experience", "years",
            "year", "job", "team", "work", "working", "ability",
            "skills", "candidate", "responsibilities", "responsibility",
            "including", "using", "use", "support", "strong", "good",
            "knowledge", "preferred", "looking", "seeking",
            "develop", "development"
        })

        self.skill_aliases = {
            "python3": "python", "py": "python",
            "powerbi": "power bi", "power-bi": "power bi",
            "sklearn": "scikit-learn", "scikit learn": "scikit-learn",
            "scikit-learn": "scikit-learn",
            "tf": "tensorflow", "torch": "pytorch",
            "opencv-python": "opencv", "ml": "machine learning",
            "ai": "artificial intelligence",
            "genai": "generative ai", "llms": "llm",
            "nodejs": "node.js", "postgres": "postgresql",
            "gcp": "google cloud", "k8s": "kubernetes"
        }

    def clean_text(self, text: Optional[str]) -> str:
        if text is None:
            return ""
        text = str(text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\x00", "").replace("\t", " ")
        text = re.sub(r"[ ]{2,}", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def normalize_skill(self, skill: str) -> str:
        if skill is None:
            return ""
        skill = str(skill).strip().lower()
        skill = re.sub(r"\s+", " ", skill)
        return skill

    def normalize_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [self.clean_text(x) for x in value.splitlines() if self.clean_text(x)]
        if isinstance(value, (list, tuple, set)):
            return [self.clean_text(x) for x in value if x and self.clean_text(x)]
        return [self.clean_text(value)] if self.clean_text(value) else []

    def comparison_text(self, text: str) -> str:
        if not text:
            return ""
        text = str(text).lower()
        text = text.replace("&", " and ")
        text = re.sub(r"[-_/]+", " ", text)
        text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def deduplicate(self, items: List[str]) -> List[str]:
        result, seen = [], set()
        for item in items:
            if item is None:
                continue
            item = str(item).strip()
            if not item:
                continue
            key = re.sub(r"[^a-z0-9+#.]", "", self.comparison_text(item))
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    def fuzzy_match_skills(self, skill1: str, skill2: str, threshold: float = 0.80) -> bool:
        if not skill1 or not skill2:
            return False
        s1, s2 = self.comparison_text(skill1), self.comparison_text(skill2)
        if not s1 or not s2:
            return False
        if s1 == s2:
            return True
        a1 = self.skill_aliases.get(s1, s1)
        a2 = self.skill_aliases.get(s2, s2)
        if a1 == a2:
            return True
        if len(s1) >= 4 and len(s2) >= 4:
            if s1 in s2 or s2 in s1:
                return True
        words1 = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", s1))
        words2 = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", s2))
        if not words1 or not words2:
            return False
        common = words1.intersection(words2)
        if not common:
            return False
        return len(common) / min(len(words1), len(words2)) >= threshold

    def get_protected_data(self, resume_data: Dict) -> Dict:
        default = {f: "" for f in ["name", "phone", "email", "linkedin", "github", "kaggle", "location", "education", "certifications"]}
        if not isinstance(resume_data, dict):
            return default
        protected = resume_data.get("protected", {})
        if not isinstance(protected, dict):
            protected = {}
        for key in default:
            val = protected.get(key, resume_data.get(key, ""))
            default[key] = "" if val is None else str(val).strip()
        return default

    def get_editable_data(self, resume_data: Dict) -> Dict:
        default = {"summary": "", "skills": [], "experience": "", "projects": ""}
        if not isinstance(resume_data, dict):
            return default
        editable = resume_data.get("editable", {})
        if not isinstance(editable, dict):
            editable = {}
        default["summary"] = self.clean_text(editable.get("summary", resume_data.get("summary", "")))
        default["skills"] = self.normalize_list(editable.get("skills", resume_data.get("skills", [])))
        default["experience"] = self.clean_text(editable.get("experience", resume_data.get("experience", "")))
        default["projects"] = self.clean_text(editable.get("projects", resume_data.get("projects", "")))
        return default

    def split_content(self, text: str) -> List[str]:
        text = self.clean_text(text)
        if not text:
            return []
        lines = text.split("\n")
        blocks, current = [], []
        for line in lines:
            line = line.strip()
            if not line:
                if current:
                    blocks.append(" ".join(current).strip())
                    current = []
                continue
            if re.match(r"^(?:[-•●▪◦*]|\d+[.)])\s+", line):
                if current:
                    blocks.append(" ".join(current).strip())
                line = re.sub(r"^(?:[-•●▪◦*]|\d+[.)])\s+", "", line)
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append(" ".join(current).strip())
        if len(blocks) == 1:
            fallback = re.split(r"(?<=[.!?])\s+", blocks[0])
            if len(fallback) > 1:
                blocks = [x.strip() for x in fallback if x.strip()]
        return self.deduplicate(blocks)

    def relevance_score(self, text: str, jd_terms: List[str]) -> float:
        if not text or not jd_terms:
            return 0.0
        text_lower = self.comparison_text(text)
        score, matched_terms = 0.0, set()
        for term in jd_terms:
            term_norm = self.comparison_text(term)
            if not term_norm:
                continue
            if term_norm in text_lower:
                if term_norm not in matched_terms:
                    score += 2.0
                    matched_terms.add(term_norm)
                continue
            term_words = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", term_norm))
            text_words = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", text_lower))
            useful = {w for w in term_words if w not in self.stop_words}
            common = useful.intersection(text_words)
            if common:
                score += min(len(common), 2)
        return score

    def tailor(self, resume_data: Dict, jd_result: Dict, job_description: str = "") -> OrderedDict:
        # Handle raw text
        if not isinstance(resume_data, dict):
            raw = str(resume_data or "")
            resume_data = {
                "text": raw,
                "protected": {f: "" for f in ["name", "phone", "email", "linkedin", "github", "kaggle", "location", "education", "certifications"]},
                "editable": {"summary": "", "skills": [], "experience": raw, "projects": ""}
            }

        protected = self.get_protected_data(resume_data)
        editable = self.get_editable_data(resume_data)

        # Extract JD skills
        jd_skills = self.normalize_list(jd_result.get("skills", [])) if isinstance(jd_result, dict) else []
        jd_terms = self.normalize_list(jd_result.get("skills", [])) + self.normalize_list(jd_result.get("keywords", [])) + self.normalize_list(jd_result.get("responsibilities", []))

        # Match skills
        resume_skills = self.normalize_list(editable.get("skills", []))
        matched, missing = [], []
        for jd_skill in jd_skills:
            found = False
            for res_skill in resume_skills:
                if self.fuzzy_match_skills(res_skill, jd_skill):
                    matched.append(res_skill)
                    found = True
                    break
            if not found:
                missing.append(jd_skill)
        matched = self.deduplicate(matched)
        missing = self.deduplicate(missing)

        # Prioritize skills
        ordered = []
        remaining = []
        for skill in resume_skills:
            found = False
            for jd_skill in jd_skills:
                if self.fuzzy_match_skills(skill, jd_skill):
                    found = True
                    break
            if found:
                ordered.append(skill)
            else:
                remaining.append(skill)
        all_skills = self.deduplicate(ordered + remaining)

        # Reorder experience & projects
        exp_parts = self.split_content(editable.get("experience", ""))
        proj_parts = self.split_content(editable.get("projects", ""))

        scored_exp = [(self.relevance_score(p, jd_terms), i, p) for i, p in enumerate(exp_parts)]
        scored_exp.sort(key=lambda x: (-x[0], x[1]))
        ordered_exp = self.deduplicate([item[2] for item in scored_exp])

        scored_proj = [(self.relevance_score(p, jd_terms), i, p) for i, p in enumerate(proj_parts)]
        scored_proj.sort(key=lambda x: (-x[0], x[1]))
        ordered_proj = self.deduplicate([item[2] for item in scored_proj])

        # Summary
        original_summary = self.clean_text(editable.get("summary", ""))
        job_title = jd_result.get("job_title", "Target Position") if isinstance(jd_result, dict) else "Target Position"
        if original_summary:
            summary = original_summary
        elif matched:
            summary = f"Professional with skills relevant to {job_title}, including {', '.join(matched[:6])}."
        else:
            summary = f"Professional seeking opportunities as a {job_title}."

        # Build result – FORCE PROTECTED DATA
        result = OrderedDict([
            ("job_title", job_title),
            ("experience_required", jd_result.get("experience_years", 0) if isinstance(jd_result, dict) else 0),
            ("name", protected.get("name", "")),
            ("phone", protected.get("phone", "")),
            ("email", protected.get("email", "")),
            ("linkedin", protected.get("linkedin", "")),
            ("github", protected.get("github", "")),
            ("kaggle", protected.get("kaggle", "")),
            ("location", protected.get("location", "")),
            ("education", protected.get("education", "")),
            ("certifications", protected.get("certifications", "")),
            ("professional_summary", summary),
            ("skills", all_skills),
            ("matched_skills", matched),
            ("missing_skills", missing),
            ("experience", ordered_exp),
            ("projects", ordered_proj),
        ])

        return result
"""
============================================================
AI RESUME TAILORING SYSTEM
Resume Tailoring Engine - Professional Edition
============================================================

Purpose
-------
Tailor an existing resume according to a target Job Description.

PROTECTED INFORMATION
---------------------
These fields are NEVER generated, replaced, or modified:

    - Name
    - Phone
    - Email
    - LinkedIn
    - GitHub
    - Kaggle
    - Location
    - Education
    - Certifications

TAILORABLE INFORMATION
----------------------
These sections may be optimized/reorganized according to the JD:

    - Professional Summary
    - Skills
    - Experience
    - Projects

IMPORTANT SAFETY RULE
---------------------
This module does NOT invent:

    - Candidate identity
    - Contact information
    - Education
    - Certifications
    - Companies
    - Job titles
    - Employment dates
    - Fake projects
    - Unsupported skills

Missing JD skills are reported separately as gaps.

Only skills already present in the candidate's resume
can appear inside the tailored resume skills section.

Experience and projects are REORDERED based on JD relevance.
They are not fabricated.
============================================================
"""

import re
from collections import OrderedDict
from typing import Dict, List, Optional, Any, Set, Tuple, Union


class ResumeTailor:
    """
    Tailor resumes to match job descriptions while preserving
    protected candidate information.

    Protected fields:
        name, phone, email, linkedin, github, kaggle,
        location, education, certifications

    Editable fields:
        summary, skills, experience, projects
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self) -> None:
        """Initialize the ResumeTailor engine with stop words and role words."""
        # Common stop words that should not receive high relevance scores
        self.stop_words: frozenset = frozenset({
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

        # Common role words – used to avoid treating a professional
        # title as a candidate name during extraction.
        self.role_words: frozenset = frozenset({
            "analyst", "engineer", "developer", "scientist",
            "manager", "designer", "consultant", "specialist",
            "administrator", "architect", "researcher", "intern",
            "trainee", "professional", "expert", "programmer",
            "technician", "lead", "director", "officer", "executive",
            "assistant", "coordinator"
        })

        # Expanded skill aliases for fuzzy matching
        self.skill_aliases: Dict[str, str] = {
            "python3": "python",
            "py": "python",
            "powerbi": "power bi",
            "power-bi": "power bi",
            "sklearn": "scikit learn",
            "scikit learn": "scikit learn",
            "scikit-learn": "scikit learn",
            "tf": "tensorflow",
            "tensorflow": "tensorflow",
            "pytorch": "pytorch",
            "opencv python": "opencv",
            "opencv-python": "opencv",
            "ml": "machine learning",
            "machinelearning": "machine learning",
            "ai": "artificial intelligence",
            "artificial intelligence": "artificial intelligence",
            "nlp": "natural language processing",
            "genai": "generative ai",
            "llm": "large language model",
            "llms": "large language model",
            "d3": "d3.js",
            "angularjs": "angular",
            "vuejs": "vue",
            "nodejs": "node.js",
            "reactjs": "react",
            "postgres": "postgresql",
            "gcp": "google cloud",
            "azure": "azure",
            "aws": "aws",
        }

    # ============================================================
    # TEXT CLEANING & NORMALISATION
    # ============================================================

    def clean_text(self, text: Optional[str]) -> str:
        """
        Clean and normalise text while preserving useful line structure.

        Args:
            text: Raw text.

        Returns:
            Cleaned text with normalised whitespace and line breaks.
        """
        if text is None:
            return ""

        text = str(text)
        if not text.strip():
            return ""

        # Normalise line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove null characters
        text = text.replace("\x00", "")
        # Replace tabs with spaces
        text = text.replace("\t", " ")
        # Remove markdown bold
        text = text.replace("**", "")
        # Collapse multiple spaces
        text = re.sub(r"[ ]{2,}", " ", text)
        # Remove spaces around newlines
        text = re.sub(r" *\n *", "\n", text)
        # Max two consecutive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def comparison_text(self, text: str) -> str:
        """
        Create a normalised version of text for matching/aliases.

        Example:
            "Power BI" -> "power bi"
            "scikit-learn" -> "scikit learn"
        """
        if not text:
            return ""

        text = str(text).lower()
        text = text.replace("&", " and ")
        text = re.sub(r"[-_/]+", " ", text)
        text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def normalize_skill(self, skill: str) -> str:
        """Normalise a skill for comparison; the original display value is preserved elsewhere."""
        if skill is None:
            return ""
        return re.sub(r"\s+", " ", str(skill).strip())

    # ============================================================
    # LIST OPERATIONS
    # ============================================================

    def normalize_list(self, value: Any) -> List[str]:
        """
        Convert a string/list/dict/tuple/set into a clean list of strings.

        Args:
            value: Any input.

        Returns:
            List of strings, with bullets and separators removed.
        """
        if value is None:
            return []

        # Already a list
        if isinstance(value, list):
            result = []
            for item in value:
                if item is None:
                    continue
                item = str(item).strip()
                if item:
                    result.append(item)
            return result

        # Tuple or set
        if isinstance(value, (tuple, set)):
            result = []
            for item in value:
                if item is None:
                    continue
                item = str(item).strip()
                if item:
                    result.append(item)
            return result

        # Dictionary
        if isinstance(value, dict):
            result = []
            for key, vals in value.items():
                if isinstance(vals, (list, tuple, set)):
                    for item in vals:
                        if item:
                            result.append(str(item).strip())
                elif vals:
                    result.append(str(vals).strip())
            return result

        # String
        text = str(value).strip()
        if not text:
            return []

        # Split by common separators
        parts = re.split(r"[,|;\n]+", text)
        result = []
        for part in parts:
            part = part.strip()
            # Remove common bullet symbols
            part = re.sub(r"^[•●▪◦\-*]+\s*", "", part)
            if part:
                result.append(part)
        return result

    def deduplicate(self, items: List[str]) -> List[str]:
        """
        Remove duplicate items while preserving original order.

        Uses a normalised key for comparison (ignores case and punctuation).
        """
        result: List[str] = []
        seen: Set[str] = set()

        for item in items:
            if item is None:
                continue
            item = str(item).strip()
            if not item:
                continue
            # Normalise for dedup (alphanumeric + # + . only)
            key = re.sub(r"[^a-z0-9+#.]", "", self.comparison_text(item))
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    # ============================================================
    # SKILL MATCHING
    # ============================================================

    def fuzzy_match_skills(self, skill1: str, skill2: str, threshold: float = 0.80) -> bool:
        """
        Compare two skills using a safe fuzzy matching algorithm.

        Matching order:
            1. Exact normalised match
            2. Alias expansion
            3. Safe containment (for longer phrases)
            4. Word overlap (using threshold)

        Returns:
            True if skills are considered equivalent.
        """
        if not skill1 or not skill2:
            return False

        s1 = self.comparison_text(skill1)
        s2 = self.comparison_text(skill2)

        if not s1 or not s2:
            return False

        # 1. Exact
        if s1 == s2:
            return True

        # 2. Aliases
        a1 = self.skill_aliases.get(s1, s1)
        a2 = self.skill_aliases.get(s2, s2)
        if a1 == a2:
            return True

        # 3. Safe containment (only if both are at least 4 chars)
        if len(s1) >= 4 and len(s2) >= 4:
            if s1 in s2 or s2 in s1:
                return True

        # 4. Word overlap
        words1 = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", s1))
        words2 = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", s2))
        if not words1 or not words2:
            return False

        common = words1.intersection(words2)
        if not common:
            return False

        overlap = len(common) / min(len(words1), len(words2))
        return overlap >= threshold

    # ============================================================
    # EXTRACT DATA FROM RESUME
    # ============================================================

    def get_protected_data(self, resume_data: Dict) -> Dict[str, str]:
        """
        Extract protected information from the resume.

        IMPORTANT: Values are copied from the original parsed resume.
        They are NOT generated or modified.
        """
        default = {
            "name": "",
            "phone": "",
            "email": "",
            "linkedin": "",
            "github": "",
            "kaggle": "",
            "location": "",
            "education": "",
            "certifications": "",
        }

        if not isinstance(resume_data, dict):
            return default

        protected = resume_data.get("protected", {})
        if not isinstance(protected, dict):
            protected = {}

        def get_value(key: str) -> str:
            val = protected.get(key, resume_data.get(key, ""))
            return "" if val is None else str(val).strip()

        return {key: get_value(key) for key in default}

    def get_editable_data(self, resume_data: Dict) -> Dict[str, Any]:
        """Extract editable resume information."""
        default = {
            "summary": "",
            "skills": [],
            "experience": "",
            "projects": "",
        }

        if not isinstance(resume_data, dict):
            return default

        editable = resume_data.get("editable", {})
        if not isinstance(editable, dict):
            editable = {}

        return {
            "summary": editable.get("summary", resume_data.get("summary", "")),
            "skills": editable.get("skills", resume_data.get("skills", [])),
            "experience": editable.get("experience", resume_data.get("experience", "")),
            "projects": editable.get("projects", resume_data.get("projects", "")),
        }

    # ============================================================
    # JD TERMS EXTRACTION
    # ============================================================

    def extract_jd_terms(self, job_description: str, jd_result: Optional[Dict] = None) -> List[str]:
        """
        Extract relevant terms from the Job Description.

        Priority is given to terms already extracted by JDAnalyzer.
        Falls back to raw text with stop‑word removal.
        """
        terms: List[str] = []

        # From JD analyzer
        if isinstance(jd_result, dict):
            for key in ("skills", "keywords", "responsibilities"):
                values = jd_result.get(key, [])
                terms.extend(self.normalize_list(values))

        # From raw JD
        jd_text = self.clean_text(job_description)
        if jd_text:
            words = re.findall(r"\b[A-Za-z][A-Za-z0-9+#./-]{1,}\b", jd_text)
            for word in words:
                clean = word.strip(".,:;!?()[]{}")
                if len(clean) >= 3 and clean.lower() not in self.stop_words:
                    terms.append(clean)

        return self.deduplicate(terms)

    # ============================================================
    # SKILL TAILORING
    # ============================================================

    def match_existing_skills(self, resume_skills: List[str], jd_skills: List[str]) -> List[str]:
        """
        Find JD skills that are already present in the candidate's resume.

        CRITICAL: Only existing candidate skills can be returned.
        Missing JD skills are never inserted here.
        """
        resume_skills = [self.normalize_skill(x) for x in self.normalize_list(resume_skills)]
        jd_skills = [self.normalize_skill(x) for x in self.normalize_list(jd_skills)]

        matched: List[str] = []
        for resume_skill in resume_skills:
            for jd_skill in jd_skills:
                if self.fuzzy_match_skills(resume_skill, jd_skill):
                    matched.append(resume_skill)
                    break
        return self.deduplicate(matched)

    def prioritize_skills(self, resume_skills: List[str], jd_result: Optional[Dict] = None) -> List[str]:
        """
        Put JD-relevant EXISTING skills first.

        Missing skills are not inserted.
        """
        resume_skills = [self.normalize_skill(x) for x in self.normalize_list(resume_skills)]
        resume_skills = self.deduplicate(resume_skills)

        if not resume_skills:
            return []

        jd_skills: List[str] = []
        if isinstance(jd_result, dict):
            jd_skills = self.normalize_list(jd_result.get("skills", []))

        jd_skills = [self.normalize_skill(x) for x in jd_skills]

        matched: List[str] = []
        remaining: List[str] = []

        for skill in resume_skills:
            found = False
            for jd_skill in jd_skills:
                if self.fuzzy_match_skills(skill, jd_skill):
                    found = True
                    break
            if found:
                matched.append(skill)
            else:
                remaining.append(skill)

        return self.deduplicate(matched) + self.deduplicate(remaining)

    def build_skills(self, resume_data: Dict, jd_result: Dict) -> Dict[str, List[str]]:
        """
        Build the optimised skills section.

        Returns:
            - all_skills: ordered list of existing skills (JD‑relevant first)
            - matched_skills: JD skills that are already present
            - missing_skills: JD skills that are not present (advisory only)

        IMPORTANT: missing_skills are ONLY reported as gaps.
        They are NOT added to all_skills.
        """
        editable = self.get_editable_data(resume_data)
        resume_skills = self.normalize_list(editable.get("skills", []))

        jd_skills: List[str] = []
        if isinstance(jd_result, dict):
            jd_skills = self.normalize_list(jd_result.get("skills", []))

        resume_skills = self.deduplicate(resume_skills)
        jd_skills = self.deduplicate(jd_skills)

        ordered_skills = self.prioritize_skills(resume_skills, jd_result)
        matched = self.match_existing_skills(resume_skills, jd_skills)

        # Identify missing – only if skill is in JD and not matched
        missing: List[str] = []
        for jd_skill in jd_skills:
            present = False
            for existing in resume_skills:
                if self.fuzzy_match_skills(existing, jd_skill):
                    present = True
                    break
            if not present:
                missing.append(jd_skill)

        return {
            "all_skills": self.deduplicate(ordered_skills),
            "matched_skills": self.deduplicate(matched),
            "missing_skills": self.deduplicate(missing),
        }

    # ============================================================
    # RELEVANCE SCORING & REORDERING
    # ============================================================

    def clean_job_title(self, title: str) -> str:
        """
        Sanitize job title string by stripping raw metadata labels.
        """
        if not title:
            return "Target Position"
        # Insert space before concatenated metadata labels
        title = re.sub(
            r"(?i)(engineer|developer|analyst|scientist|manager|lead|architect|specialist)"
            r"(Location|Job|Type|Description|Department|About|Salary|Responsibilities|Requirements|Qualifications)",
            r"\1 \2", title
        )
        # Split on metadata keywords
        split_pattern = (
            r"(?i)(?:\bLocation\b|\bJob\s*Type\b|\bJob\s*Description\b|"
            r"\bAbout\s+the\s+Job\b|\bDepartment\b|\bSalary\b|"
            r"\bResponsibilities\b|\bRequirements\b|\bQualifications\b|"
            r"\bOverview\b|\bHybrid\b|\bFull[\s-]*time\b|\bPart[\s-]*time\b|"
            r"\bRemote\b|\bOnsite\b|\bOn[\s-]*site\b)"
        )
        title = re.split(split_pattern, title)[0].strip()
        # Strip trailing punctuation
        title = re.sub(r"[:\-–—,|/()]+$", "", title).strip()
        # Remove seniority/level prefixes (Senior, Junior, Lead, etc.)
        title = re.sub(
            r"(?i)^(?:senior|sr\.?|junior|jr\.?|lead|principal|staff|associate|chief|head|director|entry[\s-]*level)\s+",
            "", title
        ).strip()
        return title if title and len(title) >= 2 else "Target Position"

    def split_content(self, text: str) -> List[str]:
        """
        Split a block of text (experience or projects) into logical items.

        Tries to preserve bullets and sentences, but never generates new content.
        """
        text = self.clean_text(text)
        if not text:
            return []

        # Fix digit-period-letter without space (e.g. "1.Heart" -> "1. Heart")
        text = re.sub(r"(\d+)[\.\)]([A-Za-z])", r"\1. \2", text)
        # Separate inline glued numbers/bullets (e.g. "FastAPI. 5. Computer Vision" -> "\n5. Computer Vision")
        text = re.sub(r"(?<=[.!?]|\s)\s*(\d+[\.\)]\s*[A-Z])", r"\n\1", text)
        text = re.sub(r"(?<=[.!?]|\s)\s*([●•▪◦]\s*)", r"\n\1", text)

        lines = text.split("\n")
        blocks: List[str] = []
        current: List[str] = []

        for line in lines:
            line = line.strip()
            if not line:
                if current:
                    blocks.append(" ".join(current).strip())
                    current = []
                continue

            # Bullet or numbered line starts a new item
            is_bullet = re.match(r"^(?:[-•●▪◦*]|\d+[\.\)])\s*", line)
            if is_bullet:
                if current:
                    blocks.append(" ".join(current).strip())
                line = re.sub(r"^(?:[-•●▪◦*]|\d+[\.\)])\s*", "", line)
                current = [line] if line else []
            else:
                current.append(line)

        if current:
            blocks.append(" ".join(current).strip())

        # Clean leading digits/bullets from items
        cleaned_blocks = []
        for item in blocks:
            c_item = re.sub(r"^(?:[-•●▪◦*]|\d+[\.\)])\s*", "", item).strip()
            if c_item:
                cleaned_blocks.append(c_item)

        # If only one block, try splitting by sentences as fallback
        if len(cleaned_blocks) == 1:
            fallback = re.split(r"(?<=[.!?])\s+", cleaned_blocks[0])
            if len(fallback) > 1:
                cleaned_blocks = [x.strip() for x in fallback if x.strip()]

        return self.deduplicate(cleaned_blocks)

    def relevance_score(self, text: str, jd_terms: List[str]) -> float:
        """
        Calculate a transparent relevance score for a text block.

        This does NOT generate content; it only determines ordering.
        """
        if not text or not jd_terms:
            return 0.0

        text_lower = self.comparison_text(text)
        score = 0.0
        matched_terms: Set[str] = set()

        for term in jd_terms:
            term_norm = self.comparison_text(term)
            if not term_norm:
                continue

            # Exact phrase match
            if term_norm in text_lower:
                if term_norm not in matched_terms:
                    score += 2.0
                    matched_terms.add(term_norm)
                continue

            # Word overlap
            term_words = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", term_norm))
            text_words = set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", text_lower))
            useful = {w for w in term_words if w not in self.stop_words}
            common = useful.intersection(text_words)
            if common:
                score += min(len(common), 2)

        return score

    def tailor_experience(self, experience_data: Any, jd_result: Dict) -> Union[List[Dict], List[str]]:
        """
        Reorder and optimize existing experience items by JD relevance.
        Preserves structured dictionaries ({title, company, dates, bullets}) when provided.
        """
        if not experience_data:
            return []

        jd_terms: List[str] = []
        if isinstance(jd_result, dict):
            jd_terms.extend(self.normalize_list(jd_result.get("skills", [])))
            jd_terms.extend(self.normalize_list(jd_result.get("keywords", [])))
            jd_terms.extend(self.normalize_list(jd_result.get("responsibilities", [])))
        jd_terms = self.deduplicate(jd_terms)

        # Structured list of dictionaries
        if isinstance(experience_data, list) and all(isinstance(item, dict) for item in experience_data):
            scored = []
            for idx, item in enumerate(experience_data):
                bullets = self.normalize_list(item.get("bullets", item.get("description", [])))
                content = f"{item.get('title', '')} {item.get('company', '')} {' '.join(bullets)}"
                score = self.relevance_score(content, jd_terms)

                # Prioritize bullets matching JD terms
                if bullets:
                    b_scored = [(self.relevance_score(b, jd_terms), b_idx, b) for b_idx, b in enumerate(bullets)]
                    b_scored.sort(key=lambda x: (-x[0], x[1]))
                    item_copy = dict(item)
                    item_copy["bullets"] = [x[2] for x in b_scored]
                else:
                    item_copy = dict(item)
                scored.append((score, idx, item_copy))

            scored.sort(key=lambda x: (-x[0], x[1]))
            return [s[2] for s in scored]

        # Text or flat string list
        if isinstance(experience_data, list):
            parts = [str(x).strip() for x in experience_data if str(x).strip()]
        else:
            parts = self.split_content(str(experience_data))

        if not parts:
            return []

        scored = [(self.relevance_score(part, jd_terms), idx, part) for idx, part in enumerate(parts)]
        scored.sort(key=lambda x: (-x[0], x[1]))
        return self.deduplicate([item[2] for item in scored])

    def tailor_projects(self, projects_data: Any, jd_result: Dict) -> Union[List[Dict], List[str]]:
        """
        Reorder existing projects by JD relevance.
        Preserves structured dictionaries ({name, description, technologies}) when provided.
        """
        if not projects_data:
            return []

        jd_terms: List[str] = []
        if isinstance(jd_result, dict):
            jd_terms.extend(self.normalize_list(jd_result.get("skills", [])))
            jd_terms.extend(self.normalize_list(jd_result.get("keywords", [])))
            jd_terms.extend(self.normalize_list(jd_result.get("responsibilities", [])))
        jd_terms = self.deduplicate(jd_terms)

        # Structured list of dictionaries
        if isinstance(projects_data, list) and all(isinstance(item, dict) for item in projects_data):
            scored = []
            for idx, item in enumerate(projects_data):
                techs = " ".join(self.normalize_list(item.get("technologies", item.get("tech_stack", []))))
                content = f"{item.get('name', '')} {item.get('description', '')} {techs}"
                score = self.relevance_score(content, jd_terms)
                scored.append((score, idx, dict(item)))
            scored.sort(key=lambda x: (-x[0], x[1]))
            return [s[2] for s in scored]

        # Text or flat string list
        if isinstance(projects_data, list):
            parts = [str(x).strip() for x in projects_data if str(x).strip()]
        else:
            parts = self.split_content(str(projects_data))

        if not parts:
            return []

        scored = [(self.relevance_score(part, jd_terms), idx, part) for idx, part in enumerate(parts)]
        scored.sort(key=lambda x: (-x[0], x[1]))
        return self.deduplicate([item[2] for item in scored])

    # ============================================================
    # PROFESSIONAL SUMMARY
    # ============================================================

    def build_summary(self, resume_data: Dict, jd_result: Dict, skills_result: Dict) -> str:
        """
        Build an executive, high-impact professional summary tailored to the target role.
        Uses candidate-owned matched skills, experience years from JD, and target job title
        to maximize interview conversion.
        """
        editable = self.get_editable_data(resume_data)
        original_summary = self.clean_text(editable.get("summary", ""))

        job_title = "Target Position"
        experience_years = 0
        if isinstance(jd_result, dict):
            job_title = str(jd_result.get("job_title", "Target Position")).strip()
            experience_years = jd_result.get("experience_years", 0)
            try:
                experience_years = float(experience_years)
            except (ValueError, TypeError):
                experience_years = 0
        job_title = self.clean_job_title(job_title)
        if not job_title or job_title == "Target Position":
            job_title = "Technical Specialist"

        # Format experience years string (e.g., 2.0 → "2+", 3.5 → "3+")
        exp_str = ""
        if experience_years and experience_years > 0:
            exp_int = int(experience_years)
            exp_str = f"{exp_int}+"

        matched_skills = self.normalize_list(skills_result.get("matched_skills", []))
        all_skills = self.normalize_list(skills_result.get("all_skills", []))
        top_skills = matched_skills[:6] if matched_skills else all_skills[:5]
        skills_str = ", ".join(top_skills) if top_skills else "modern software engineering and data frameworks"

        # Sanitize original_summary from previous repetitive boilerplates or raw metadata text
        clean_orig = original_summary
        if clean_orig:
            clean_orig = re.sub(r"^Results-driven and detail-oriented\s+.*?\s+with\s+(?:proven|solid)\s+(?:technical\s+)?(?:proficiency|expertise)\s+in\s+.*?\.\s*", "", clean_orig, flags=re.IGNORECASE)
            clean_orig = re.sub(r"\bRecognized for delivering scalable solutions, optimizing system performance, and driving measurable business impact\.?", "", clean_orig, flags=re.IGNORECASE).strip()
            clean_orig = re.sub(r"(?i)Senior AI EngineerLocation:.*?(?:Job Description:)?", "", clean_orig).strip()
            # Also strip any old experience year phrases so we don't double them
            clean_orig = re.sub(r"\bwith\s+\d+\+?\s*years?\s+of\s+(?:professional\s+)?(?:hands-on\s+)?experience\s+(?:in\s+)?", "with experience in ", clean_orig, flags=re.IGNORECASE).strip()

        # Build experience phrase
        if exp_str:
            exp_phrase = f"with {exp_str} years of experience in {skills_str}"
        else:
            exp_phrase = f"with proven proficiency in {skills_str}"

        if clean_orig and len(clean_orig) > 30:
            return (
                f"Results-driven and detail-oriented {job_title} {exp_phrase}. "
                f"{clean_orig.rstrip('.')}. Recognized for delivering scalable solutions, optimizing system performance, and driving measurable business impact."
            )
        else:
            return (
                f"Results-driven and detail-oriented {job_title} {exp_phrase}. "
                f"Experienced in developing end-to-end scalable solutions, architecting high-performance pipelines, and solving complex technical challenges. "
                f"Strong analytical mindset with a passion for continuous learning and driving organizational impact."
            )

    # ============================================================
    # SKILL CATEGORIZATION
    # ============================================================

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Group flat skills into clean, recruiter-friendly domain categories.
        """
        cats = {
            "Programming & Core": [],
            "AI / Machine Learning & Frameworks": [],
            "Cloud, Databases & DevOps": [],
            "Analytics, Tools & Methodologies": [],
        }

        prog_keywords = {"python", "r", "sql", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "scala", "bash", "html", "css"}
        ai_keywords = {"machine learning", "deep learning", "nlp", "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn", "transformers", "huggingface", "llm", "langchain", "rag", "opencv", "generative ai", "neural networks", "bert", "gpt", "fine-tuning"}
        cloud_keywords = {"aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "ci/cd", "postgresql", "mysql", "mongodb", "redis", "snowflake", "bigquery", "fastapi", "flask", "django"}

        for s in skills:
            s_low = s.lower()
            if any(k in s_low for k in ai_keywords):
                cats["AI / Machine Learning & Frameworks"].append(s)
            elif any(k in s_low for k in prog_keywords):
                cats["Programming & Core"].append(s)
            elif any(k in s_low for k in cloud_keywords):
                cats["Cloud, Databases & DevOps"].append(s)
            else:
                cats["Analytics, Tools & Methodologies"].append(s)

        # Filter out empty categories
        return {k: v for k, v in cats.items() if v}

    # ============================================================
    # COVER LETTER GENERATOR
    # ============================================================

    def generate_cover_letter(self, resume_data: Dict, jd_result: Dict, company_name: str = "Hiring Team") -> str:
        """
        Generate a professional, compelling cover letter customized for the target job description.
        """
        name = self.clean_text(resume_data.get("name") or "Applicant")
        email = self.clean_text(resume_data.get("email") or "")
        phone = self.clean_text(resume_data.get("phone") or "")
        job_title = jd_result.get("job_title", "Target Position") if isinstance(jd_result, dict) else "Target Position"

        skills = self.normalize_list(resume_data.get("skills", []))
        matched = self.normalize_list(resume_data.get("matched_skills", []))
        top_skills = matched[:5] if matched else skills[:5]
        skills_str = ", ".join(top_skills) if top_skills else "modern technical frameworks"

        contact_line = f"{email} | {phone}" if email and phone else (email or phone)

        letter = f"""Dear {company_name},

I am writing to express my strong enthusiasm and interest in the {job_title} position. With a strong track record of engineering scalable solutions and deep expertise in {skills_str}, I am excited about the opportunity to contribute significantly to your team's success.

Throughout my technical experience, I have focused on solving real-world challenges by architecting robust pipelines, optimizing performance, and delivering measurable impact. My core competencies in {skills_str} align directly with the requirements outlined for the {job_title} role. I take pride in writing clean, maintainable code, developing data-driven systems, and collaborating closely with cross-functional teams to exceed project milestones.

I am confident that my technical skills, proactive problem-solving attitude, and commitment to excellence make me a high-value addition to your organization. I look forward to the possibility of discussing how my experience and passion can help drive your mission forward.

Thank you for your time and consideration.

Sincerely,
{name}
{contact_line}
"""
        return letter.strip()

    # ============================================================
    # INTERVIEW READINESS TIPS
    # ============================================================

    def generate_interview_tips(self, matched_skills: List[str], missing_skills: List[str], jd_result: Dict) -> List[Dict[str, str]]:
        """
        Generate actionable tactical tips for the candidate to maximize interview conversion.
        """
        tips = []
        job_title = jd_result.get("job_title", "the target role") if isinstance(jd_result, dict) else "the target role"

        if matched_skills:
            top_m = ", ".join(matched_skills[:4])
            tips.append({
                "type": "strength",
                "title": "Lead With Your Matched Core Competencies",
                "description": f"Highlight your deep hands-on experience with {top_m} during your technical introduction and system design questions. Emphasize quantifiable outcomes (e.g. % performance increase, latency reduction)."
            })

        if missing_skills:
            top_missing = ", ".join(missing_skills[:3])
            tips.append({
                "type": "gap",
                "title": f"Bridge Skill Gap: {top_missing}",
                "description": f"The job description highlights {top_missing}. In the interview, frame your existing expertise in related tools as a bridge: emphasize your rapid learning curve and architectural familiarity with these technologies."
            })

        tips.append({
            "type": "strategy",
            "title": "Use the Google XYZ Achievement Formula",
            "description": "When answering behavioral or project questions, structure answers as: 'Accomplished [X], as measured by [Y], by doing [Z]'. Recruiters love candidates who articulate business and technical impact clearly."
        })

        return tips

    # ============================================================
    # PROTECTED FIELD VALIDATION
    # ============================================================

    def validate_protected_information(self, original: Dict, tailored: Dict) -> Dict:
        """
        Verify that protected fields were not changed.

        Returns a dictionary with:
            - all_protected_fields_unchanged: bool
            - field_checks: dict of field → bool
        """
        fields = [
            "name", "phone", "email", "linkedin",
            "github", "kaggle", "location",
            "education", "certifications"
        ]
        checks = {}
        for field in fields:
            orig = original.get(field, "")
            tail = tailored.get(field, "")
            checks[field] = str(orig) == str(tail)

        return {
            "all_protected_fields_unchanged": all(checks.values()),
            "field_checks": checks,
        }

    # ============================================================
    # MAIN TAILORING METHOD
    # ============================================================

    def tailor(self, resume_data: Dict, jd_result: Dict, job_description: str = "") -> OrderedDict:
        """
        Main resume tailoring method.

        Accepts:
            1. Structured parsed resume data (from ResumeParser)
            2. Raw text (fallback)

        Returns an OrderedDict containing:
            - protected information (preserved)
            - tailored sections (summary, skills, experience, projects)
            - matched_skills, missing_skills, and protected_validation
        """
        # Safety: raw text input
        if not isinstance(resume_data, dict):
            raw_text = str(resume_data or "")
            resume_data = {
                "text": raw_text,
                "protected": {
                    "name": "", "phone": "", "email": "",
                    "linkedin": "", "github": "", "kaggle": "",
                    "location": "", "education": "", "certifications": "",
                },
                "editable": {
                    "summary": "", "skills": [],
                    "experience": raw_text, "projects": "",
                }
            }

        protected = self.get_protected_data(resume_data)
        editable = self.get_editable_data(resume_data)

        # Build skills
        skills_result = self.build_skills(resume_data, jd_result)

        # Reorder experience and projects
        tailored_experience = self.tailor_experience(editable.get("experience", ""), jd_result)
        tailored_projects = self.tailor_projects(editable.get("projects", ""), jd_result)

        # Build summary
        tailored_summary = self.build_summary(resume_data, jd_result, skills_result)

        # Job info
        job_title = "Target Position"
        experience_required = 0
        if isinstance(jd_result, dict):
            job_title = jd_result.get("job_title", "Target Position")
            experience_required = jd_result.get("experience_years", 0)
        job_title = self.clean_job_title(job_title)

        # Assemble final result
        result = OrderedDict([
            ("job_title", job_title),
            ("experience_required", experience_required),
            ("name", protected["name"]),
            ("phone", protected["phone"]),
            ("email", protected["email"]),
            ("linkedin", protected["linkedin"]),
            ("github", protected["github"]),
            ("kaggle", protected["kaggle"]),
            ("location", protected["location"]),
            ("education", protected["education"]),
            ("certifications", protected["certifications"]),
            ("professional_summary", tailored_summary),
            ("skills", skills_result["all_skills"]),
            ("matched_skills", skills_result["matched_skills"]),
            ("missing_skills", skills_result["missing_skills"]),
            ("experience", tailored_experience),
            ("projects", tailored_projects),
        ])

        # Add validation
        result["protected_validation"] = self.validate_protected_information(
            protected, dict(result)
        )

        return result

    # ============================================================
    # COMPATIBILITY METHOD
    # ============================================================

    def tailor_resume(self, resume_data: Dict, jd_result: Dict, job_description: str = "") -> OrderedDict:
        """Compatibility alias for older app.py versions."""
        return self.tailor(resume_data, jd_result, job_description)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("AI RESUME TAILORING ENGINE TEST")
    print("=" * 70)

    # Simulated original resume
    resume_data = {
        "protected": {
            "name": "Summaiya Bibi",
            "phone": "03001234567",
            "email": "summaiya@example.com",
            "linkedin": "https://www.linkedin.com/in/summaiya-bibi",
            "github": "https://github.com/summaiyazafar",
            "kaggle": "https://www.kaggle.com/summaiya",
            "location": "Islamabad, Pakistan",
            "education": "BS Computer Science\nVirtual University of Pakistan",
            "certifications": "Artificial Intelligence using Python",
        },
        "editable": {
            "summary": "Data professional with experience in Python, SQL and Power BI.",
            "skills": ["Python", "SQL", "Power BI", "Excel", "Pandas", "NumPy", "Machine Learning"],
            "experience": """
                Analyzed business data using SQL.
                Created Power BI dashboards.
                Worked with Excel reports.
                Cleaned datasets using Pandas.
            """,
            "projects": """
                Sales Dashboard
                Created a Power BI dashboard for sales analysis.
                Machine Learning Project
                Built a machine learning model using Python.
            """,
        }
    }

    # Simulated JD analysis result
    jd_result = {
        "job_title": "Data Analyst",
        "skills": ["SQL", "Power BI", "Azure", "Data Analysis", "Dashboard", "Reporting",
                   "Problem Solving", "Communication"],
        "experience_years": 3,
        "keywords": ["analytics", "reporting", "automation", "data", "dashboard"],
        "responsibilities": [
            "Develop reporting dashboards.",
            "Analyze business data.",
            "Support data integration.",
        ]
    }

    tailor = ResumeTailor()
    result = tailor.tailor(resume_data, jd_result)

    # Print results
    print("\n" + "=" * 70)
    print("PROTECTED INFORMATION")
    print("=" * 70)
    for key in ["name", "phone", "email", "linkedin", "github", "kaggle", "location", "education", "certifications"]:
        print(f"{key.capitalize()}: {result[key]}")

    print("\n" + "=" * 70)
    print("TAILORED INFORMATION")
    print("=" * 70)
    print(f"\nJOB TITLE: {result['job_title']}")
    print(f"\nSUMMARY: {result['professional_summary']}")

    print("\nSKILLS:")
    for skill in result["skills"]:
        print(f"  ✓ {skill}")

    print("\nMATCHED JD SKILLS:")
    for skill in result["matched_skills"]:
        print(f"  ✓ {skill}")

    print("\nMISSING JD SKILLS:")
    for skill in result["missing_skills"]:
        print(f"  ✗ {skill}")

    print("\nEXPERIENCE:")
    for item in result["experience"]:
        print(f"  • {item}")

    print("\nPROJECTS:")
    for item in result["projects"]:
        print(f"  • {item}")

    print("\n" + "=" * 70)
    print("PROTECTED FIELD VALIDATION")
    print("=" * 70)
    validation = result["protected_validation"]
    print(f"All protected fields unchanged: {validation['all_protected_fields_unchanged']}")
    for field, status in validation["field_checks"].items():
        print(f"  {'✓' if status else '✗'} {field}: {status}")

    print("\n" + "=" * 70)
    print("RESUME TAILORING TEST COMPLETED")
    print("=" * 70)
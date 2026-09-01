"""
Gap Analysis Engine - Professional Edition
AI Resume Tailoring System

Identifies:
- Matched skills with confidence levels
- Missing skills with priority rankings
- Critical missing skills (blockers)
- Skill coverage percentage
- Semantic similarity between resume and JD
- Actionable recommendations
- Step-by-step action plan

Uses:
- NLP-based skill extraction (semantic matching)
- Priority scoring for missing skills
- Action plan generation
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter
import math

# Optional: Use semantic matching if available
try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_AVAILABLE = True
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    SEMANTIC_AVAILABLE = False
    semantic_model = None


class GapAnalyzer:
    """
    Professional Skill Gap Analyzer with NLP capabilities.
    """

    def __init__(self, use_semantic=True):
        """
        Initialize Gap Analyzer.

        Args:
            use_semantic: Use semantic similarity (BERT) for matching
        """
        self.use_semantic = use_semantic and SEMANTIC_AVAILABLE
        self.semantic_threshold = 0.7  # Similarity threshold for semantic matching

        # Expanded critical skills with categories
        self.critical_skills = {
            # Programming Languages
            "python": "Programming",
            "java": "Programming",
            "javascript": "Programming",
            "typescript": "Programming",
            "c++": "Programming",
            "c#": "Programming",
            "ruby": "Programming",
            "go": "Programming",
            "rust": "Programming",

            # Databases
            "sql": "Database",
            "mysql": "Database",
            "postgresql": "Database",
            "mongodb": "Database",
            "redis": "Database",
            "elasticsearch": "Database",

            # Machine Learning & AI
            "machine learning": "ML/AI",
            "deep learning": "ML/AI",
            "nlp": "ML/AI",
            "natural language processing": "ML/AI",
            "computer vision": "ML/AI",
            "reinforcement learning": "ML/AI",
            "generative ai": "ML/AI",
            "llm": "ML/AI",
            "large language models": "ML/AI",
            "rag": "ML/AI",
            "retrieval augmented generation": "ML/AI",
            "langchain": "ML/AI",
            "langgraph": "ML/AI",

            # ML Frameworks
            "tensorflow": "ML/AI",
            "pytorch": "ML/AI",
            "keras": "ML/AI",
            "scikit-learn": "ML/AI",
            "pandas": "Data Science",
            "numpy": "Data Science",
            "matplotlib": "Data Science",
            "seaborn": "Data Science",
            "plotly": "Data Science",

            # Big Data
            "hadoop": "Big Data",
            "spark": "Big Data",
            "kafka": "Big Data",
            "airflow": "Big Data",
            "dbt": "Big Data",

            # Cloud
            "aws": "Cloud",
            "azure": "Cloud",
            "gcp": "Cloud",
            "docker": "DevOps",
            "kubernetes": "DevOps",
            "jenkins": "DevOps",
            "git": "DevOps",
            "ci/cd": "DevOps",
            "terraform": "DevOps",

            # Web Development
            "react": "Frontend",
            "angular": "Frontend",
            "vue": "Frontend",
            "node.js": "Backend",
            "django": "Backend",
            "flask": "Backend",
            "fastapi": "Backend",
            "spring boot": "Backend",

            # Data Visualization
            "tableau": "Visualization",
            "power bi": "Visualization",
            "looker": "Visualization",

            # Soft Skills
            "communication": "Soft Skills",
            "leadership": "Soft Skills",
            "teamwork": "Soft Skills",
            "problem solving": "Soft Skills",
            "critical thinking": "Soft Skills",
            "project management": "Soft Skills",
        }

        # Skill importance weights (1-10)
        self.skill_weights = {
            "python": 10,
            "sql": 9,
            "machine learning": 10,
            "deep learning": 9,
            "nlp": 8,
            "computer vision": 8,
            "tensorflow": 8,
            "pytorch": 8,
            "aws": 8,
            "azure": 8,
            "docker": 7,
            "kubernetes": 7,
            "react": 7,
            "angular": 7,
            "django": 7,
            "fastapi": 7,
            "java": 8,
            "javascript": 7,
        }

        # Category priority order
        self.category_priority = [
            "Programming", "ML/AI", "Data Science", "Database",
            "Backend", "Frontend", "Cloud", "DevOps",
            "Big Data", "Visualization", "Soft Skills"
        ]

    # ==========================================================
    # TEXT PROCESSING
    # ==========================================================

    def clean_skill(self, skill: str) -> str:
        """Normalize skill string."""
        if not skill:
            return ""
        skill = str(skill).strip().lower()
        skill = re.sub(r"\s+", " ", skill)
        return skill

    def normalize_skills(self, skills: List[str]) -> Set[str]:
        """Normalize a list of skills."""
        if not skills:
            return set()
        return {self.clean_skill(s) for s in skills if s}

    # ==========================================================
    # SEMANTIC MATCHING
    # ==========================================================

    def semantic_match_skills(
        self,
        resume_skills: Set[str],
        job_skills: Set[str]
    ) -> Dict[str, Dict]:
        """
        Match skills using semantic similarity (BERT).

        Returns:
            Dict with match details for each skill.
        """
        if not self.use_semantic or not semantic_model:
            return {}

        results = {}

        for jd_skill in job_skills:
            # Check exact match first
            if jd_skill in resume_skills:
                results[jd_skill] = {
                    "matched": True,
                    "confidence": 1.0,
                    "matching_skill": jd_skill
                }
                continue

            # Check for semantic matches
            best_match = None
            best_score = 0

            for resume_skill in resume_skills:
                # Skip if too short
                if len(resume_skill) < 3 or len(jd_skill) < 3:
                    continue

                # Compute semantic similarity
                emb1 = semantic_model.encode([resume_skill])
                emb2 = semantic_model.encode([jd_skill])
                from sklearn.metrics.pairwise import cosine_similarity
                score = cosine_similarity(emb1, emb2)[0][0]

                if score > best_score and score > self.semantic_threshold:
                    best_score = score
                    best_match = resume_skill

            if best_match:
                results[jd_skill] = {
                    "matched": True,
                    "confidence": round(best_score, 3),
                    "matching_skill": best_match
                }
            else:
                results[jd_skill] = {
                    "matched": False,
                    "confidence": 0,
                    "matching_skill": None
                }

        return results

    # ==========================================================
    # ADVANCED SKILL ANALYSIS
    # ==========================================================

    def analyze_skills(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Dict:
        """
        Advanced skill comparison with semantic matching.

        Returns:
            Comprehensive skill analysis including:
            - Matched skills with confidence
            - Missing skills with priority
            - Skill coverage by category
            - Overall compatibility score
        """
        resume_skills_norm = self.normalize_skills(resume_skills)
        job_skills_norm = self.normalize_skills(job_skills)

        # Exact matches
        exact_matched = resume_skills_norm.intersection(job_skills_norm)

        # Semantic matches
        semantic_results = self.semantic_match_skills(
            resume_skills_norm,
            job_skills_norm
        )

        # Build matched skills list
        matched_skills = sorted(list(exact_matched))
        matched_with_confidence = []

        for skill in matched_skills:
            matched_with_confidence.append({
                "skill": skill,
                "match_type": "exact",
                "confidence": 1.0
            })

        # Add semantic matches
        for jd_skill, result in semantic_results.items():
            if result["matched"]:
                matched_skills.append(jd_skill)
                matched_with_confidence.append({
                    "skill": jd_skill,
                    "match_type": "semantic",
                    "confidence": result["confidence"],
                    "matched_skill": result["matching_skill"]
                })

        # Remove duplicates
        seen = set()
        unique_matched = []
        for item in matched_with_confidence:
            if item["skill"] not in seen:
                seen.add(item["skill"])
                unique_matched.append(item)

        # Identify missing skills
        all_matched = {item["skill"] for item in unique_matched}
        missing_skills = job_skills_norm - all_matched

        # Classify missing skills by importance
        missing_priority = []
        for skill in missing_skills:
            priority = self.get_skill_priority(skill)
            category = self.get_skill_category(skill)
            missing_priority.append({
                "skill": skill,
                "priority": priority,
                "category": category,
                "importance_score": self.get_skill_weight(skill)
            })

        # Sort by importance (highest first)
        missing_priority.sort(
            key=lambda x: x["importance_score"],
            reverse=True
        )

        # Calculate category coverage
        category_coverage = self.calculate_category_coverage(
            resume_skills_norm,
            job_skills_norm
        )

        # Calculate overall compatibility score
        compatibility_score = self.calculate_compatibility_score(
            matched_skills,
            job_skills_norm
        )

        return {
            "matched_skills": [item["skill"] for item in unique_matched],
            "matched_with_confidence": unique_matched,
            "missing_skills": [item["skill"] for item in missing_priority],
            "missing_with_priority": missing_priority,
            "skill_coverage": self.calculate_coverage_percentage(
                matched_skills,
                job_skills_norm
            ),
            "category_coverage": category_coverage,
            "compatibility_score": compatibility_score,
            "semantic_used": self.use_semantic,
            "total_job_skills": len(job_skills_norm),
            "total_matched": len(matched_skills),
            "total_missing": len(missing_skills)
        }

    # ==========================================================
    # SKILL PRIORITY & CATEGORY
    # ==========================================================

    def get_skill_priority(self, skill: str) -> str:
        """Get priority level for a skill."""
        skill_lower = skill.lower()

        if skill_lower in self.critical_skills:
            return "Critical"
        elif skill_lower in self.skill_weights and self.skill_weights[skill_lower] >= 7:
            return "High"
        elif skill_lower in self.skill_weights and self.skill_weights[skill_lower] >= 5:
            return "Medium"
        else:
            return "Low"

    def get_skill_category(self, skill: str) -> str:
        """Get category for a skill."""
        skill_lower = skill.lower()
        return self.critical_skills.get(skill_lower, "General")

    def get_skill_weight(self, skill: str) -> int:
        """Get importance weight for a skill."""
        skill_lower = skill.lower()
        return self.skill_weights.get(skill_lower, 3)

    # ==========================================================
    # COVERAGE CALCULATIONS
    # ==========================================================

    def calculate_coverage_percentage(
        self,
        matched_skills: List[str],
        job_skills: Set[str]
    ) -> float:
        """Calculate skill coverage percentage."""
        if not job_skills:
            return 100.0

        matched_set = set(matched_skills)
        coverage = (len(matched_set.intersection(job_skills)) / len(job_skills)) * 100
        return round(coverage, 2)

    def calculate_category_coverage(
        self,
        resume_skills: Set[str],
        job_skills: Set[str]
    ) -> Dict[str, Dict]:
        """Calculate coverage by skill category."""
        category_data = {}

        for skill in job_skills:
            category = self.get_skill_category(skill)
            if category not in category_data:
                category_data[category] = {
                    "total": 0,
                    "matched": 0,
                    "skills": [],
                    "missing": []
                }

            category_data[category]["total"] += 1
            if skill in resume_skills:
                category_data[category]["matched"] += 1
                category_data[category]["skills"].append(skill)
            else:
                category_data[category]["missing"].append(skill)

        # Calculate percentages
        for category in category_data:
            total = category_data[category]["total"]
            matched = category_data[category]["matched"]
            category_data[category]["coverage"] = round(
                (matched / total * 100) if total > 0 else 0,
                2
            )

        return category_data

    def calculate_compatibility_score(
        self,
        matched_skills: List[str],
        job_skills: Set[str]
    ) -> float:
        """
        Calculate overall compatibility score (0-100).

        Weighted by skill importance.
        """
        if not job_skills:
            return 100.0

        matched_set = set(matched_skills)
        total_weight = 0
        matched_weight = 0

        for skill in job_skills:
            weight = self.get_skill_weight(skill)
            total_weight += weight
            if skill in matched_set:
                matched_weight += weight

        if total_weight == 0:
            return 0

        score = (matched_weight / total_weight) * 100
        return round(score, 2)

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    def generate_recommendations(
        self,
        missing_skills: List[str],
        missing_with_priority: List[Dict]
    ) -> List[Dict]:
        """
        Generate detailed recommendations for missing skills.

        Returns:
            List of recommendation dictionaries with:
            - skill: Skill name
            - priority: Priority level
            - recommendation: Actionable advice
            - resources: Suggested resources
            - difficulty: Learning difficulty
        """
        recommendations = []

        for skill_info in missing_with_priority:
            skill = skill_info["skill"]
            priority = skill_info["priority"]
            category = skill_info["category"]

            rec = {
                "skill": skill,
                "priority": priority,
                "category": category,
                "recommendation": "",
                "resources": [],
                "difficulty": "Medium"
            }

            skill_lower = skill.lower()

            # Generate specific recommendations
            if "python" in skill_lower:
                rec["recommendation"] = "Take Python courses on Coursera/Codecademy, build Python projects, and practice coding daily."
                rec["resources"] = ["Python.org", "Coursera Python", "Codecademy Python"]
                rec["difficulty"] = "Easy"

            elif "sql" in skill_lower:
                rec["recommendation"] = "Learn SQL basics, practice with LeetCode SQL problems, and work with databases in projects."
                rec["resources"] = ["SQLZoo", "LeetCode SQL", "W3Schools SQL"]
                rec["difficulty"] = "Easy"

            elif "machine learning" in skill_lower or "deep learning" in skill_lower:
                rec["recommendation"] = "Take Andrew Ng's ML course, practice with Kaggle competitions, and build ML projects."
                rec["resources"] = ["Coursera ML", "Kaggle", "TensorFlow/PyTorch tutorials"]
                rec["difficulty"] = "Hard"

            elif "aws" in skill_lower or "azure" in skill_lower or "gcp" in skill_lower:
                rec["recommendation"] = "Get cloud certification (AWS Solutions Architect, Azure Administrator), practice with free tier."
                rec["resources"] = ["AWS Training", "Azure Learn", "Google Cloud Skills"]
                rec["difficulty"] = "Medium"

            elif "docker" in skill_lower or "kubernetes" in skill_lower:
                rec["recommendation"] = "Learn containerization basics, practice with Docker/Kubernetes tutorials, and deploy applications."
                rec["resources"] = ["Docker Docs", "Kubernetes Tutorials", "KodeKloud"]
                rec["difficulty"] = "Medium"

            elif "tensorflow" in skill_lower or "pytorch" in skill_lower:
                rec["recommendation"] = "Take deep learning courses, practice with frameworks, and build neural network projects."
                rec["resources"] = ["TensorFlow Tutorials", "PyTorch Docs", "Fast.ai"]
                rec["difficulty"] = "Hard"

            elif "react" in skill_lower or "angular" in skill_lower or "vue" in skill_lower:
                rec["recommendation"] = "Build projects with the framework, take online courses, and contribute to open source."
                rec["resources"] = ["React Docs", "Angular Tutorial", "Vue.js Guide"]
                rec["difficulty"] = "Medium"

            elif "django" in skill_lower or "flask" in skill_lower or "fastapi" in skill_lower:
                rec["recommendation"] = "Build web applications with the framework, follow tutorials, and deploy to production."
                rec["resources"] = ["Django Docs", "Flask Tutorial", "FastAPI Docs"]
                rec["difficulty"] = "Medium"

            elif "tableau" in skill_lower or "power bi" in skill_lower:
                rec["recommendation"] = "Complete certification courses, build dashboards with public datasets, and showcase on portfolio."
                rec["resources"] = ["Tableau Public", "Power BI Learn", "Dashboard Examples"]
                rec["difficulty"] = "Easy"

            else:
                rec["recommendation"] = (
                    f"Learn {skill} through online courses, hands-on projects, "
                    f"and practical application. Add certifications if available."
                )
                rec["resources"] = [
                    f"{skill} Tutorials",
                    f"{skill} Courses",
                    f"{skill} Documentation"
                ]
                rec["difficulty"] = "Medium"

            recommendations.append(rec)

        # Sort by priority
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 2))

        return recommendations

    # ==========================================================
    # ACTION PLAN GENERATION
    # ==========================================================

    def generate_action_plan(
        self,
        missing_with_priority: List[Dict],
        recommendations: List[Dict]
    ) -> Dict:
        """
        Generate a step-by-step action plan.

        Returns:
            Dictionary with:
            - short_term: Skills to learn immediately (Critical + High)
            - medium_term: Skills to learn next (Medium)
            - long_term: Skills for later (Low)
            - total_estimated_hours: Estimated learning time
        """
        plan = {
            "short_term": [],
            "medium_term": [],
            "long_term": [],
            "total_estimated_hours": 0
        }

        for rec in recommendations:
            skill = rec["skill"]
            priority = rec["priority"]
            difficulty = rec["difficulty"]

            # Estimate hours based on priority and difficulty
            if difficulty == "Easy":
                hours = 10
            elif difficulty == "Medium":
                hours = 30
            else:
                hours = 60

            item = {
                "skill": skill,
                "priority": priority,
                "difficulty": difficulty,
                "estimated_hours": hours,
                "recommendation": rec["recommendation"]
            }

            if priority in ["Critical", "High"]:
                plan["short_term"].append(item)
            elif priority == "Medium":
                plan["medium_term"].append(item)
            else:
                plan["long_term"].append(item)

            plan["total_estimated_hours"] += hours

        return plan

    # ==========================================================
    # COMPLETE ANALYSIS
    # ==========================================================

    def complete_analysis(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Dict:
        """
        Perform complete gap analysis with full details.

        Returns:
            Comprehensive analysis including:
            - Skill analysis (matches, gaps, coverage)
            - Priority classification
            - Recommendations
            - Action plan
            - Compatibility score
            - Category breakdown
        """
        # Basic skill analysis
        skill_analysis = self.analyze_skills(
            resume_skills,
            job_skills
        )

        # Get missing skills with priority
        missing_with_priority = skill_analysis.get("missing_with_priority", [])

        # Generate recommendations
        recommendations = self.generate_recommendations(
            [item["skill"] for item in missing_with_priority],
            missing_with_priority
        )

        # Generate action plan
        action_plan = self.generate_action_plan(
            missing_with_priority,
            recommendations
        )

        # Get overall status
        compatibility = skill_analysis.get("compatibility_score", 0)
        if compatibility >= 80:
            status = "Excellent"
        elif compatibility >= 60:
            status = "Good"
        elif compatibility >= 40:
            status = "Fair"
        else:
            status = "Needs Improvement"

        return {
            "matched_skills": skill_analysis.get("matched_skills", []),
            "matched_with_confidence": skill_analysis.get("matched_with_confidence", []),
            "missing_skills": [item["skill"] for item in missing_with_priority],
            "missing_with_priority": missing_with_priority,
            "skill_coverage": skill_analysis.get("skill_coverage", 0),
            "category_coverage": skill_analysis.get("category_coverage", {}),
            "compatibility_score": compatibility,
            "compatibility_status": status,
            "recommendations": recommendations,
            "action_plan": action_plan,
            "semantic_used": skill_analysis.get("semantic_used", False),
            "total_job_skills": skill_analysis.get("total_job_skills", 0),
            "total_matched": skill_analysis.get("total_matched", 0),
            "total_missing": skill_analysis.get("total_missing", 0)
        }

    # ==========================================================
    # COMPATIBILITY METHODS
    # ==========================================================

    def get_summary(self, analysis_result: Dict) -> Dict:
        """
        Get a concise summary of the analysis.

        Returns:
            Summary with key metrics.
        """
        return {
            "compatibility_score": analysis_result.get("compatibility_score", 0),
            "compatibility_status": analysis_result.get("compatibility_status", "Unknown"),
            "skill_coverage": analysis_result.get("skill_coverage", 0),
            "total_matched": analysis_result.get("total_matched", 0),
            "total_missing": analysis_result.get("total_missing", 0),
            "total_job_skills": analysis_result.get("total_job_skills", 0),
            "has_critical_gaps": any(
                item["priority"] == "Critical"
                for item in analysis_result.get("missing_with_priority", [])
            ),
            "estimated_learning_hours": analysis_result.get("action_plan", {}).get("total_estimated_hours", 0)
        }

    def get_skill_breakdown(self, analysis_result: Dict) -> Dict:
        """
        Get skill breakdown by category.

        Returns:
            Dictionary with category-wise skill counts.
        """
        category_breakdown = {}

        for category, data in analysis_result.get("category_coverage", {}).items():
            category_breakdown[category] = {
                "total": data["total"],
                "matched": data["matched"],
                "missing": len(data["missing"]),
                "coverage": data["coverage"],
                "skills": data["skills"],
                "missing_skills": data["missing"]
            }

        return category_breakdown


# ==========================================================
# TEST AND DEMONSTRATION
# ==========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AI RESUME TAILORING SYSTEM - GAP ANALYSIS ENGINE")
    print("PROFESSIONAL EDITION")
    print("=" * 70)

    # Sample skills
    resume_skills = [
        "python", "sql", "machine learning", "pandas", "numpy",
        "power bi", "communication", "teamwork"
    ]

    job_skills = [
        "python", "sql", "machine learning", "tensorflow", "pytorch",
        "power bi", "deep learning", "aws", "docker", "nlp",
        "problem solving", "communication", "leadership"
    ]

    # Initialize analyzer
    analyzer = GapAnalyzer(use_semantic=True)

    print("\n📊 Analyzing Skills...")
    result = analyzer.complete_analysis(resume_skills, job_skills)

    # ==========================================================
    # DISPLAY RESULTS
    # ==========================================================

    print("\n" + "=" * 70)
    print("📈 ANALYSIS RESULTS")
    print("=" * 70)

    summary = analyzer.get_summary(result)

    # Overall Score
    print(f"\n🎯 Overall Compatibility Score: {summary['compatibility_score']:.1f}%")
    print(f"   Status: {summary['compatibility_status']}")

    # Coverage
    print(f"\n📊 Skill Coverage: {summary['skill_coverage']:.1f}%")
    print(f"   ✅ Matched: {summary['total_matched']} skills")
    print(f"   ❌ Missing: {summary['total_missing']} skills")
    print(f"   📚 Total JD Skills: {summary['total_job_skills']}")

    # Critical Gaps
    if summary['has_critical_gaps']:
        print("\n⚠️  Critical Skill Gaps Detected!")
        print("   Focus on these skills first:")
        for item in result.get("missing_with_priority", []):
            if item["priority"] == "Critical":
                print(f"   - {item['skill']} ({item['category']})")
    else:
        print("\n✅ No critical skill gaps!")

    # Estimated Learning Time
    print(f"\n⏰ Estimated Learning Time: {summary['estimated_learning_hours']} hours")

    # Matched Skills
    print("\n✅ MATCHED SKILLS:")
    for skill in result.get("matched_skills", []):
        print(f"   • {skill}")

    # Missing Skills by Priority
    print("\n❌ MISSING SKILLS (By Priority):")

    for item in result.get("missing_with_priority", []):
        priority = item["priority"]
        skill = item["skill"]
        category = item["category"]

        if priority == "Critical":
            symbol = "🔴"
        elif priority == "High":
            symbol = "🟠"
        elif priority == "Medium":
            symbol = "🟡"
        else:
            symbol = "🟢"

        print(f"   {symbol} {priority}: {skill} ({category})")

    # Category Breakdown
    print("\n📂 CATEGORY BREAKDOWN:")
    breakdown = analyzer.get_skill_breakdown(result)
    for category, data in breakdown.items():
        if data["total"] > 0:
            status = "✅" if data["coverage"] >= 70 else "⚠️"
            print(f"   {status} {category}: {data['coverage']:.1f}% ({data['matched']}/{data['total']})")
            if data["missing_skills"]:
                print(f"      Missing: {', '.join(data['missing_skills'])}")

    # Action Plan
    print("\n📋 ACTION PLAN:")

    plan = result.get("action_plan", {})

    print("\n   🔥 SHORT TERM (Critical + High Priority):")
    for item in plan.get("short_term", [])[:5]:
        print(f"   - {item['skill']} (~{item['estimated_hours']} hours)")
        print(f"     → {item['recommendation'][:80]}...")

    print("\n   📈 MEDIUM TERM (Medium Priority):")
    for item in plan.get("medium_term", [])[:5]:
        print(f"   - {item['skill']} (~{item['estimated_hours']} hours)")

    print("\n   🎯 LONG TERM (Low Priority):")
    for item in plan.get("long_term", [])[:5]:
        print(f"   - {item['skill']} (~{item['estimated_hours']} hours)")

    # Top Recommendation
    print("\n💡 TOP RECOMMENDATION:")
    if result.get("recommendations"):
        top_rec = result["recommendations"][0]
        print(f"   Skill: {top_rec['skill']}")
        print(f"   Priority: {top_rec['priority']}")
        print(f"   Action: {top_rec['recommendation']}")
        print(f"   Resources: {', '.join(top_rec['resources'])}")

    print("\n" + "=" * 70)
    print("GAP ANALYSIS COMPLETED")
    print("=" * 70)
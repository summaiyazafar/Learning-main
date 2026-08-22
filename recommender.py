"""
DIGIBOOST INSTITUTE OF TECHNOLOGY
AI-Powered Course Recommendation Engine

Recommendation factors:
1. Qualification
2. Interests
3. Skills
4. Career Goal
5. Experience

Weighted scoring system:
Qualification = 25%
Interests     = 30%
Skills        = 20%
Career Goal   = 20%
Experience    = 5%

Total = 100 points
"""

from courses import courses


# =========================================================
# QUALIFICATION NORMALIZATION
# =========================================================

def normalize_qualification(qualification):
    """
    Converts different qualification formats
    into one standard format.
    """

    if not qualification:
        return ""

    q = str(qualification).strip().upper()

    qualification_map = {

        # FSC
        "FSC": "FSC",
        "F.SC": "FSC",
        "F.SC.": "FSC",
        "FCS": "FSC",

        # ICS
        "ICS": "ICS",
        "I.C.S": "ICS",
        "I.C.S.": "ICS",

        # FA
        "FA": "FA",
        "F.A": "FA",
        "F.A.": "FA",

        # BA
        "BA": "BA",
        "B.A": "BA",
        "B.A.": "BA",

        # BBA
        "BBA": "BBA",
        "B.B.A": "BBA",
        "B.B.A.": "BBA",

        # BS
        "BS": "BS",

        # BS Computer Science
        "BSCS": "BS_CS",
        "BS CS": "BS_CS",
        "BS-CS": "BS_CS",
        "BS COMPUTER SCIENCE": "BS_CS",

        # BS Information Technology
        "BSIT": "BS_IT",
        "BS IT": "BS_IT",
        "BS-IT": "BS_IT",
        "BS INFORMATION TECHNOLOGY": "BS_IT",

        # BS Artificial Intelligence
        "BSAI": "BS_AI",
        "BS AI": "BS_AI",
        "BS-AI": "BS_AI",
        "BS ARTIFICIAL INTELLIGENCE": "BS_AI",
    }

    return qualification_map.get(q, q)


# =========================================================
# LIST / TEXT NORMALIZATION
# =========================================================

def normalize_list(items):
    """
    Converts input into a clean lowercase list.

    Examples:

    "Python, AI, Data"
    ->
    ["python", "ai", "data"]

    ["Python", "AI"]
    ->
    ["python", "ai"]
    """

    if not items:
        return []

    if isinstance(items, str):
        items = items.split(",")

    return [
        str(item).strip().lower()
        for item in items
        if str(item).strip()
    ]


# =========================================================
# TEXT MATCHING HELPER
# =========================================================

def text_matches(user_text, course_text):
    """
    Checks whether two pieces of text are related.

    Exact matching:
        python == python

    Partial matching:
        python == python programming

    Reverse partial matching:
        data science == data
    """

    if not user_text or not course_text:
        return False

    user_text = str(user_text).strip().lower()
    course_text = str(course_text).strip().lower()

    return (
        user_text == course_text
        or user_text in course_text
        or course_text in user_text
    )


# =========================================================
# MATCH SCORE CALCULATION
# =========================================================

def calculate_match_score(
    course,
    qualification,
    interests,
    skills,
    career_goal,
    experience
):
    """
    Calculates the match score for one course.

    Maximum = 100 points.

    Qualification = 25 points
    Interests     = 30 points
    Skills        = 20 points
    Career Goal   = 20 points
    Experience    = 5 points

    Returns:
        score, reasons
    """

    score = 0
    reasons = []


    # =====================================================
    # 1. QUALIFICATION MATCH - 25 POINTS
    # =====================================================

    ideal_for = normalize_list(
        course.get("ideal_for", [])
    )

    qualification_match = False

    for ideal_qualification in ideal_for:

        normalized_ideal = normalize_qualification(
            ideal_qualification
        )

        if (
            qualification == normalized_ideal
            or normalized_ideal == "ALL"
        ):
            qualification_match = True
            break


    if qualification_match:

        score += 25

        reasons.append(
            "Your qualification is suitable for this course."
        )


    # =====================================================
    # 2. INTEREST MATCH - 30 POINTS
    # =====================================================

    course_tags = normalize_list(
        course.get("tags", [])
    )

    interest_matches = []


    for interest in interests:

        for tag in course_tags:

            if text_matches(
                interest,
                tag
            ):

                interest_matches.append(tag)

                break


    # Remove duplicates
    interest_matches = list(
        set(interest_matches)
    )


    if interest_matches:

        # Maximum 30 points
        interest_score = min(
            30,
            len(interest_matches) * 10
        )

        score += interest_score

        reasons.append(
            "Your interests match this course."
        )


    # =====================================================
    # 3. SKILLS MATCH - 20 POINTS
    # =====================================================

    course_skills = normalize_list(
        course.get("skills", [])
    )

    skill_matches = []


    for skill in skills:

        for course_skill in course_skills:

            if text_matches(
                skill,
                course_skill
            ):

                skill_matches.append(
                    course_skill
                )

                break


    # Remove duplicates
    skill_matches = list(
        set(skill_matches)
    )


    if skill_matches:

        skill_score = min(
            20,
            len(skill_matches) * 5
        )

        score += skill_score

        reasons.append(
            "Your skills are relevant to this course."
        )


    # =====================================================
    # 4. CAREER GOAL MATCH - 20 POINTS
    # =====================================================

    career_goals = normalize_list(
        course.get("career_goals", [])
    )

    career_match = False


    if career_goal:

        for goal in career_goals:

            if text_matches(
                career_goal,
                goal
            ):

                career_match = True

                break


    if career_match:

        score += 20

        reasons.append(
            "This course matches your career goal."
        )


    # =====================================================
    # 5. EXPERIENCE MATCH - 5 POINTS
    # =====================================================

    level = str(
        course.get("level", "")
    ).strip().lower()

    experience = str(
        experience or ""
    ).strip().lower()


    if experience:

        # Beginner
        if experience in [
            "beginner",
            "no experience",
            "none"
        ]:

            if level == "beginner":

                score += 5

                reasons.append(
                    "This course is suitable "
                    "for your beginner level."
                )


        # Intermediate
        elif experience in [
            "intermediate",
            "some experience"
        ]:

            if level in [
                "beginner",
                "intermediate"
            ]:

                score += 5

                reasons.append(
                    "This course suits your "
                    "current experience level."
                )


        # Advanced
        elif experience in [
            "advanced",
            "experienced"
        ]:

            if level in [
                "advanced",
                "intermediate"
            ]:

                score += 5

                reasons.append(
                    "This course matches "
                    "your experience level."
                )


    # =====================================================
    # FINAL SCORE
    # =====================================================

    score = min(
        100,
        score
    )


    return score, reasons


# =========================================================
# MATCH TYPE
# =========================================================

def get_match_type(score):
    """
    Converts numeric score into
    human-readable match category.
    """

    if score >= 80:

        return "🌟 EXCELLENT MATCH"

    elif score >= 60:

        return "⭐ STRONG MATCH"

    elif score >= 40:

        return "✅ GOOD MATCH"

    elif score >= 20:

        return "💡 POSSIBLE MATCH"

    else:

        return "📚 LOW MATCH"


# =========================================================
# MAIN RECOMMENDER
# =========================================================

def recommend_courses(
    qualification,
    interests,
    skills=None,
    career_goal="",
    experience=""
):
    """
    Generates ranked course recommendations.

    Parameters
    ----------
    qualification : str
        Example:
        FSC
        ICS
        BS_CS
        BS_IT

    interests : list
        Example:
        ["python", "ai", "data"]

    skills : list
        Example:
        ["python", "excel", "sql"]

    career_goal : str
        Example:
        "Data Analyst"

    experience : str
        Example:
        "Beginner"

    Returns
    -------
    list
        Top 5 ranked courses.
    """


    # =====================================================
    # CLEAN INPUT
    # =====================================================

    qualification = normalize_qualification(
        qualification
    )

    interests = normalize_list(
        interests
    )

    skills = normalize_list(
        skills
    )

    career_goal = str(
        career_goal or ""
    ).strip().lower()

    experience = str(
        experience or ""
    ).strip().lower()


    # =====================================================
    # DISPLAY PROFILE IN TERMINAL
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "🔍 ANALYZING STUDENT PROFILE"
    )

    print("=" * 60)

    print(
        f"📚 Qualification : {qualification}"
    )

    print(
        f"💡 Interests     : {interests}"
    )

    print(
        f"🛠️ Skills        : {skills}"
    )

    print(
        f"🎯 Career Goal   : {career_goal}"
    )

    print(
        f"📈 Experience    : {experience}"
    )


    # =====================================================
    # CHECK COURSE DATABASE
    # =====================================================

    if not isinstance(
        courses,
        dict
    ):

        raise TypeError(
            "The 'courses' variable in courses.py "
            "must be a dictionary."
        )


    # =====================================================
    # CALCULATE EVERY COURSE
    # =====================================================

    recommendations = []


    for course_name, course_data in courses.items():

        # Safety check
        if not isinstance(
            course_data,
            dict
        ):
            continue


        # Calculate score
        score, reasons = calculate_match_score(

            course=course_data,

            qualification=qualification,

            interests=interests,

            skills=skills,

            career_goal=career_goal,

            experience=experience
        )


        # Get match category
        match_type = get_match_type(
            score
        )


        # =================================================
        # CREATE RECOMMENDATION
        # =================================================

        recommendation = {

            "course": course_name,

            "category": course_data.get(
                "category",
                "General"
            ),

            "description": course_data.get(
                "description",
                "No description available."
            ),

            "match_score": score,

            "match_percentage": f"{score}%",

            "match_type": match_type,

            "reasons": reasons,

            "level": course_data.get(
                "level",
                "Not specified"
            )
        }


        recommendations.append(
            recommendation
        )


    # =====================================================
    # SORT BY SCORE
    # =====================================================

    recommendations.sort(

        key=lambda item:
            item["match_score"],

        reverse=True
    )


    # =====================================================
    # TOP 5
    # =====================================================

    recommendations = recommendations[:5]


    # =====================================================
    # DISPLAY RESULTS
    # =====================================================

    print("\n" + "=" * 60)

    print(
        "🎯 TOP COURSE RECOMMENDATIONS"
    )

    print("=" * 60)


    if not recommendations:

        print(
            "❌ No courses available."
        )


    else:

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):

            print(

                f"{index}. "
                f"{recommendation['course']} "
                f"→ "
                f"{recommendation['match_percentage']} "
                f"| "
                f"{recommendation['match_type']}"
            )


    print("=" * 60 + "\n")


    # =====================================================
    # RETURN RESULTS
    # =====================================================

    return recommendations
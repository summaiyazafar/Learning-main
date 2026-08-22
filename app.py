"""
DIGIBOOST INSTITUTE OF TECHNOLOGY
AI-Powered Course Recommendation System
Flask Web Application
"""

from flask import Flask, render_template, request, jsonify
from recommender import recommend_courses


app = Flask(__name__)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def index():

    recommendations = None
    user_data = None
    error = None

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        name = request.form.get("name", "").strip()

        age = request.form.get("age", "").strip()

        qualification = request.form.get(
            "qualification",
            ""
        ).strip().upper()

        interests_input = request.form.get(
            "interests",
            ""
        ).strip()

        skills_input = request.form.get(
            "skills",
            ""
        ).strip()

        career_goal = request.form.get(
            "career_goal",
            ""
        ).strip()

        experience = request.form.get(
            "experience",
            ""
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name:
            error = "Please enter your name."

        elif not age:
            error = "Please enter your age."

        elif not qualification:
            error = "Please select your qualification."

        elif not interests_input:
            error = "Please enter at least one interest."

        else:

            # -------------------------------------------------
            # CONVERT INTERESTS TO LIST
            # -------------------------------------------------

            interests = [
                interest.strip().lower()
                for interest in interests_input.split(",")
                if interest.strip()
            ]


            # -------------------------------------------------
            # CONVERT SKILLS TO LIST
            # -------------------------------------------------

            skills = [
                skill.strip().lower()
                for skill in skills_input.split(",")
                if skill.strip()
            ]


            # -------------------------------------------------
            # USER DATA
            # -------------------------------------------------

            user_data = {
                "name": name,
                "age": age,
                "qualification": qualification,
                "interests": interests,
                "skills": skills,
                "career_goal": career_goal,
                "experience": experience
            }


            # -------------------------------------------------
            # RECOMMEND COURSES
            # -------------------------------------------------

            try:

                recommendations = recommend_courses(
                    qualification=qualification,
                    interests=interests,
                    skills=skills,
                    career_goal=career_goal,
                    experience=experience
                )

            except Exception as e:

                print("\n❌ Recommendation Error:")
                print(e)

                recommendations = []

                error = (
                    "Unable to generate recommendations. "
                    "Please check your input."
                )


    return render_template(
        "index.html",
        user=user_data,
        recommendations=recommendations,
        error=error
    )


# =========================================================
# API
# =========================================================

@app.route("/api/recommend", methods=["POST"])
def api_recommend():

    data = request.get_json(silent=True) or {}

    qualification = str(
        data.get("qualification", "")
    ).strip().upper()

    interests = data.get("interests", [])

    skills = data.get("skills", [])

    career_goal = str(
        data.get("career_goal", "")
    ).strip()

    experience = str(
        data.get("experience", "")
    ).strip()


    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------

    if not qualification:

        return jsonify({
            "success": False,
            "error": "Qualification is required."
        }), 400


    if not isinstance(interests, list):

        return jsonify({
            "success": False,
            "error": "Interests must be a list."
        }), 400


    interests = [
        str(interest).strip().lower()
        for interest in interests
        if str(interest).strip()
    ]


    if not interests:

        return jsonify({
            "success": False,
            "error": "At least one interest is required."
        }), 400


    if not isinstance(skills, list):
        skills = []


    skills = [
        str(skill).strip().lower()
        for skill in skills
        if str(skill).strip()
    ]


    # -------------------------------------------------
    # RECOMMEND
    # -------------------------------------------------

    try:

        recommendations = recommend_courses(
            qualification=qualification,
            interests=interests,
            skills=skills,
            career_goal=career_goal,
            experience=experience
        )

    except Exception as e:

        print("\n❌ API Recommendation Error:")
        print(e)

        return jsonify({
            "success": False,
            "error": "Unable to generate recommendations."
        }), 500


    return jsonify({

        "success": True,

        "qualification": qualification,

        "interests": interests,

        "skills": skills,

        "career_goal": career_goal,

        "experience": experience,

        "recommendations": recommendations

    })


# =========================================================
# 404
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({
        "success": False,
        "error": "Page not found."
    }), 404


# =========================================================
# 500
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("🎓 DIGIBOOST INSTITUTE OF TECHNOLOGY")
    print("🤖 AI-Powered Course Recommendation System")
    print("=" * 60)
    print()
    print("🚀 Starting Flask server...")
    print("🌐 Open: http://127.0.0.1:5000")
    print("📋 Press CTRL+C to stop")
    print()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
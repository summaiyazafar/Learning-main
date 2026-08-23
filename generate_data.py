"""
DIGIBOOST INSTITUTE OF TECHNOLOGY
ML Course Recommendation System
Training Data Generator

Generates realistic synthetic student profiles
without collecting names or personal identifiers.

Age: 18-40
Experience: Beginner / Intermediate / Advanced

Target:
    recommended_course
"""

import pandas as pd
import random
import os


# =========================================================
# RANDOM SEED
# =========================================================

random.seed(42)


# =========================================================
# QUALIFICATIONS
# =========================================================

INTERMEDIATE_QUALIFICATIONS = [
    "FSC Pre-Medical",
    "FSC Pre-Engineering",
    "ICS",
    "I.Com",
    "FA",
    "General Intermediate",
    "DAE",
    "A-Level"
]

GRADUATION_QUALIFICATIONS = [
    "BS Computer Science",
    "BS Information Technology",
    "BS Artificial Intelligence",
    "BS Software Engineering",
    "BS Data Science",
    "BS Cyber Security",
    "BS Mathematics",
    "BS Physics",
    "BS English",
    "BS Business Administration",
    "BBA",
    "BA",
    "B.Com",
    "BS Any Subject"
]

ALL_QUALIFICATIONS = (
    INTERMEDIATE_QUALIFICATIONS
    + GRADUATION_QUALIFICATIONS
)


# =========================================================
# EXPERIENCE
# =========================================================

EXPERIENCE_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced"
]


# =========================================================
# PROFILE OPTIONS
# =========================================================

INTERESTS = [
    "Developer",
    "Coder",
    "Programming",
    "Software",
    "AI",
    "Machine Learning",
    "Data",
    "Data Analysis",
    "Data Science",
    "Deep Learning",
    "LLM",
    "Generative AI",
    "Robotics",
    "Cyber Security",
    "Web Development",
    "Mobile Apps",
    "Game Development",

    "Business",
    "Entrepreneurship",
    "Management",
    "Sales",
    "Finance",
    "HR",
    "Marketing",

    "Digital Marketing",
    "SEO",
    "E-Commerce",
    "Social Media",

    "Graphic Design",
    "UI UX",
    "Video Editing",
    "Content Creation",

    "Freelancing",
    "Administration",
    "Cloud Computing",
    "DevOps",
    "Networking"
]


SKILLS = [
    "Python",
    "JavaScript",
    "Java",
    "C++",
    "C#",
    "PHP",
    "Swift",
    "Kotlin",

    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue.js",
    "Node.js",
    "Django",
    "Flask",

    "SQL",
    "MongoDB",
    "PostgreSQL",

    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Computer Vision",

    "AWS",
    "Azure",
    "GCP",
    "Docker",
    "Linux",

    "Git",
    "GitHub",

    "Excel",
    "PowerPoint",
    "Word",

    "Photoshop",
    "Illustrator",
    "Figma",
    "Premiere Pro",
    "After Effects",

    "SEO",
    "Google Ads",
    "Facebook Ads",
    "Instagram",
    "TikTok",
    "LinkedIn",

    "Shopify",
    "WooCommerce",
    "WordPress",

    "Communication",
    "Leadership",
    "Problem Solving",
    "Teamwork",
    "Creativity",
    "Project Management",
    "Time Management",
    "Analytical Thinking"
]


# =========================================================
# CAREER GOALS
# =========================================================

CAREER_GOALS = [
    "Software Developer",
    "Web Developer",
    "Mobile App Developer",
    "AI Engineer",
    "ML Engineer",
    "Data Analyst",
    "Data Scientist",
    "Cyber Security Engineer",
    "DevOps Engineer",
    "Cloud Engineer",

    "Business Owner",
    "Entrepreneur",
    "Business Manager",

    "Sales Manager",
    "Finance Manager",
    "HR Manager",
    "Marketing Manager",

    "Digital Marketer",
    "SEO Specialist",
    "Social Media Manager",

    "Graphic Designer",
    "UI/UX Designer",
    "Video Editor",

    "Content Creator",
    "Freelancer",
    "E-Commerce Specialist",

    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer"
]


# =========================================================
# COURSE DATABASE
# =========================================================

COURSES = {

    # =====================================================
    # DATA & AI
    # =====================================================

    "Python": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "developer",
            "coder",
            "programming",
            "software",
            "python",
            "problem solving"
        ]
    },

    "Data Analytics": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "data",
            "data analysis",
            "data science",
            "excel",
            "finance",
            "analytical thinking"
        ]
    },

    "Machine Learning": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "machine learning",
            "ai",
            "data science",
            "python",
            "ml engineer",
            "data scientist"
        ]
    },

    "Deep Learning": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Advanced"],
        "keywords": [
            "deep learning",
            "ai",
            "machine learning",
            "data science"
        ]
    },

    "Advanced Artificial Intelligence": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Advanced"],
        "keywords": [
            "ai",
            "artificial intelligence",
            "machine learning",
            "ai engineer"
        ]
    },

    "AI Automation": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "ai",
            "automation",
            "business",
            "entrepreneurship",
            "technology"
        ]
    },

    "Generative AI": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "generative ai",
            "ai",
            "llm",
            "content creation",
            "chatgpt"
        ]
    },

    "Large Language Model (LLM)": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Advanced"],
        "keywords": [
            "llm",
            "ai",
            "deep learning",
            "nlp",
            "machine learning"
        ]
    },

    "Agentic AI": {
        "category": "Data & Artificial Intelligence",
        "levels": ["Advanced"],
        "keywords": [
            "ai",
            "agents",
            "automation",
            "python",
            "llm"
        ]
    },


    # =====================================================
    # DEVELOPMENT
    # =====================================================

    "Mobile Application Development": {
        "category": "Development & Programming",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "mobile",
            "mobile apps",
            "android",
            "ios",
            "developer",
            "kotlin",
            "swift"
        ]
    },

    "Web Application Development": {
        "category": "Development & Programming",
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "keywords": [
            "web",
            "web development",
            "developer",
            "programming",
            "javascript",
            "html",
            "css"
        ]
    },

    "Front-end Development": {
        "category": "Development & Programming",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "frontend",
            "web",
            "developer",
            "html",
            "css",
            "javascript",
            "ui"
        ]
    },

    "Back-end Development": {
        "category": "Development & Programming",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "backend",
            "developer",
            "python",
            "node",
            "database",
            "sql"
        ]
    },

    "Game Programming": {
        "category": "Development & Programming",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "game",
            "game development",
            "programming",
            "developer",
            "c#"
        ]
    },

    "Server Administration": {
        "category": "Development & Programming",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "server",
            "linux",
            "networking",
            "cloud",
            "devops"
        ]
    },


    # =====================================================
    # PROFESSIONAL SKILLS
    # =====================================================

    "Sales Administration": {
        "category": "Professional Skills",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "sales",
            "business",
            "communication",
            "administration"
        ]
    },

    "Finance Administration": {
        "category": "Professional Skills",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "finance",
            "accounting",
            "business",
            "excel"
        ]
    },

    "HR Administration": {
        "category": "Professional Skills",
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "keywords": [
            "hr",
            "human resources",
            "management",
            "communication"
        ]
    },

    "Marketing Administration": {
        "category": "Professional Skills",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "marketing",
            "business",
            "administration"
        ]
    },

    "Operational Administration": {
        "category": "Professional Skills",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "operations",
            "management",
            "business",
            "administration"
        ]
    },

    "Sales Manager": {
        "category": "Professional Skills",
        "levels": ["Advanced"],
        "keywords": [
            "sales",
            "business",
            "management",
            "leadership"
        ]
    },

    "Finance Manager": {
        "category": "Professional Skills",
        "levels": ["Advanced"],
        "keywords": [
            "finance",
            "business",
            "management",
            "leadership"
        ]
    },

    "HR Manager": {
        "category": "Professional Skills",
        "levels": ["Advanced"],
        "keywords": [
            "hr",
            "management",
            "leadership"
        ]
    },

    "Marketing Manager": {
        "category": "Professional Skills",
        "levels": ["Advanced"],
        "keywords": [
            "marketing",
            "business",
            "management",
            "leadership"
        ]
    },

    "IT Administrator": {
        "category": "Professional Skills",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "it",
            "networking",
            "linux",
            "administration"
        ]
    },

    "IT Manager": {
        "category": "Professional Skills",
        "levels": ["Advanced"],
        "keywords": [
            "it",
            "management",
            "leadership",
            "technology"
        ]
    },


    # =====================================================
    # DIGITAL MARKETING
    # =====================================================

    "Digital Marketing": {
        "category": "Digital Marketing",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "digital marketing",
            "marketing",
            "business",
            "entrepreneurship"
        ]
    },

    "Social Media Marketing": {
        "category": "Digital Marketing",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "social media",
            "marketing",
            "instagram",
            "facebook",
            "tiktok"
        ]
    },

    "SEO": {
        "category": "Digital Marketing",
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "keywords": [
            "seo",
            "digital marketing",
            "marketing",
            "content"
        ]
    },

    "Content Marketing": {
        "category": "Digital Marketing",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "content",
            "marketing",
            "writing",
            "content creation"
        ]
    },

    "Email Marketing": {
        "category": "Digital Marketing",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "email",
            "marketing",
            "business"
        ]
    },

    "E-Commerce Marketing": {
        "category": "Digital Marketing",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "ecommerce",
            "business",
            "marketing",
            "online store"
        ]
    },

    "Affiliate Marketing": {
        "category": "Digital Marketing",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "affiliate",
            "marketing",
            "business",
            "online"
        ]
    },

    "TikTok Marketing": {
        "category": "Digital Marketing",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "tiktok",
            "social media",
            "marketing",
            "video"
        ]
    },

    "Meta Ads": {
        "category": "Digital Marketing",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "meta ads",
            "facebook",
            "instagram",
            "marketing"
        ]
    },

    "Google Ads": {
        "category": "Digital Marketing",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "google ads",
            "marketing",
            "advertising"
        ]
    },

    "Shopify Stores Creation & Branding": {
        "category": "Digital Marketing",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "shopify",
            "ecommerce",
            "business",
            "branding"
        ]
    },


    # =====================================================
    # FREELANCING
    # =====================================================

    "Freelancing & Personal Branding": {
        "category": "Freelancing & Personal Branding",
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "keywords": [
            "freelancing",
            "business",
            "entrepreneurship",
            "personal branding"
        ]
    },


    # =====================================================
    # DESIGN & CREATIVE
    # =====================================================

    "Graphic Designing": {
        "category": "Design, Media & Creative",
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "keywords": [
            "graphic design",
            "design",
            "creative",
            "photoshop",
            "illustrator"
        ]
    },

    "UX/UI/CX": {
        "category": "Design, Media & Creative",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "ui",
            "ux",
            "design",
            "figma",
            "creative"
        ]
    },

    "Video Creation & Editing": {
        "category": "Design, Media & Creative",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "video",
            "video editing",
            "creative",
            "premiere"
        ]
    },

    "Web Designing": {
        "category": "Design, Media & Creative",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "web design",
            "design",
            "html",
            "css",
            "ui"
        ]
    },

    "E-Commerce": {
        "category": "Design, Media & Creative",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "ecommerce",
            "shopify",
            "business",
            "online store"
        ]
    },

    "AI Video Creation": {
        "category": "Design, Media & Creative",
        "levels": ["Intermediate", "Advanced"],
        "keywords": [
            "ai",
            "video",
            "content",
            "generative ai"
        ]
    },

    "Content Creation": {
        "category": "Design, Media & Creative",
        "levels": ["Beginner", "Intermediate"],
        "keywords": [
            "content",
            "content creation",
            "video",
            "social media"
        ]
    },

    "AI Tools": {
        "category": "Design, Media & Creative",
        "levels": ["Beginner", "Intermediate", "Advanced"],
        "keywords": [
            "ai",
            "ai tools",
            "automation",
            "generative ai"
        ]
    }
}


# =========================================================
# COURSE KEYWORD GROUPS
# =========================================================

COURSE_GROUPS = {

    "AI": [
        "Machine Learning",
        "Deep Learning",
        "Advanced Artificial Intelligence",
        "Generative AI",
        "Large Language Model (LLM)",
        "Agentic AI",
        "AI Automation",
        "AI Tools"
    ],

    "PROGRAMMING": [
        "Python",
        "Web Application Development",
        "Front-end Development",
        "Back-end Development",
        "Mobile Application Development",
        "Game Programming"
    ],

    "DATA": [
        "Data Analytics",
        "Machine Learning",
        "Python"
    ],

    "BUSINESS": [
        "Digital Marketing",
        "E-Commerce Marketing",
        "Shopify Stores Creation & Branding",
        "Affiliate Marketing",
        "Freelancing & Personal Branding",
        "Marketing Administration",
        "Sales Administration"
    ],

    "MARKETING": [
        "Digital Marketing",
        "Social Media Marketing",
        "SEO",
        "Content Marketing",
        "Email Marketing",
        "Meta Ads",
        "Google Ads",
        "TikTok Marketing"
    ],

    "DESIGN": [
        "Graphic Designing",
        "UX/UI/CX",
        "Web Designing",
        "Video Creation & Editing",
        "AI Video Creation",
        "Content Creation"
    ],

    "FREELANCING": [
        "Freelancing & Personal Branding"
    ],

    "IT": [
        "IT Administrator",
        "IT Manager",
        "Server Administration"
    ]
}


# =========================================================
# QUALIFICATION → COURSE PREFERENCES
# =========================================================

QUALIFICATION_GROUPS = {

    "TECHNICAL": [
        "ICS",
        "FSC Pre-Engineering",
        "DAE",
        "BS Computer Science",
        "BS Information Technology",
        "BS Artificial Intelligence",
        "BS Software Engineering",
        "BS Data Science",
        "BS Cyber Security"
    ],

    "BUSINESS": [
        "I.Com",
        "B.Com",
        "BBA",
        "BA",
        "BS Business Administration"
    ],

    "GENERAL": [
        "FA",
        "General Intermediate",
        "A-Level",
        "BS English",
        "BS Any Subject"
    ],

    "SCIENCE": [
        "FSC Pre-Medical",
        "BS Mathematics",
        "BS Physics"
    ]
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def normalize(text):
    return str(text).lower().strip()


def contains_any(text, words):
    text = normalize(text)
    return any(normalize(word) in text for word in words)


# =========================================================
# RECOMMEND COURSE (FIXED)
# =========================================================

def get_recommended_course(
    qualification,
    interests,
    skills,
    career_goal,
    experience
):
    # ✅ FIX: Convert lists to strings
    interests_str = " ".join(interests) if interests else ""
    skills_str = " ".join(skills) if skills else ""

    profile_text = " ".join([
        qualification,
        interests_str,
        skills_str,
        career_goal
    ])

    profile_text = normalize(profile_text)

    scores = {}

    for course_name, course in COURSES.items():

        score = 0

        # -------------------------------------------------
        # 1. INTEREST MATCH - VERY IMPORTANT
        # -------------------------------------------------

        for keyword in course["keywords"]:

            if normalize(keyword) in profile_text:
                score += 15


        # -------------------------------------------------
        # 2. CAREER GOAL MATCH
        # -------------------------------------------------

        career = normalize(career_goal)

        if "business owner" in career or "entrepreneur" in career:

            if course_name in COURSE_GROUPS["BUSINESS"]:
                score += 50

        elif "software developer" in career:

            if course_name in COURSE_GROUPS["PROGRAMMING"]:
                score += 50

        elif "web developer" in career:

            if course_name in [
                "Web Application Development",
                "Front-end Development",
                "Back-end Development",
                "Web Designing"
            ]:
                score += 60

        elif "mobile app developer" in career:

            if course_name == "Mobile Application Development":
                score += 60

        elif "ai engineer" in career:

            if course_name in COURSE_GROUPS["AI"]:
                score += 60

        elif "ml engineer" in career:

            if course_name == "Machine Learning":
                score += 70

        elif "data analyst" in career:

            if course_name == "Data Analytics":
                score += 70

        elif "data scientist" in career:

            if course_name in [
                "Data Analytics",
                "Machine Learning",
                "Python"
            ]:
                score += 55

        elif "digital marketer" in career:

            if course_name in COURSE_GROUPS["MARKETING"]:
                score += 60

        elif "seo specialist" in career:

            if course_name == "SEO":
                score += 70

        elif "graphic designer" in career:

            if course_name == "Graphic Designing":
                score += 70

        elif "video editor" in career:

            if course_name == "Video Creation & Editing":
                score += 70

        elif "freelancer" in career:

            if course_name == "Freelancing & Personal Branding":
                score += 70

        elif "e-commerce specialist" in career:

            if course_name in [
                "E-Commerce",
                "E-Commerce Marketing",
                "Shopify Stores Creation & Branding"
            ]:
                score += 60


        # -------------------------------------------------
        # 3. EXPERIENCE MATCH
        # -------------------------------------------------

        if experience in course["levels"]:
            score += 15
        else:
            score -= 10


        # -------------------------------------------------
        # 4. QUALIFICATION MATCH
        # -------------------------------------------------

        if qualification in course.get("ideal_for", []):
            score += 20


        # -------------------------------------------------
        # 5. SPECIAL PROFILE LOGIC
        # -------------------------------------------------

        # Business profiles
        if contains_any(
            profile_text,
            [
                "business",
                "entrepreneur",
                "management",
                "sales",
                "marketing"
            ]
        ):
            if course_name in COURSE_GROUPS["BUSINESS"]:
                score += 20


        # AI profiles
        if contains_any(
            profile_text,
            [
                "artificial intelligence",
                "machine learning",
                "deep learning",
                "generative ai",
                "llm"
            ]
        ):
            if course_name in COURSE_GROUPS["AI"]:
                score += 25


        # Programming profiles
        if contains_any(
            profile_text,
            [
                "developer",
                "coder",
                "programming",
                "software"
            ]
        ):
            if course_name in COURSE_GROUPS["PROGRAMMING"]:
                score += 20


        # Design profiles
        if contains_any(
            profile_text,
            [
                "graphic",
                "design",
                "ui",
                "ux",
                "video"
            ]
        ):
            if course_name in COURSE_GROUPS["DESIGN"]:
                score += 25


        scores[course_name] = score


    # =====================================================
    # BEST COURSE
    # =====================================================

    sorted_courses = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_courses[0][0]


# =========================================================
# GENERATE ONE STUDENT
# =========================================================

def generate_student():

    age = random.randint(18, 40)

    qualification = random.choice(
        ALL_QUALIFICATIONS
    )

    experience = random.choice(
        EXPERIENCE_LEVELS
    )

    # -----------------------------------------------------
    # Create related profile
    # -----------------------------------------------------

    profile_type = random.choice([
        "AI",
        "PROGRAMMING",
        "DATA",
        "BUSINESS",
        "MARKETING",
        "DESIGN",
        "FREELANCING",
        "IT"
    ])

    # -----------------------------------------------------
    # Interests
    # -----------------------------------------------------

    interest_map = {

        "AI": [
            "AI",
            "Machine Learning",
            "Deep Learning",
            "Generative AI",
            "LLM"
        ],

        "PROGRAMMING": [
            "Developer",
            "Coder",
            "Programming",
            "Software",
            "Web Development",
            "Mobile Apps"
        ],

        "DATA": [
            "Data",
            "Data Analysis",
            "Data Science",
            "AI",
            "Machine Learning"
        ],

        "BUSINESS": [
            "Business",
            "Entrepreneurship",
            "Management",
            "E-Commerce",
            "Sales"
        ],

        "MARKETING": [
            "Marketing",
            "Digital Marketing",
            "SEO",
            "Social Media",
            "Content Creation"
        ],

        "DESIGN": [
            "Graphic Design",
            "UI UX",
            "Video Editing",
            "Content Creation"
        ],

        "FREELANCING": [
            "Freelancing",
            "Business",
            "Digital Marketing",
            "Personal Branding"
        ],

        "IT": [
            "Cloud Computing",
            "DevOps",
            "Networking",
            "Cyber Security"
        ]
    }

    interests = random.sample(
        interest_map[profile_type],
        k=min(
            3,
            len(interest_map[profile_type])
        )
    )


    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    skill_map = {

        "AI": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "Problem Solving",
            "Analytical Thinking"
        ],

        "PROGRAMMING": [
            "Python",
            "JavaScript",
            "HTML",
            "CSS",
            "Git",
            "Problem Solving"
        ],

        "DATA": [
            "Python",
            "SQL",
            "Excel",
            "Analytical Thinking",
            "Problem Solving"
        ],

        "BUSINESS": [
            "Communication",
            "Leadership",
            "Excel",
            "Project Management",
            "Creativity"
        ],

        "MARKETING": [
            "SEO",
            "Google Ads",
            "Instagram",
            "Communication",
            "Creativity"
        ],

        "DESIGN": [
            "Photoshop",
            "Illustrator",
            "Figma",
            "Creativity",
            "Premiere Pro"
        ],

        "FREELANCING": [
            "Communication",
            "Marketing",
            "LinkedIn",
            "Creativity",
            "Time Management"
        ],

        "IT": [
            "Linux",
            "AWS",
            "Docker",
            "Networking",
            "Git"
        ]
    }

    skills = random.sample(
        skill_map[profile_type],
        k=4
    )


    # -----------------------------------------------------
    # Career Goal
    # -----------------------------------------------------

    career_map = {

        "AI": [
            "AI Engineer",
            "ML Engineer",
            "Data Scientist"
        ],

        "PROGRAMMING": [
            "Software Developer",
            "Web Developer",
            "Full Stack Developer",
            "Backend Developer",
            "Frontend Developer",
            "Mobile App Developer"
        ],

        "DATA": [
            "Data Analyst",
            "Data Scientist"
        ],

        "BUSINESS": [
            "Business Owner",
            "Entrepreneur",
            "Business Manager",
            "E-Commerce Specialist"
        ],

        "MARKETING": [
            "Digital Marketer",
            "SEO Specialist",
            "Social Media Manager",
            "Marketing Manager"
        ],

        "DESIGN": [
            "Graphic Designer",
            "UI/UX Designer",
            "Video Editor",
            "Content Creator"
        ],

        "FREELANCING": [
            "Freelancer",
            "Business Owner"
        ],

        "IT": [
            "Cloud Engineer",
            "DevOps Engineer",
            "Cyber Security Engineer"
        ]
    }

    career_goal = random.choice(
        career_map[profile_type]
    )


    # -----------------------------------------------------
    # Recommended Course
    # -----------------------------------------------------

    recommended_course = get_recommended_course(
        qualification,
        interests,
        skills,
        career_goal,
        experience
    )


    return {
        "age": age,
        "qualification": qualification,
        "interests": ", ".join(interests),
        "skills": ", ".join(skills),
        "career_goal": career_goal,
        "experience": experience,
        "recommended_course": recommended_course,
        "course_category": COURSES[
            recommended_course
        ]["category"]
    }


# =========================================================
# GENERATE DATASET
# =========================================================

def generate_dataset(num_records=1000):

    print("=" * 65)
    print("DIGIBOOST INSTITUTE OF TECHNOLOGY")
    print("ML COURSE RECOMMENDATION - DATA GENERATOR")
    print("=" * 65)

    print()
    print(
        f"Generating {num_records} student profiles..."
    )

    data = []

    for _ in range(num_records):

        student = generate_student()

        data.append(student)


    df = pd.DataFrame(data)


    # -----------------------------------------------------
    # Add ID only for dataset tracking
    # -----------------------------------------------------

    df.insert(
        0,
        "student_id",
        range(1, len(df) + 1)
    )


    # -----------------------------------------------------
    # Save dataset
    # -----------------------------------------------------

    os.makedirs(
        "data",
        exist_ok=True
    )

    file_path = "data/student_data.csv"

    df.to_csv(
        file_path,
        index=False
    )


    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    print()
    print("DATASET CREATED SUCCESSFULLY")
    print("-" * 65)

    print(
        f"Total Students: {len(df)}"
    )

    print(
        f"Qualifications: {df['qualification'].nunique()}"
    )

    print(
        f"Courses: {df['recommended_course'].nunique()}"
    )

    print(
        f"Categories: {df['course_category'].nunique()}"
    )

    print(
        f"Experience Levels: "
        f"{df['experience'].unique().tolist()}"
    )

    print()
    print("COURSE DISTRIBUTION")
    print("-" * 65)

    print(
        df["recommended_course"]
        .value_counts()
        .to_string()
    )

    print()
    print("SAMPLE DATA")
    print("-" * 65)

    print(
        df[
            [
                "age",
                "qualification",
                "interests",
                "skills",
                "career_goal",
                "experience",
                "recommended_course"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print()
    print(
        f"CSV saved at: {file_path}"
    )

    print("=" * 65)

    return df


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    generate_dataset(1000)
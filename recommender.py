"""
DIGIBOOST INSTITUTE OF TECHNOLOGY
ML-Powered Course Recommendation Engine
Uses trained Random Forest model to recommend Top 5 courses
"""

import pandas as pd
import numpy as np
import joblib
import os
from courses import courses

# =========================================================
# LOAD ML MODEL
# =========================================================

def load_ml_artifacts():
    """Load all trained ML artifacts"""
    try:
        model = joblib.load('models/ml_recommender.pkl')
        scaler = joblib.load('models/scaler.pkl')
        le_qual = joblib.load('models/qual_encoder.pkl')
        le_target = joblib.load('models/target_encoder.pkl')
        mlb_interests = joblib.load('models/interests_mlb.pkl')
        mlb_skills = joblib.load('models/skills_mlb.pkl')
        feature_cols = joblib.load('models/feature_columns.pkl')
        career_keywords = joblib.load('models/career_keywords.pkl')
        interest_classes = joblib.load('models/interests_classes.pkl')
        skill_classes = joblib.load('models/skills_classes.pkl')
        
        print("✅ ML Model loaded successfully!")
        return model, scaler, le_qual, le_target, mlb_interests, mlb_skills, feature_cols, career_keywords, interest_classes, skill_classes
    except Exception as e:
        print(f"⚠️ Model not found: {e}")
        print("   Falling back to rule-based recommender...")
        return None, None, None, None, None, None, None, None, None, None

# Load artifacts
(model, scaler, le_qual, le_target, 
 mlb_interests, mlb_skills, feature_cols, 
 career_keywords, interest_classes, skill_classes) = load_ml_artifacts()


# =========================================================
# HELPERS
# =========================================================

def normalize_list(items):
    if not items: return []
    if isinstance(items, str): items = items.split(",")
    return [str(i).strip().lower() for i in items if str(i).strip()]

def get_match_type(score):
    if score >= 80: return "🌟 EXCELLENT MATCH"
    elif score >= 60: return "⭐ STRONG MATCH"
    elif score >= 40: return "✅ GOOD MATCH"
    elif score >= 20: return "💡 POSSIBLE MATCH"
    else: return "📚 LOW MATCH"

def get_reasons(course_name, interests, skills, career_goal):
    reasons = []
    course_data = courses.get(course_name, {})
    
    # Interest match
    course_tags = [t.lower() for t in course_data.get('tags', [])]
    for interest in interests[:3]:
        if interest in ' '.join(course_tags):
            reasons.append(f"💡 Aligns with your interest in '{interest}'")
            break
    
    # Skill match
    course_skills = [s.lower() for s in course_data.get('skills', [])]
    for skill in skills[:3]:
        if skill in ' '.join(course_skills):
            reasons.append(f"🛠️ Relevant to your skill '{skill}'")
            break
    
    # Career goal
    if career_goal:
        goals = [g.lower() for g in course_data.get('career_goals', [])]
        if any(career_goal in g or g in career_goal for g in goals):
            reasons.append(f"🎯 Matches your career goal '{career_goal}'")
    
    if not reasons:
        reasons.append("📚 Good overall fit for your profile")
    return reasons

# =========================================================
# FALLBACK (Rule-based)
# =========================================================

def fallback_recommend(qualification, interests, skills, career_goal, experience):
    # Simple fallback logic if ML fails
    from courses import courses
    scores = {}
    for name, data in courses.items():
        score = 0
        if qualification in [q.upper() for q in data.get('ideal_for', [])]:
            score += 30
        for tag in data.get('tags', []):
            if any(tag in i for i in [str(i).lower() for i in interests]):
                score += 20
                break
        scores[name] = score
    
    sorted_courses = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    results = []
    for name, score in sorted_courses:
        data = courses.get(name, {})
        results.append({
            'course': name,
            'category': data.get('category', 'General'),
            'description': data.get('description', ''),
            'match_score': score,
            'match_percentage': f"{score}%",
            'match_type': get_match_type(score),
            'reasons': ['✅ Based on your qualification and interests'],
            'level': data.get('level', '')
        })
    return results

# =========================================================
# MAIN RECOMMEND FUNCTION
# =========================================================

def recommend_courses(qualification, interests, skills=None, career_goal="", experience=""):
    """
    ML-powered recommendation - returns Top 5 courses
    """
    # If model not loaded, use fallback
    if model is None:
        return fallback_recommend(qualification, interests, skills, career_goal, experience)

    # Clean inputs
    qual_clean = qualification.strip().upper()
    interests = normalize_list(interests)
    skills = normalize_list(skills) if skills else []
    career_goal = str(career_goal or "").strip().lower()
    experience = str(experience or "").strip().lower()

    # ---- 1. Qualification ----
    qual_map = {
        'FSC': 'FSC', 'ICS': 'ICS', 'FA': 'FA', 'BA': 'BA',
        'BBA': 'BBA', 'BS': 'BS', 'BS_CS': 'BS_CS', 
        'BS_IT': 'BS_IT', 'BS_AI': 'BS_AI', 'BS_SE': 'BS_SE'
    }
    try:
        qual_enc = le_qual.transform([qual_map.get(qual_clean, 'General')])[0]
    except:
        qual_enc = 0

    # ---- 2. Experience ----
    exp_enc = {'beginner': 0, 'intermediate': 1, 'advanced': 2}.get(experience, 0)
    age = 22  # Default

    # ---- 3. Interests ----
    try:
        int_vec = mlb_interests.transform([interests])[0]
    except:
        int_vec = [0] * len(interest_classes)
    int_dict = {f'int_{col}': int_vec[i] for i, col in enumerate(interest_classes)}

    # ---- 4. Skills ----
    try:
        sk_vec = mlb_skills.transform([skills])[0]
    except:
        sk_vec = [0] * len(skill_classes)
    sk_dict = {f'skill_{col}': sk_vec[i] for i, col in enumerate(skill_classes)}

    # ---- 5. Career Keywords ----
    career_dict = {f'career_{kw}': 1 if kw in career_goal else 0 for kw in career_keywords}

    # ---- 6. Combine ----
    feature_dict = {
        'age': age,
        'qual_encoded': qual_enc,
        'exp_encoded': exp_enc,
        **int_dict,
        **sk_dict,
        **career_dict
    }

    feature_df = pd.DataFrame([feature_dict])
    for col in feature_cols:
        if col not in feature_df.columns:
            feature_df[col] = 0
    feature_df = feature_df[feature_cols]

    # ---- 7. Predict ----
    X_scaled = scaler.transform(feature_df)
    
    # Get probabilities for ALL courses
    probs = model.predict_proba(X_scaled)[0]
    
    # Get top 5 indices
    top_indices = np.argsort(probs)[::-1][:5]
    
    recommendations = []
    for idx in top_indices:
        course_name = le_target.inverse_transform([idx])[0]
        confidence = probs[idx] * 100
        data = courses.get(course_name, {})
        
        recommendations.append({
            'course': course_name,
            'category': data.get('category', 'General'),
            'description': data.get('description', 'No description available.'),
            'match_score': confidence,
            'match_percentage': f"{confidence:.1f}%",
            'match_type': get_match_type(confidence),
            'reasons': get_reasons(course_name, interests, skills, career_goal),
            'level': data.get('level', 'Not specified')
        })
    
    return recommendations
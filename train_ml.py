"""
DIGIBOOST INSTITUTE OF TECHNOLOGY
ML Model Training Script
Trains a model on synthetic data to recommend courses
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("🎓 DIGIBOOST ML MODEL TRAINING")
print("=" * 60)

# =========================================================
# 1. LOAD DATA
# =========================================================

try:
    df = pd.read_csv('data/student_data.csv')
    print(f"✅ Loaded {len(df)} student records")
except:
    print("❌ data/student_data.csv not found!")
    print("   Run: python generate_data.py first")
    exit()

# =========================================================
# 2. FEATURE ENGINEERING
# =========================================================

print("\n🔧 Feature Engineering...")

# ---- 2a. Qualification Mapping ----
qual_map = {
    'FSC Pre-Medical': 'FSC', 'FSC Pre-Engineering': 'FSC',
    'ICS': 'ICS', 'I.Com': 'ICom', 'FA': 'FA',
    'General Intermediate': 'Gen', 'DAE': 'DAE', 'A-Level': 'ALevel',
    'BS Computer Science': 'BS_CS', 'BS Information Technology': 'BS_IT',
    'BS Artificial Intelligence': 'BS_AI', 'BS Software Engineering': 'BS_SE',
    'BS Data Science': 'BS_DS', 'BS Cyber Security': 'BS_CSec',
    'BS Mathematics': 'BS_Math', 'BS Physics': 'BS_Phys',
    'BS English': 'BS_Eng', 'BS Business Administration': 'BS_BA',
    'BBA': 'BBA', 'BA': 'BA', 'B.Com': 'BCom', 'BS Any Subject': 'BS_Any'
}
df['qual_clean'] = df['qualification'].map(qual_map).fillna('General')

le_qual = LabelEncoder()
df['qual_encoded'] = le_qual.fit_transform(df['qual_clean'])

# ---- 2b. Experience Encoding ----
exp_map = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
df['exp_encoded'] = df['experience'].map(exp_map)

# ---- 2c. Interests (Multi-label Binarization) ----
df['interests_list'] = df['interests'].apply(
    lambda x: [i.strip().lower() for i in str(x).split(',')]
)
mlb_interests = MultiLabelBinarizer()
interests_encoded = mlb_interests.fit_transform(df['interests_list'])
interest_cols = [f'int_{col}' for col in mlb_interests.classes_]
interests_df = pd.DataFrame(interests_encoded, columns=interest_cols)

# ---- 2d. Skills (Multi-label Binarization) ----
df['skills_list'] = df['skills'].apply(
    lambda x: [i.strip().lower() for i in str(x).split(',')]
)
mlb_skills = MultiLabelBinarizer()
skills_encoded = mlb_skills.fit_transform(df['skills_list'])
skill_cols = [f'skill_{col}' for col in mlb_skills.classes_]
skills_df = pd.DataFrame(skills_encoded, columns=skill_cols)

# ---- 2e. Career Goal Keywords ----
career_keywords = ['developer', 'engineer', 'analyst', 'scientist', 'designer',
                   'manager', 'marketer', 'specialist', 'creator', 'freelancer',
                   'data', 'ai', 'web', 'mobile', 'cloud', 'security', 'business']
for kw in career_keywords:
    df[f'career_{kw}'] = df['career_goal'].str.lower().str.contains(kw, na=False).astype(int)
career_cols = [col for col in df.columns if col.startswith('career_')]

# ---- 2f. Combine All Features ----
df = pd.concat([df, interests_df, skills_df], axis=1)

feature_cols = ['age', 'qual_encoded', 'exp_encoded'] + list(interest_cols) + list(skill_cols) + career_cols

# Ensure all feature columns exist
existing_cols = [col for col in feature_cols if col in df.columns]
if len(existing_cols) != len(feature_cols):
    missing = set(feature_cols) - set(df.columns)
    print(f"⚠️ Missing columns: {missing}")

# ✅ FIX: Select only numeric columns to avoid string columns
X = df[existing_cols].select_dtypes(include=np.number)
# Drop any columns that are all NaN (if any)
X = X.dropna(axis=1, how='all')

y = df['recommended_course']

print(f"✅ Features: {X.shape[1]}, Samples: {X.shape[0]}")

# =========================================================
# 3. ENCODE TARGET
# =========================================================

le_target = LabelEncoder()
y_encoded = le_target.fit_transform(y)

# Print class distribution
print(f"\n📊 Class distribution (top 10):")
class_counts = pd.Series(y_encoded).value_counts().sort_index()
for i, count in class_counts.items():
    print(f"   {le_target.inverse_transform([i])[0]}: {count}")

# =========================================================
# 4. TRAIN/TEST SPLIT - WITHOUT STRATIFICATION
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

print(f"\n📚 Training set: {len(X_train)} samples")
print(f"🧪 Test set: {len(X_test)} samples")

# =========================================================
# 5. SCALE FEATURES
# =========================================================

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =========================================================
# 6. TRAIN RANDOM FOREST
# =========================================================

print("\n🚀 Training Random Forest Classifier...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_scaled, y_train)

# =========================================================
# 7. EVALUATE
# =========================================================

y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {accuracy:.4f}")

print("\n📊 Classification Report (Top classes):")
print(classification_report(y_test, y_pred))

# =========================================================
# 8. SAVE MODEL & ENCODERS
# =========================================================

print("\n💾 Saving Model...")
os.makedirs('models', exist_ok=True)

joblib.dump(model, 'models/ml_recommender.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(le_qual, 'models/qual_encoder.pkl')
joblib.dump(le_target, 'models/target_encoder.pkl')
joblib.dump(mlb_interests, 'models/interests_mlb.pkl')
joblib.dump(mlb_skills, 'models/skills_mlb.pkl')
joblib.dump(X.columns.tolist(), 'models/feature_columns.pkl')  # Save final column list
joblib.dump(career_keywords, 'models/career_keywords.pkl')
joblib.dump(mlb_interests.classes_, 'models/interests_classes.pkl')
joblib.dump(mlb_skills.classes_, 'models/skills_classes.pkl')

print("✅ Models saved in 'models/' directory")

# =========================================================
# 9. FEATURE IMPORTANCE
# =========================================================

print("\n📊 Top 15 Important Features:")
importance = model.feature_importances_
fi_df = pd.DataFrame({
    'feature': X.columns,
    'importance': importance
}).sort_values('importance', ascending=False).head(15)
print(fi_df.to_string(index=False))

print("\n" + "=" * 60)
print("✅ Training Complete!")
print("=" * 60)
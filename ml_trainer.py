"""
ML Trainer
AI Resume Tailoring System

Trains multiple Machine Learning models:
1. XGBoost
2. Random Forest
3. Decision Tree
4. Logistic Regression

The models learn resume-job matching patterns from
engineered numerical features.
"""

import os
import pickle
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score
)

from xgboost import XGBRegressor


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# IMPORT FEATURE ENGINEERING
# ============================================================

from modules.ml_feature_engineering import (
    create_features
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    resume_path = os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "resumes_clean.csv"
    )

    jobs_path = os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "jobs_clean.csv"
    )

    print("=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    print("\nResume dataset:")
    print(resume_path)

    print("\nJob dataset:")
    print(jobs_path)

    resumes = pd.read_csv(
        resume_path
    )

    jobs = pd.read_csv(
        jobs_path
    )

    print("\nResume shape:", resumes.shape)
    print("Job shape:", jobs.shape)

    return resumes, jobs


# ============================================================
# PREPARE TRAINING DATA
# ============================================================

def prepare_training_data():

    resumes, jobs = load_data()

    print("\n" + "=" * 60)
    print("CREATING ML TRAINING FEATURES")
    print("=" * 60)

    # --------------------------------------------------------
    # Find resume text column
    # --------------------------------------------------------

    resume_column = None

    possible_resume_columns = [
        "Resume_str",
        "resume",
        "resume_text",
        "text",
        "clean_resume"
    ]

    for column in possible_resume_columns:

        if column in resumes.columns:
            resume_column = column
            break

    if resume_column is None:

        raise ValueError(
            "Resume text column not found."
        )

    # --------------------------------------------------------
    # Find job description column
    # --------------------------------------------------------

    jd_column = None

    possible_jd_columns = [
        "Job Description",
        "job_description",
        "description",
        "job_description_text"
    ]

    for column in possible_jd_columns:

        if column in jobs.columns:
            jd_column = column
            break

    if jd_column is None:

        raise ValueError(
            "Job description column not found."
        )

    print(
        "\nResume column:",
        resume_column
    )

    print(
        "Job description column:",
        jd_column
    )

    # --------------------------------------------------------
    # Limit dataset for initial training
    # --------------------------------------------------------

    resumes = resumes.dropna(
        subset=[resume_column]
    )

    jobs = jobs.dropna(
        subset=[jd_column]
    )

    # --------------------------------------------------------
    # Create training pairs
    #
    # We create positive pairs from resume/JD samples.
    # Negative pairs are created by shuffling JDs.
    # --------------------------------------------------------

    n = min(
        len(resumes),
        len(jobs)
    )

    resumes = resumes.head(n).reset_index(
        drop=True
    )

    jobs = jobs.head(n).reset_index(
        drop=True
    )

    positive_resumes = resumes[
        resume_column
    ].astype(str).tolist()

    positive_jobs = jobs[
        jd_column
    ].astype(str).tolist()

    print(
        "\nPositive pairs:",
        len(positive_resumes)
    )

    # --------------------------------------------------------
    # Positive examples
    # --------------------------------------------------------

    X_positive = create_features(
        positive_resumes,
        positive_jobs
    )

    y_positive = np.ones(
        len(X_positive)
    )

    # --------------------------------------------------------
    # Negative examples
    # --------------------------------------------------------

    shuffled_jobs = jobs[
        jd_column
    ].sample(
        frac=1,
        random_state=42
    ).reset_index(
        drop=True
    )

    negative_jobs = shuffled_jobs.astype(
        str
    ).tolist()

    X_negative = create_features(
        positive_resumes,
        negative_jobs
    )

    y_negative = np.zeros(
        len(X_negative)
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    X = np.vstack(
        [
            X_positive,
            X_negative
        ]
    )

    y = np.concatenate(
        [
            y_positive,
            y_negative
        ]
    )

    print(
        "\nFinal feature matrix:",
        X.shape
    )

    print(
        "Labels:",
        y.shape
    )

    return X, y


# ============================================================
# TRAIN MODELS
# ============================================================

def train_models():

    X, y = prepare_training_data()

    print("\n" + "=" * 60)
    print("TRAIN / TEST SPLIT")
    print("=" * 60)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # --------------------------------------------------------
    # Scaling
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    # ========================================================
    # XGBOOST
    # ========================================================

    print("\nTraining XGBoost...")

    xgb_model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )

    xgb_model.fit(
        X_train,
        y_train
    )

    xgb_pred = xgb_model.predict(
        X_test
    )

    # ========================================================
    # RANDOM FOREST
    # ========================================================

    print("Training Random Forest...")

    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )

    rf_model.fit(
        X_train,
        y_train
    )

    rf_pred = rf_model.predict(
        X_test
    )

    # ========================================================
    # DECISION TREE
    # ========================================================

    print("Training Decision Tree...")

    dt_model = DecisionTreeRegressor(
        max_depth=10,
        random_state=42
    )

    dt_model.fit(
        X_train,
        y_train
    )

    dt_pred = dt_model.predict(
        X_test
    )

    # ========================================================
    # LOGISTIC REGRESSION
    # ========================================================

    print("Training Logistic Regression...")

    logistic_model = LogisticRegression(
        max_iter=1000,
        random_state=42
    )

    logistic_model.fit(
        X_train_scaled,
        y_train.astype(int)
    )

    logistic_pred = logistic_model.predict(
        X_test_scaled
    )

    # ========================================================
    # EVALUATION
    # ========================================================

    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

    # --------------------------------------------------------
    # XGBoost
    # --------------------------------------------------------

    xgb_mae = mean_absolute_error(
        y_test,
        xgb_pred
    )

    xgb_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            xgb_pred
        )
    )

    xgb_r2 = r2_score(
        y_test,
        xgb_pred
    )

    print("\nXGBoost")
    print(
        "MAE :",
        round(xgb_mae, 4)
    )
    print(
        "RMSE:",
        round(xgb_rmse, 4)
    )
    print(
        "R2  :",
        round(xgb_r2, 4)
    )

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    rf_mae = mean_absolute_error(
        y_test,
        rf_pred
    )

    rf_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            rf_pred
        )
    )

    rf_r2 = r2_score(
        y_test,
        rf_pred
    )

    print("\nRandom Forest")
    print(
        "MAE :",
        round(rf_mae, 4)
    )
    print(
        "RMSE:",
        round(rf_rmse, 4)
    )
    print(
        "R2  :",
        round(rf_r2, 4)
    )

    # --------------------------------------------------------
    # Decision Tree
    # --------------------------------------------------------

    dt_mae = mean_absolute_error(
        y_test,
        dt_pred
    )

    dt_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            dt_pred
        )
    )

    dt_r2 = r2_score(
        y_test,
        dt_pred
    )

    print("\nDecision Tree")
    print(
        "MAE :",
        round(dt_mae, 4)
    )
    print(
        "RMSE:",
        round(dt_rmse, 4)
    )
    print(
        "R2  :",
        round(dt_r2, 4)
    )

    # --------------------------------------------------------
    # Logistic Regression
    # --------------------------------------------------------

    logistic_accuracy = accuracy_score(
        y_test,
        logistic_pred
    )

    print("\nLogistic Regression")

    print(
        "Accuracy:",
        round(
            logistic_accuracy * 100,
            2
        ),
        "%"
    )

    # ========================================================
    # ENSEMBLE
    # ========================================================

    ensemble_prediction = (
        (xgb_pred * 0.50)
        +
        (rf_pred * 0.35)
        +
        (dt_pred * 0.15)
    )

    ensemble_mae = mean_absolute_error(
        y_test,
        ensemble_prediction
    )

    ensemble_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            ensemble_prediction
        )
    )

    ensemble_r2 = r2_score(
        y_test,
        ensemble_prediction
    )

    print("\n" + "=" * 60)
    print("ENSEMBLE MODEL")
    print("=" * 60)

    print(
        "\nXGBoost Weight      : 50%"
    )

    print(
        "Random Forest Weight: 35%"
    )

    print(
        "Decision Tree Weight: 15%"
    )

    print(
        "\nEnsemble MAE :",
        round(
            ensemble_mae,
            4
        )
    )

    print(
        "Ensemble RMSE:",
        round(
            ensemble_rmse,
            4
        )
    )

    print(
        "Ensemble R2  :",
        round(
            ensemble_r2,
            4
        )
    )

    # ========================================================
    # SAVE MODELS
    # ========================================================

    print("\n" + "=" * 60)
    print("SAVING TRAINED MODELS")
    print("=" * 60)

    with open(
        os.path.join(
            MODEL_DIR,
            "resume_jd_xgboost.pkl"
        ),
        "wb"
    ) as file:

        pickle.dump(
            xgb_model,
            file
        )

    with open(
        os.path.join(
            MODEL_DIR,
            "resume_jd_random_forest.pkl"
        ),
        "wb"
    ) as file:

        pickle.dump(
            rf_model,
            file
        )

    with open(
        os.path.join(
            MODEL_DIR,
            "resume_jd_decision_tree.pkl"
        ),
        "wb"
    ) as file:

        pickle.dump(
            dt_model,
            file
        )

    with open(
        os.path.join(
            MODEL_DIR,
            "resume_jd_logistic_regression.pkl"
        ),
        "wb"
    ) as file:

        pickle.dump(
            logistic_model,
            file
        )

    with open(
        os.path.join(
            MODEL_DIR,
            "feature_scaler.pkl"
        ),
        "wb"
    ) as file:

        pickle.dump(
            scaler,
            file
        )

    print("\nModels saved in:")

    print(
        MODEL_DIR
    )

    print("\nCreated files:")

    print(
        "✓ resume_jd_xgboost.pkl"
    )

    print(
        "✓ resume_jd_random_forest.pkl"
    )

    print(
        "✓ resume_jd_decision_tree.pkl"
    )

    print(
        "✓ resume_jd_logistic_regression.pkl"
    )

    print(
        "✓ feature_scaler.pkl"
    )

    print("\n" + "=" * 60)
    print("ML TRAINING COMPLETED")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    train_models()
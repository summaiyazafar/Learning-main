"""
============================================================
AI RESUME TAILORING SYSTEM
============================================================

File:
    ml_trainer.py

Purpose:
    Train machine-learning models for Resume vs Job
    Description matching.

Models:
    1. Logistic Regression
    2. Decision Tree
    3. Random Forest
    4. XGBoost (optional)

Features:
    (Imported from ml_feature_engineering to ensure consistency)

IMPORTANT:
    The feature order must remain identical during:
        - training
        - validation
        - prediction

Integration:
    - Uses ml_feature_engineering.FEATURE_NAMES.
    - Saves models as pickles in the 'models/' directory.
    - Provides a cached predictor for fast inference.
"""

from __future__ import annotations

import os
import pickle
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Import feature names from the feature engineering module
try:
    from modules.ml_feature_engineering import FEATURE_NAMES
except ImportError:
    # Fallback if the module is not available
    FEATURE_NAMES = [
        "skill_match",
        "semantic_similarity",
        "keyword_overlap",
        "critical_skill_coverage",
        "preferred_skill_coverage",
        "experience_match",
        "education_match",
        "resume_length",
        "jd_length"
    ]

N_FEATURES = len(FEATURE_NAMES)

# XGBoost is optional – gracefully handle if not installed
try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGBClassifier = None
    XGB_AVAILABLE = False

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
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
# CONSTANTS
# ============================================================

RANDOM_STATE = 42

# ============================================================
# SYNTHETIC TRAINING DATA
# ============================================================

def create_training_data(
    n_samples: int = 5000,
    random_state: int = RANDOM_STATE
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create synthetic training data with weak supervision.

    This is useful for building and testing the ML pipeline
    when real labelled Resume–JD pairs are not available.

    The label is generated using a weighted sum of features
    plus a small noise, thresholded at 0.50.

    Returns
    -------
    X : np.ndarray, shape (n_samples, N_FEATURES)
        Feature matrix.
    y : np.ndarray, shape (n_samples,)
        Binary labels (1 = good match, 0 = poor match).
    """
    rng = np.random.RandomState(random_state)

    # Generate random features in [0,1]
    X = rng.uniform(0.0, 1.0, size=(n_samples, N_FEATURES))

    # Feature weights (must sum to 1)
    # These reflect the relative importance of each feature.
    weights = np.array([
        0.25,  # skill_match
        0.25,  # semantic_similarity
        0.10,  # keyword_overlap
        0.15,  # critical_skill_coverage
        0.05,  # preferred_skill_coverage
        0.10,  # experience_match
        0.10,  # education_match
        0.00,  # resume_length (ignored)
        0.00   # jd_length (ignored)
    ])

    if len(weights) != N_FEATURES:
        raise ValueError(
            f"Weights length ({len(weights)}) does not match "
            f"number of features ({N_FEATURES})."
        )

    # Weighted score
    scores = np.dot(X, weights)

    # Add small random noise
    noise = rng.normal(loc=0.0, scale=0.035, size=n_samples)
    scores += noise

    # Binary label
    y = (scores >= 0.50).astype(int)

    return X, y


# ============================================================
# CREATE ML MODELS
# ============================================================

def create_models() -> Dict[str, Any]:
    """
    Create all candidate ML models.

    Returns
    -------
    dict
        Model name -> model instance.
    """
    models: Dict[str, Any] = {}

    # Logistic Regression with StandardScaler
    models["Logistic Regression"] = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=3000,
            random_state=RANDOM_STATE
        ))
    ])

    # Decision Tree
    models["Decision Tree"] = DecisionTreeClassifier(
        max_depth=6,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=RANDOM_STATE
    )

    # Random Forest
    models["Random Forest"] = RandomForestClassifier(
        n_estimators=250,
        max_depth=8,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    # XGBoost (only if available)
    if XGB_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            n_estimators=250,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=4
        )
    else:
        print("XGBoost not installed – skipping this model.")

    return models


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model(
    model: Any,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray
) -> Dict[str, Any]:
    """
    Train and evaluate a single ML model.

    Returns
    -------
    dict
        Contains trained model, metrics, predictions, etc.
    """
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    return {
        "model": model,
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "predictions": predictions,
        "classification_report": classification_report(y_test, predictions, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predictions)
    }


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(model: Any, model_name: str) -> str:
    """
    Save a trained model as a pickle file.
    """
    safe_name = model_name.lower().replace(" ", "_").replace("-", "_")
    path = os.path.join(MODEL_DIR, f"{safe_name}.pkl")
    with open(path, "wb") as f:
        pickle.dump(model, f)
    return path


# ============================================================
# SAVE FEATURE INFORMATION
# ============================================================

def save_feature_information() -> str:
    """
    Save feature names and metadata to ensure consistent order during inference.
    """
    feature_info = {
        "feature_names": FEATURE_NAMES,
        "number_of_features": N_FEATURES,
        "feature_range": "0-1",
        "random_state": RANDOM_STATE
    }
    path = os.path.join(MODEL_DIR, "feature_names.pkl")
    with open(path, "wb") as f:
        pickle.dump(feature_info, f)
    return path


# ============================================================
# LOAD FEATURE INFORMATION
# ============================================================

def load_feature_information() -> Dict[str, Any]:
    """
    Load saved feature names and metadata.
    """
    path = os.path.join(MODEL_DIR, "feature_names.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Feature information not found at {path}. "
            "Please run ml_trainer.py first."
        )
    with open(path, "rb") as f:
        return pickle.load(f)


# ============================================================
# TRAIN ALL MODELS
# ============================================================

def train_all_models() -> Dict[str, Any]:
    """
    Train all ML models, select the best one, and save everything.

    The best model is selected using F1 score as the primary metric,
    with accuracy used as the tie-breaker.

    Returns
    -------
    dict
        Training results, best model, paths, etc.
    """
    print("=" * 75)
    print("AI RESUME TAILORING SYSTEM - ML MODEL TRAINING")
    print("=" * 75)

    # Create synthetic data
    print("\nCreating synthetic training dataset...")
    X, y = create_training_data(n_samples=5000, random_state=RANDOM_STATE)
    print(f"Training samples : {len(X)}")
    print(f"Feature count    : {X.shape[1]}")
    print(f"Positive matches : {int(np.sum(y))}")
    print(f"Negative matches : {int(len(y) - np.sum(y))}")

    # Show feature order
    print("\nFeature Order:")
    for idx, name in enumerate(FEATURE_NAMES, start=1):
        print(f"{idx}. {name}")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTraining set : {len(X_train)}")
    print(f"Testing set  : {len(X_test)}")

    # Train each model
    models = create_models()
    results: Dict[str, Any] = {}
    best_model = None
    best_model_name = None
    best_f1 = -1.0
    best_accuracy = -1.0

    for model_name, model in models.items():
        print(f"\n{'-' * 75}")
        print(f"Training: {model_name}")
        print('-' * 75)

        try:
            result = evaluate_model(model, X_train, X_test, y_train, y_test)
            results[model_name] = result

            print(f"Accuracy : {result['accuracy']:.4f}")
            print(f"Precision: {result['precision']:.4f}")
            print(f"Recall   : {result['recall']:.4f}")
            print(f"F1 Score : {result['f1']:.4f}")

            # Select best model (F1 first, accuracy second)
            if (result["f1"] > best_f1) or (
                result["f1"] == best_f1 and result["accuracy"] > best_accuracy
            ):
                best_f1 = result["f1"]
                best_accuracy = result["accuracy"]
                best_model = result["model"]
                best_model_name = model_name

        except Exception as error:
            print(f"\nERROR training {model_name}:")
            print(error)

    if best_model is None:
        raise RuntimeError("No ML model was successfully trained.")

    # Save individual models
    print("\n" + "=" * 75)
    print("SAVING INDIVIDUAL MODELS")
    print("=" * 75)
    saved_models = {}
    for model_name, result in results.items():
        path = save_model(result["model"], model_name)
        saved_models[model_name] = path
        print(f"{model_name}: {path}")

    # Save best model separately
    best_model_path = os.path.join(MODEL_DIR, "best_resume_match_model.pkl")
    with open(best_model_path, "wb") as f:
        pickle.dump(best_model, f)
    print(f"\nBest model saved to: {best_model_path}")

    # Save feature information
    feature_info_path = save_feature_information()
    print(f"\nFeature information saved to: {feature_info_path}")

    # Print best model summary
    print("\n" + "=" * 75)
    print("BEST MODEL")
    print("=" * 75)
    print(f"Model    : {best_model_name}")
    print(f"Accuracy : {best_accuracy:.4f}")
    print(f"F1 Score : {best_f1:.4f}")
    print(f"Saved to : {best_model_path}")

    best_result = results[best_model_name]
    print("\nClassification Report:")
    print(best_result["classification_report"])
    print("Confusion Matrix:")
    print(best_result["confusion_matrix"])

    print("\n" + "=" * 75)
    print("MODEL TRAINING COMPLETED")
    print("=" * 75)

    return {
        "models": results,
        "best_model": best_model,
        "best_model_name": best_model_name,
        "best_accuracy": best_accuracy,
        "best_f1": best_f1,
        "feature_names": FEATURE_NAMES,
        "best_model_path": best_model_path
    }


# ============================================================
# MODEL LOADING (with caching)
# ============================================================

_CACHED_MODEL = None
_CACHED_FEATURE_NAMES = None


def load_best_model() -> Any:
    """
    Load the best trained model from disk, with caching.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    model_path = os.path.join(MODEL_DIR, "best_resume_match_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Trained model not found at {model_path}. "
            "Please run ml_trainer.py first."
        )
    with open(model_path, "rb") as f:
        _CACHED_MODEL = pickle.load(f)
    return _CACHED_MODEL


def load_feature_names() -> List[str]:
    """
    Load the saved feature names, with caching.
    """
    global _CACHED_FEATURE_NAMES
    if _CACHED_FEATURE_NAMES is not None:
        return _CACHED_FEATURE_NAMES

    info = load_feature_information()
    _CACHED_FEATURE_NAMES = info.get("feature_names", FEATURE_NAMES)
    return _CACHED_FEATURE_NAMES


# ============================================================
# PREPARE FEATURES FOR PREDICTION
# ============================================================

def prepare_prediction_features(
    features: Dict[str, float]
) -> np.ndarray:
    """
    Convert a feature dictionary into a numpy array
    using the exact feature order used during training.
    """
    # Use saved feature names if available, else global
    feature_names = load_feature_names()
    values = []
    for name in feature_names:
        try:
            val = float(features.get(name, 0.0))
        except (ValueError, TypeError):
            val = 0.0
        val = max(0.0, min(val, 1.0))
        values.append(val)
    return np.array(values, dtype=float).reshape(1, -1)


# ============================================================
# PREDICT MATCH
# ============================================================

def predict_match(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Predict whether a Resume and JD are a good match.

    Returns
    -------
    dict
        prediction (0/1),
        probability (0-1),
        match_percentage (0-100),
        match_level (string)
    """
    model = load_best_model()
    X = prepare_prediction_features(features)

    prediction = int(model.predict(X)[0])

    if hasattr(model, "predict_proba"):
        proba = float(model.predict_proba(X)[0][1])
    else:
        proba = float(prediction)

    proba = max(0.0, min(proba, 1.0))
    match_pct = proba * 100

    if match_pct >= 85:
        level = "Excellent Match"
    elif match_pct >= 70:
        level = "Strong Match"
    elif match_pct >= 55:
        level = "Moderate Match"
    elif match_pct >= 40:
        level = "Weak Match"
    else:
        level = "Low Match"

    return {
        "prediction": prediction,
        "probability": round(proba, 4),
        "match_percentage": round(match_pct, 2),
        "match_level": level
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    train_all_models()
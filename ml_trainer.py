import os
import pickle
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# ---------------------------------------------------------
# FEATURE NAMES
# ---------------------------------------------------------

FEATURE_NAMES = [
    "skill_match",
    "semantic_similarity",
    "keyword_overlap",
    "experience_match",
    "education_match",
    "resume_length",
    "jd_length"
]


# ---------------------------------------------------------
# CREATE SYNTHETIC TRAINING DATA
# ---------------------------------------------------------

def create_training_data(n_samples=3000, random_state=42):

    rng = np.random.RandomState(random_state)

    X = rng.uniform(
        low=0.0,
        high=1.0,
        size=(n_samples, 7)
    )

    # Feature weights
    weights = np.array([
        0.35,   # skill match
        0.30,   # semantic similarity
        0.15,   # keyword overlap
        0.10,   # experience
        0.10,   # education
        0.00,   # resume length
        0.00    # JD length
    ])

    scores = np.dot(X, weights)

    # Add small noise
    noise = rng.normal(
        loc=0.0,
        scale=0.04,
        size=n_samples
    )

    scores = scores + noise

    y = (scores >= 0.50).astype(int)

    return X, y


# ---------------------------------------------------------
# CREATE MODELS
# ---------------------------------------------------------

def create_models():

    models = {

        "Logistic Regression": Pipeline([
            (
                "scaler",
                StandardScaler()
            ),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    random_state=42
                )
            )
        ]),

        "Decision Tree": DecisionTreeClassifier(
            max_depth=6,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),

        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=4
        )
    }

    return models


# ---------------------------------------------------------
# EVALUATE MODEL
# ---------------------------------------------------------

def evaluate_model(model, X_train, X_test, y_train, y_test):

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    return {
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "predictions": predictions
    }


# ---------------------------------------------------------
# SAVE MODEL
# ---------------------------------------------------------

def save_model(model, model_name):

    safe_name = (
        model_name
        .lower()
        .replace(" ", "_")
    )

    path = os.path.join(
        MODEL_DIR,
        f"{safe_name}.pkl"
    )

    with open(
        path,
        "wb"
    ) as file:

        pickle.dump(
            model,
            file
        )

    return path


# ---------------------------------------------------------
# TRAIN ALL MODELS
# ---------------------------------------------------------

def train_all_models():

    print("=" * 70)
    print("AI RESUME TAILORING - ML MODEL TRAINING")
    print("=" * 70)

    print("\nCreating training dataset...")

    X, y = create_training_data(
        n_samples=3000
    )

    print(
        f"Training samples: {len(X)}"
    )

    print(
        f"Features: {X.shape[1]}"
    )

    print(
        f"Positive matches: {sum(y)}"
    )

    print(
        f"Negative matches: {len(y) - sum(y)}"
    )

    # -----------------------------------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(
        f"\nTraining set: {len(X_train)}"
    )

    print(
        f"Testing set: {len(X_test)}"
    )

    # -----------------------------------------------------
    # MODELS
    # -----------------------------------------------------

    models = create_models()

    results = {}

    best_model = None
    best_model_name = None
    best_accuracy = -1

    # -----------------------------------------------------
    # TRAIN
    # -----------------------------------------------------

    for model_name, model in models.items():

        print("\n" + "-" * 70)
        print(
            f"Training: {model_name}"
        )
        print("-" * 70)

        try:

            result = evaluate_model(
                model,
                X_train,
                X_test,
                y_train,
                y_test
            )

            results[model_name] = result

            print(
                f"Accuracy : {result['accuracy']:.4f}"
            )

            print(
                f"Precision: {result['precision']:.4f}"
            )

            print(
                f"Recall   : {result['recall']:.4f}"
            )

            print(
                f"F1 Score : {result['f1']:.4f}"
            )

            if result["accuracy"] > best_accuracy:

                best_accuracy = result["accuracy"]

                best_model = result["model"]

                best_model_name = model_name

        except Exception as error:

            print(
                f"ERROR training {model_name}:"
            )

            print(error)

    # -----------------------------------------------------
    # SAVE INDIVIDUAL MODELS
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("SAVING MODELS")
    print("=" * 70)

    for model_name, result in results.items():

        path = save_model(
            result["model"],
            model_name
        )

        print(
            f"{model_name}: {path}"
        )

    # -----------------------------------------------------
    # SAVE BEST MODEL
    # -----------------------------------------------------

    best_model_path = os.path.join(
        MODEL_DIR,
        "best_resume_match_model.pkl"
    )

    with open(
        best_model_path,
        "wb"
    ) as file:

        pickle.dump(
            best_model,
            file
        )

    # -----------------------------------------------------
    # SAVE FEATURE INFORMATION
    # -----------------------------------------------------

    feature_info_path = os.path.join(
        MODEL_DIR,
        "feature_names.pkl"
    )

    with open(
        feature_info_path,
        "wb"
    ) as file:

        pickle.dump(
            FEATURE_NAMES,
            file
        )

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("BEST MODEL")
    print("=" * 70)

    print(
        f"Model    : {best_model_name}"
    )

    print(
        f"Accuracy : {best_accuracy:.4f}"
    )

    print(
        f"Saved to : {best_model_path}"
    )

    print("\n" + "=" * 70)
    print("MODEL TRAINING COMPLETED")
    print("=" * 70)

    return {
        "models": results,
        "best_model": best_model,
        "best_model_name": best_model_name,
        "best_accuracy": best_accuracy
    }


# ---------------------------------------------------------
# PREDICT MATCH
# ---------------------------------------------------------

def predict_match(features):

    model_path = os.path.join(
        MODEL_DIR,
        "best_resume_match_model.pkl"
    )

    if not os.path.exists(model_path):

        raise FileNotFoundError(
            "Trained model not found. "
            "Run ml_trainer.py first."
        )

    with open(
        model_path,
        "rb"
    ) as file:

        model = pickle.load(
            file
        )

    values = [
        float(features.get(name, 0.0))
        for name in FEATURE_NAMES
    ]

    X = np.array(
        values,
        dtype=float
    ).reshape(1, -1)

    prediction = model.predict(X)[0]

    if hasattr(
        model,
        "predict_proba"
    ):

        probability = model.predict_proba(
            X
        )[0][1]

    else:

        probability = float(
            prediction
        )

    return {
        "prediction": int(prediction),
        "probability": float(probability)
    }


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    train_all_models()
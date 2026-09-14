from config import DATASET
from query import fetch_training_data
import os
import sys
import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error
import joblib

_api = Path(__file__).resolve().parent.parent / "api"
if str(_api) not in sys.path:
    sys.path.insert(0, str(_api))
from features import engineer_features  # noqa: E402

MODEL_PATH = Path(os.environ.get(
    "MODEL_PATH",
    Path(__file__).resolve().parent.parent / "api" / "model.pkl",
))

FEATURES = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'semester_progress',
            'temperature', 'is_weekend', 'weather_adverse']

def train():
    if os.environ.get("TRAIN_FROM_CSV"):
        df = pd.read_csv(DATASET)
        df = df.drop_duplicates(subset=["hour", "day_of_week", "semester_progress"])
    else:
        df = fetch_training_data()

    # Reuse api/features.py so training and inference always encode identically.
    engineered = df.apply(lambda row: engineer_features(
        row['hour'], row['day_of_week'], row['semester_progress'],
        row['weather'], row['temperature'],
    ), axis=1, result_type='expand')

    X = engineered[FEATURES]
    y = df['occupancy']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)

    cv_scores = -cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
    print(f"5-fold CV MAE: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))
    print(f"Holdout MAE: {mae:.4f}")

    importances = pd.Series(model.feature_importances_, index=FEATURES)
    print(importances.sort_values(ascending=False))

    joblib.dump(model, MODEL_PATH)
    print(f"Saved {MODEL_PATH}")

if __name__ == "__main__":
    train()
    
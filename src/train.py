from config import DATASET, WEATHER
from query import fetch_training_data
import os
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

MODEL_PATH = Path(os.environ.get(
    "MODEL_PATH",
    Path(__file__).resolve().parent.parent / "api" / "model.pkl",
))

# Fixed category list (not just whatever codes happen to appear in a given
# training run) so the one-hot columns are always the same, matching
# api/features.py's WEATHER_CODES. Includes 0 - schemas.py's PredictionRequest
# allows weather=0 (older/unlabeled "unknown" reading, present in historical
# data) alongside config.WEATHER's named 1-8 categories.
WEATHER_CODES = [0] + sorted(WEATHER.values())

def train():
    if os.environ.get("TRAIN_FROM_CSV"):
        df = pd.read_csv(DATASET)
        df = df.drop_duplicates(subset=["hour", "day_of_week", "semester_progress"])
    else:
        df = fetch_training_data()

    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin']  = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos']  = np.cos(2 * np.pi * df['day_of_week'] / 7)

    # .astype(CategoricalDtype) instead of pd.Categorical(...) - the latter
    # returns a bare array with no index, which silently misaligns with df in
    # the concat below once drop_duplicates has left gaps in df's index.
    weather_dtype = pd.CategoricalDtype(categories=WEATHER_CODES)
    weather_dummies = pd.get_dummies(df['weather'].astype(weather_dtype), prefix='weather', dtype=int)
    df = pd.concat([df, weather_dummies], axis=1)

    features = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos',
                'semester_progress', 'temperature'] + list(weather_dummies.columns)

    X = df[features]
    y = df['occupancy']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
    model.fit(X_train, y_train)
    
    mae = mean_absolute_error(y_test, model.predict(X_test))
    print(f"MAE: {mae:.4f}")

    importances = pd.Series(model.feature_importances_, index=features)
    print(importances.sort_values(ascending=False))
    
    joblib.dump(model, MODEL_PATH)
    print(f"Saved {MODEL_PATH}")

if __name__ == "__main__":
    train()
    
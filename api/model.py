from pathlib import Path

import joblib
import pandas as pd

try:
    from .features import engineer_features
except ImportError:  # pragma: no cover
    from features import engineer_features

_MODEL_PATH = Path(__file__).resolve().with_name("model.pkl")
_MODEL = None
_FALLBACK_WEATHER = 3  # Cloudy
_FALLBACK_TEMPERATURE = 60.0


def _load_model():
    global _MODEL
    if _MODEL is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {_MODEL_PATH}. Run `python src/train.py` to generate it."
            )
        _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL


def predict(hour, day_of_week, semester_progress, weather, temperature) -> float:
    model = _load_model()
    features = engineer_features(hour, day_of_week, semester_progress, weather, temperature)
    X = pd.DataFrame([features])
    prediction = model.predict(X)[0]
    return round(float(prediction), 4)


if __name__ == "__main__":
    import sys
    from datetime import datetime
    from zoneinfo import ZoneInfo

    _src = Path(__file__).resolve().parent.parent / "src"
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

    from fetch_data import fetch_semester_progress, fetch_weather

    now = datetime.now(ZoneInfo("America/New_York"))
    semester_progress = fetch_semester_progress(now)
    if semester_progress == -1:
        print("School is not in session — no prediction")
        raise SystemExit(0)

    weather, temperature = fetch_weather()
    occupancy = predict(now.hour, now.weekday(), semester_progress, weather, temperature)
    print(f"Predicted occupancy: {occupancy:.1%}")
from pathlib import Path

import joblib
import pandas as pd
from features import engineer_features

model = joblib.load(Path(__file__).resolve().parent / "model.pkl")

def predict(hour, day_of_week, semester_progress, weather, temperature) -> float:
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
import numpy as np

ADVERSE_WEATHER_CODES = {4, 5, 6, 7}

def engineer_features(hour, day_of_week, semester_progress, weather, temperature):
    return {
        'hour_sin': np.sin(2 * np.pi * hour / 24),
        'hour_cos': np.cos(2 * np.pi * hour / 24),
        'day_sin':  np.sin(2 * np.pi * day_of_week / 7),
        'day_cos':  np.cos(2 * np.pi * day_of_week / 7),
        'semester_progress': semester_progress,
        'temperature': temperature,
        'is_weekend': int(day_of_week in (5, 6)),
        'weather_adverse': int(weather in ADVERSE_WEATHER_CODES),
    }
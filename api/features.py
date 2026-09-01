import numpy as np

WEATHER_CODES = list(range(0, 9))

def engineer_features(hour, day_of_week, semester_progress, weather, temperature):
    features = {
        'hour_sin': np.sin(2 * np.pi * hour / 24),
        'hour_cos': np.cos(2 * np.pi * hour / 24),
        'day_sin':  np.sin(2 * np.pi * day_of_week / 7),
        'day_cos':  np.cos(2 * np.pi * day_of_week / 7),
        'semester_progress': semester_progress,
        'temperature': temperature,
    }
    for code in WEATHER_CODES:
        features[f'weather_{code}'] = int(weather == code)
    return features
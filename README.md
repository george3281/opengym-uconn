# opengym-uconn

Predicts real-time occupancy at the UConn recreation center using a trained ML model, and shows both live and forecasted occupancy on a web dashboard.

## How it works

1. **Scraper** — a scheduled GitHub Actions job (`.github/workflows/scrape.yml`, currently every 2 hours) runs `src/fetch_data.py`, which uses Selenium to read live occupancy % from the SafeSpace API, pulls current weather from Open-Meteo, and writes a row to Supabase (Postgres).
2. **Training** — `src/train.py` pulls historical readings from Supabase and trains a `GradientBoostingRegressor` (scikit-learn) on cyclical encodings of hour-of-day and day-of-week, plus semester progress, weather condition, and temperature.
3. **API** — a FastAPI service (`api/`) serve
   - `GET /occupancy` — live occupancy, scraped on request
   - `POST /predict` — model-predicted occupaeather/temperature

   The model is retrained based on the latest Supabase data (see `api/dockerfile`).
4. **Frontend** — a Next.js app (`displays current occupancy, a forecast, a heatmap of historical trends, and summary stats).

## Tech stack

- **Backend**: Python, FastAPI, scikit-learn, pandas, Selenium, Open-Meteo, Supabase
- **Frontend**: Next.js 16, React 19, TypeScrs
- **Infra**: Docker, Docker Compose, AWS EC2, GitHub Actions (scheduled scraping)

## Running locally

**Environment variables** (`.env`): `SUPABASE_URL`, `SUPABASE_KEY`, and optionally `CORS_ORIGINS` (API) /
`NEXT_PUBLIC_FASTAPI_URL`

**Backend**
```bash
cd api
pip install -r requirements.txt
# model.pkl must exist — either run src/trainown
uvicorn main:app --reload

Frontend
cd opengym-app
npm install
npm run dev

Docker (both services)
docker compose up --build
```

Manual EC2 deployment steps (build for linux/amd64, docker save/scp/load, run) are documented in ec2.md.

# ⚡ Wind Forecast Decision Portal

A full-stack enterprise dashboard built for UK energy utility traders to evaluate Day-Ahead wind generation forecasts against actual production, minimizing volumetric risk and imbalance penalties.

**Live Application:** https://zento-phi.vercel.app/  
**Video Walkthrough:** [Insert your Unlisted YouTube Link Here]

---

## 📖 The Business Context
To meet consumer electricity demand, energy utilities must buy power from the UK Day-Ahead market. Wind generation is highly weather-dependent. Because purchase decisions must be made the day *prior* to delivery (Gate Closure), traders rely heavily on forecasts. 

**The core challenge (and the trap):** 
If a trader is buying power for January 5th, they make that decision at a specific cutoff time on January 4th. A naive software implementation might show the trader the *most accurate* forecast available on January 5th, but this is **data leakage**. The trader didn't have that data at the time of the decision. 

**The Solution:**
This application implements strict temporal filtering. It ensures that when viewing a specific delivery date, the system only aggregates and evaluates forecasts whose `publish_time_utc` was strictly **before** the configurable Gate Closure cutoff on D-1.

---

## 📐 Methodology & Accuracy Metrics

This dashboard provides a unified view of both the decision data and the post-delivery accuracy metrics, acting as both a trading tool and a quantitative review mechanism.

**Data Transformations & Math:**
*   **Volume Calculation (MWh):** The UK grid settles in half-hour periods (48 slots per day). Since Elexon provides wind generation in Megawatts (MW), the total daily volume is calculated as: `Sum of MW × 0.5 hours = Total MWh`.
*   **Error Definition:** Error is calculated as `Forecast MW - Actual MW`. A positive number indicates over-forecasting (expecting more wind than arrived); a negative number indicates under-forecasting.
*   **Temporal Normalization:** All user inputs (Gate Closure time) are ingested as UK Local Time and immediately converted to strict UTC for database querying to prevent Daylight Saving boundary bugs. The frontend explicitly formats output back to UTC to avoid automatic browser time-shifting (e.g., IST/PST rendering).

**Accuracy Metrics Calculated:**
*   **MAE (Mean Absolute Error):** The average magnitude of errors in MW, regardless of direction. Gives the trader a baseline "daily risk band."
*   **RMSE (Root Mean Square Error):** Penalizes larger forecast misses more heavily than smaller ones.
*   **System Bias:** The average of all errors. Shows if the forecaster systematically over-predicts or under-predicts wind generation.
*   **P90 Error Band:** The 90th percentile of absolute errors. This tells the trader: "90% of the time, the forecast is off by no more than X MW."

---

## 🏗️ Architecture & Pipeline

The application is decoupled into three distinct layers to ensure resilience, speed, and accuracy:

1. **Data Ingestion Layer (Python/Pandas)**
   * **APIs Used:** Elexon BMRS (`/datasets/FUELHH/stream` for Actuals, `/datasets/WINDFOR/stream` for Forecasts).
   * **Strategy:** Elexon's API is paginated, rate-limited, and can experience downtime. An ingestion script (`backend/scripts/ingest.py`) uses exponential backoff to query the API, standardize timezones, calculate forecast horizons, and compile the data into local CSVs. This guarantees the dashboard loads in milliseconds.

2. **Backend API Layer (FastAPI)**
   * **Logic:** When a request hits `/api/decision`, the backend uses Pandas to execute the Gate Closure logic. It filters forecasts published $\le$ the cutoff time, groups by `start_time_utc`, selects the *latest valid* forecast for each settlement period, and merges it with the actuals.

3. **Frontend Presentation Layer (React + Vite + Recharts)**
   * **Design:** Built to mimic a dense, high-contrast quantitative trading terminal. 
   * **Tech:** Utilizes Tailwind CSS and Recharts for a highly optimized, dual-axis Intraday Area Chart capable of handling high-density time-series data without blocking the main UI thread.

---

## 📂 Project Structure

    zento/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py          # FastAPI application & REST endpoints
    │   │   ├── config.py        # Environment & timezone configurations
    │   │   └── services/
    │   │       └── selection.py # Pandas core logic (temporal filtering, metrics math)
    │   ├── data/
    │   │   ├── actuals.csv      # Ingested FUELHH data
    │   │   └── forecasts.csv    # Ingested WINDFOR data
    │   ├── scripts/
    │   │   └── ingest.py        # Elexon API extraction & transformation script
    │   └── test_main.py         # Pytest suite for data leakage & math verification
    ├── frontend/
    │   ├── src/
    │   │   ├── App.tsx          # Main React Trading Terminal UI
    │   │   ├── index.css        # Tailwind directives
    │   │   └── main.tsx         # React DOM entry
    │   ├── tailwind.config.js   # UI theme configuration
    │   └── vite.config.ts       # Build tools and API proxy config
    ├── docker-compose.yml       # Local container orchestration
    ├── Dockerfile               # Multi-stage build (Node -> Python)
    └── requirements.txt         # Python dependencies (Root for Vercel deployment)

---

## 🚀 How to Run the Application

### Option 1: Docker (Recommended for Tech Review)
The application is fully containerized using a multi-stage build.
1. Ensure Docker Desktop is running.
2. In the root directory, run:
   `docker-compose up --build`
3. Open `http://localhost:8000` in your browser. *(Note: Port 8000 serves both the API and the static React files in the Docker build).*

### Option 2: Local Development Mode

**Start the Backend:**
1. Create and activate a virtual environment:
   `python -m venv venv`
   `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run the server:
   `python -m uvicorn backend.app.main:app --reload`

**Start the Frontend:**
1. Open a second terminal and navigate to the frontend directory:
   `cd frontend`
2. Install dependencies and run:
   `npm install`
   `npm run dev`
3. Open `http://localhost:5173` in your browser.

---

## 🧪 Automated Testing

To explicitly prove the application does not suffer from look-ahead data leakage, a test suite is included using `pytest`. 
To run the tests locally:
```bash
pytest backend/test_main.py

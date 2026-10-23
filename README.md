# ⚡ Day-Ahead Market Desk: Wind Arbitration Terminal

A full-stack enterprise dashboard built for UK energy utility traders to evaluate Day-Ahead wind generation forecasts against actual production, minimizing volumetric risk and imbalance penalties.

**Live Application:** [Insert your Vercel Link Here]  
**Video Walkthrough:** [Insert your Unlisted YouTube Link Here]

---

## 📖 The Business Context
To meet consumer electricity demand, energy utilities must buy power from the UK Day-Ahead market. Wind generation is highly weather-dependent. Because purchase decisions must be made the day *prior* to delivery (Gate Closure), traders rely heavily on forecasts. 

**The core challenge (and the trap):** 
If a trader is buying power for January 5th, they make that decision at a specific cutoff time on January 4th. A naive software implementation might show the trader the *most accurate* forecast available on January 5th, but this is **data leakage**. The trader didn't have that data at the time of the decision. 

**The Solution:**
This application implements strict temporal filtering. It ensures that when viewing a specific delivery date, the system only aggregates and evaluates forecasts whose `publishTime` was strictly **before** the configurable Gate Closure cutoff on D-1.

---

## 🏗️ Architecture & Thought Process

The application is decoupled into three distinct layers to ensure resilience, speed, and accuracy:

1. **Data Ingestion Layer (Python/Pandas)**
   * **APIs Used:** Elexon BMRS (`/datasets/FUELHH/stream` for Actuals, `/datasets/WINDFOR/stream` for Forecasts).
   * **Strategy:** Elexon's API is paginated, rate-limited, and can experience downtime. I wrote an ingestion script (`backend/scripts/ingest.py`) with exponential backoff to query the API in chunks, standardize timezones to UTC, calculate forecast horizons, deduplicate records, and compile the data into local CSVs. This guarantees the dashboard loads in milliseconds and never fails due to upstream API outages.

2. **Backend API Layer (FastAPI)**
   * **Logic:** When a request hits `/api/decision`, the backend uses Pandas to execute the Gate Closure logic. It filters the forecasts to only those published $\le$ the cutoff time, groups by `start_time_utc`, selects the *latest valid* forecast for each half-hour settlement period, and merges it with the actuals.
   * **Metrics:** Calculates Total Forecast (MWh), Risk Exposure via Mean Absolute Error (MAE), and flags missing grid data.

3. **Frontend Presentation Layer (React + Vite + Recharts)**
   * **Design:** Built to mimic a dense, high-contrast quantitative trading terminal (e.g., Bloomberg Terminal). 
   * **Tech:** Utilizes Tailwind CSS for flat, utilitarian styling, `lucide-react` for iconography, and Recharts for a highly optimized, dual-axis Intraday Area Chart capable of handling high-density time-series data without blocking the main UI thread.

---

## 📂 Project Structure

    zento/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py          # FastAPI application & REST endpoints
    │   │   ├── config.py        # Environment & timezone configurations
    │   │   └── services/
    │   │       └── selection.py # Pandas core logic (temporal filtering, MAE math)
    │   ├── data/
    │   │   ├── actuals.csv      # Ingested FUELHH data
    │   │   └── forecasts.csv    # Ingested WINDFOR data
    │   ├── scripts/
    │   │   ├── ingest.py        # Elexon API extraction & transformation script
    │   │   └── verify_api.py    # Initial API payload diagnostic tool
    │   └── requirements.txt     # Python dependencies
    ├── frontend/
    │   ├── src/
    │   │   ├── App.tsx          # Main React Trading Terminal UI
    │   │   ├── index.css        # Tailwind directives
    │   │   └── main.tsx         # React DOM entry
    │   ├── tailwind.config.js   # UI theme configuration
    │   └── vite.config.ts       # Build tools and API proxy config
    ├── docker-compose.yml       # Local container orchestration
    └── Dockerfile               # Multi-stage build (Node -> Python)

---

## 🚀 How to Run the Application

### Option 1: Docker (Recommended for Tech Review)
The application is fully containerized using a multi-stage build.
1. Ensure Docker Desktop is running.
2. In the root directory, run:
   `docker-compose up --build`
3. Open `http://localhost:8000` in your browser. *(Note: Port 8000 serves both the API and the static React files in the Docker build).*

### Option 2: Local Development Mode
If you wish to run the environments separately with hot-reloading:

**Start the Backend:**
1. Create and activate a virtual environment:
   `python -m venv venv`
   `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
2. Install dependencies:
   `pip install -r backend/requirements.txt`
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

## ⚠️ Assumptions & Limitations

1. **Gate Closure Default:** The market gate closure for Day-Ahead trading is assumed to be 09:00 AM (UK Local Time) on D-1. The UI allows this to be configured dynamically.
2. **Missing Data Handling:** The system flags missing half-hour actuals rather than silently interpolating them, as fabricated volume data introduces severe financial risk in energy trading. Elexon forecasts occasionally output hourly rather than half-hourly; the frontend chart explicitly connects these nulls for visual continuity while preserving the raw underlying data integrity.
3. **Timezones:** All backend storage and processing is done in strict UTC to avoid DST boundary bugs. 

---

## 🤖 AI Tools Disclosure

In accordance with the assignment guidelines, AI tools were utilized during development:
* **Claude (Anthropic):** Utilized for initial architectural brainstorming, defining the bounds of the domain logic, and drafting the step-by-step project blueprint.
* **Gemini (Google):** Utilized as a pair-programming assistant to write the exponential backoff logic for the Elexon API ingestion script, optimize Pandas data-frame transformations, and assist with translating the UI requirements into Tailwind CSS utility classes and Recharts component structuring.
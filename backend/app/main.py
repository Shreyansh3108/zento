from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from backend.app.services.selection import get_decision_data

app = FastAPI(title="Wind Forecast Decision API")

# Enable CORS to allow the React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/decision")
def get_decision(delivery_date: str, cutoff: str = "09:00"):
    try:
        # Parse the date string from the frontend
        d = datetime.strptime(delivery_date, "%Y-%m-%d").date()
        
        # Get the filtered dataframe and the pre-calculated metrics dictionary
        df, metadata = get_decision_data(d, cutoff)
        
        # Safely convert Pandas DataFrame to a JSON-compliant dict (translates NaN to null)
        records = json.loads(df.to_json(orient="records"))
        
        return {
            "data": records,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
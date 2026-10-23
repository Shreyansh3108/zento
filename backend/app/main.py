import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from backend.app.services.selection import get_decision_data

app = FastAPI(title="Zento Energy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Zento API is running"}

@app.get("/api/decision")
def get_decision(delivery_date: date, cutoff: str = Query("09:00")):
    # Validate date range (Jan 2 to Feb 1, 2026) per architecture
    if not (date(2026, 1, 2) <= delivery_date <= date(2026, 2, 1)):
        raise HTTPException(
            status_code=400, 
            detail="Delivery date must be between 2026-01-02 and 2026-02-01"
        )
    
    try:
        df, cutoff_utc = get_decision_data(delivery_date, cutoff)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Replace NaNs with None for valid JSON serialization
    df = df.replace({np.nan: None})
    
    # Calculate brief summary metrics
    valid_rows = df.dropna(subset=["error"])
    mae = float(valid_rows["error"].abs().mean()) if not valid_rows.empty else None
    total_forecast_mwh = float(df["forecast_mw"].sum() * 0.5) # MW to MWh per half hour
    
    return {
        "metadata": {
            "delivery_date": str(delivery_date),
            "cutoff_applied_utc": cutoff_utc.isoformat(),
            "total_forecast_mwh": total_forecast_mwh,
            "mae_mw": mae,
            "missing_actuals": int(df["actual_mw"].isna().sum())
        },
        "data": df.to_dict(orient="records")
    }
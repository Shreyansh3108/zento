import pandas as pd
from datetime import datetime, date, time, timedelta
from backend.app.config import ACTUALS_PATH, FORECASTS_PATH, DEFAULT_CUTOFF, TZ_LONDON, TZ_UTC

# Load data into memory once at startup
df_actuals = pd.read_csv(ACTUALS_PATH, parse_dates=["start_time_utc"])
df_forecasts = pd.read_csv(FORECASTS_PATH, parse_dates=["start_time_utc", "publish_time_utc"])

def get_decision_data(delivery_date: date, cutoff_str: str = DEFAULT_CUTOFF):
    # 1. Parse cutoff time (e.g., "09:00" on the day BEFORE delivery)
    h, m = map(int, cutoff_str.split(':'))
    cutoff_local = datetime.combine(delivery_date - timedelta(days=1), time(h, m), tzinfo=TZ_LONDON)
    cutoff_utc = cutoff_local.astimezone(TZ_UTC)

    # 2. Target delivery day window (local midnight to midnight)
    day_start_local = datetime.combine(delivery_date, time(0, 0), tzinfo=TZ_LONDON)
    day_end_local = day_start_local + timedelta(days=1)
    day_start_utc = day_start_local.astimezone(TZ_UTC)
    day_end_utc = day_end_local.astimezone(TZ_UTC)

    # 3. Filter Forecasts: Must be for the delivery day, AND published <= cutoff
    f = df_forecasts[
        (df_forecasts["start_time_utc"] >= pd.to_datetime(day_start_utc)) & 
        (df_forecasts["start_time_utc"] < pd.to_datetime(day_end_utc)) & 
        (df_forecasts["publish_time_utc"] <= pd.to_datetime(cutoff_utc))
    ]

    # 4. Get the latest available forecast for each half-hour slot
    latest = f.sort_values("publish_time_utc").groupby("start_time_utc").tail(1)

    # 5. Get actuals for the same day
    a = df_actuals[
        (df_actuals["start_time_utc"] >= pd.to_datetime(day_start_utc)) & 
        (df_actuals["start_time_utc"] < pd.to_datetime(day_end_utc))
    ]

    # 6. Merge actuals and forecasts
    joined = pd.merge(latest, a, on="start_time_utc", how="outer")
    
    # Calculate error (positive = over-forecast)
    joined["error"] = joined["forecast_mw"] - joined["actual_mw"]
    joined.sort_values("start_time_utc", inplace=True)
    
    return joined, cutoff_utc
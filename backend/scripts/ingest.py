import os
import time
import requests
import pandas as pd
from datetime import timedelta

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_with_retry(url, params, retries=3):
    """Fetches data with a simple backoff retry mechanism for API limits."""
    for attempt in range(retries):
        try:
            res = requests.get(url, params=params, timeout=30)
            if res.status_code == 200:
                return res.json()
            print(f"  Warning: {res.status_code} - {res.text}. Retrying in {2 ** attempt}s...")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"  Error: {e}. Retrying in {2 ** attempt}s...")
            time.sleep(2 ** attempt)
    return []

def ingest_actuals():
    print("\n--- Ingesting Actuals (FUELHH) ---")
    # Jan 2026 decisions apply to delivery days 2 Jan - 1 Feb 2026
    start_date = pd.to_datetime("2026-01-02")
    end_date = pd.to_datetime("2026-02-01")
    
    all_data = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        print(f"  Fetching actuals for {date_str}...")
        params = {
            "settlementDateFrom": date_str,
            "settlementDateTo": date_str,
            "fuelType": "WIND"
        }
        data = fetch_with_retry(f"{BASE_URL}/FUELHH/stream", params)
        all_data.extend(data)
        current += timedelta(days=1)
        
    df = pd.DataFrame(all_data)
    if df.empty:
        print("  No actuals found!")
        return
        
    # Transform per architecture brief
    df = df[["startTime", "settlementDate", "settlementPeriod", "generation"]]
    df.rename(columns={
        "startTime": "start_time_utc",
        "settlementDate": "settlement_date",
        "settlementPeriod": "settlement_period",
        "generation": "actual_mw"
    }, inplace=True)
    
    # Deduplicate and sort
    df.drop_duplicates(subset=["start_time_utc"], inplace=True)
    df.sort_values("start_time_utc", inplace=True)
    
    out_path = os.path.join(DATA_DIR, "actuals.csv")
    df.to_csv(out_path, index=False)
    print(f"  -> Saved {len(df)} actuals to {out_path}")

def ingest_forecasts():
    print("\n--- Ingesting Forecasts (WINDFOR) ---")
    # We fetch publish times starting late Dec to cover early Jan forecasts
    start_date = pd.to_datetime("2025-12-25")
    end_date = pd.to_datetime("2026-01-31")
    
    all_data = []
    current = start_date
    while current <= end_date:
        next_date = current + timedelta(days=2) 
        print(f"  Fetching forecasts published {current.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}...")
        params = {
            "publishDateTimeFrom": current.strftime("%Y-%m-%dT00:00:00Z"),
            "publishDateTimeTo": next_date.strftime("%Y-%m-%dT23:59:59Z")
        }
        data = fetch_with_retry(f"{BASE_URL}/WINDFOR/stream", params)
        all_data.extend(data)
        current = next_date + timedelta(days=1)
        
    df = pd.DataFrame(all_data)
    if df.empty:
        print("  No forecasts found!")
        return
        
    df["startTime"] = pd.to_datetime(df["startTime"], format='ISO8601')
    df["publishTime"] = pd.to_datetime(df["publishTime"], format='ISO8601')
    
    # Calculate forecast horizon in hours
    df["horizon_h"] = (df["startTime"] - df["publishTime"]).dt.total_seconds() / 3600.0
    
    df = df[["startTime", "publishTime", "generation", "horizon_h"]]
    df.rename(columns={
        "startTime": "start_time_utc",
        "publishTime": "publish_time_utc",
        "generation": "forecast_mw"
    }, inplace=True)
    
    # Filter to only keep targets relevant to our date range (Jan 1 to Feb 2)
    target_start = pd.to_datetime("2026-01-01", utc=True)
    target_end = pd.to_datetime("2026-02-02", utc=True)
    df = df[(df["start_time_utc"] >= target_start) & (df["start_time_utc"] <= target_end)]
    
    # Deduplicate and sort
    df.drop_duplicates(subset=["start_time_utc", "publish_time_utc"], inplace=True)
    df.sort_values(["start_time_utc", "publish_time_utc"], inplace=True)
    
    out_path = os.path.join(DATA_DIR, "forecasts.csv")
    df.to_csv(out_path, index=False)
    print(f"  -> Saved {len(df)} forecasts to {out_path}")
    print(f"  -> Max horizon found: {df['horizon_h'].max():.1f} hours")

if __name__ == "__main__":
    ingest_actuals()
    ingest_forecasts()
    print("\nData ingestion complete! Ready for backend setup.")
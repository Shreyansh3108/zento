import requests
import json

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"

def verify_actuals():
    print("--- Fetching Actuals (FUELHH) ---")
    url = f"{BASE_URL}/FUELHH/stream"
    
    params = {
        "settlementDateFrom": "2024-01-02",
        "settlementDateTo": "2024-01-02",
        "fuelType": "WIND"
    }
    
    try:
        res = requests.get(url, params=params)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Total records returned: {len(data)}")
            if data:
                print("First record sample:")
                print(json.dumps(data[0], indent=2))
        else:
            print("Error Response:", res.text)
    except Exception as e:
        print(f"Failed to fetch actuals: {e}")

def verify_forecasts():
    print("\n--- Fetching Forecasts (WINDFOR) ---")
    url = f"{BASE_URL}/WINDFOR/stream"
    
    params = {
        "publishDateTimeFrom": "2024-01-01T00:00:00Z",
        "publishDateTimeTo": "2024-01-02T00:00:00Z"
    }
    
    try:
        res = requests.get(url, params=params)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Total records returned: {len(data)}")
            if data:
                print("First record sample:")
                print(json.dumps(data[0], indent=2))
        else:
            print("Error Response:", res.text)
    except Exception as e:
        print(f"Failed to fetch forecasts: {e}")

if __name__ == "__main__":
    print("Verifying Elexon BMRS API endpoints...")
    verify_actuals()
    verify_forecasts()
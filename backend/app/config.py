import os
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ACTUALS_PATH = os.path.join(DATA_DIR, "actuals.csv")
FORECASTS_PATH = os.path.join(DATA_DIR, "forecasts.csv")

DEFAULT_CUTOFF = "09:00"
TZ_LONDON = ZoneInfo("Europe/London")
TZ_UTC = ZoneInfo("UTC")
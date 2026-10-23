import pytest
from datetime import date
from backend.app.services.selection import get_decision_data
import pandas as pd

def test_no_data_leakage():
    # Set a strict cutoff of 09:00 on D-1
    delivery = date(2026, 1, 5)
    df, metadata = get_decision_data(delivery, "09:00")
    
    cutoff_datetime = pd.to_datetime(metadata["cutoff_applied_utc"])
    
    # Assert that NO forecast in the resulting dataframe was published after the cutoff
    assert (df["publish_time_utc"] <= cutoff_datetime).all(), "CRITICAL: Look-ahead data leakage detected!"

def test_mwh_conversion():
    delivery = date(2026, 1, 5)
    df, metadata = get_decision_data(delivery, "09:00")
    
    # Verify the sum * 0.5 logic
    expected_mwh = df["forecast_mw"].sum() * 0.5
    assert metadata["total_forecast_mwh"] == expected_mwh, "MWh calculation error"
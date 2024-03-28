import pandas as pd

def query(calendar_data):
    today_start = pd.to_datetime("2024-03-12 00:00:00-00:00")
    today_end = pd.to_datetime("2024-03-12 23:59:59-00:00")
    calendar_data["start"] = pd.to_datetime(calendar_data["start"])
    calendar_data["end"] = pd.to_datetime(calendar_data["end"])
    return len(calendar_data.loc[(calendar_data["start"] >= today_start) & (calendar_data["end"] <= today_end)])
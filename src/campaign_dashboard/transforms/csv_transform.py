"""Normalize accepted CSV values into the reporting format."""
import pandas as pd

COLUMNS = ["date", "campaign_id", "campaign_name", "channel", "spend", "clicks", "purchases", "revenue"]
NUMERIC = ["spend", "clicks", "purchases", "revenue"]


def normalize_csv(raw):
    data = raw.copy()
    data.columns = [str(column).strip() for column in data.columns]
    missing = set(COLUMNS) - set(data.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    if data.columns.duplicated().any():
        raise ValueError("Column names must be unique after trimming whitespace.")
    data = data[COLUMNS].copy()
    for column in ["campaign_id", "campaign_name", "channel"]:
        data[column] = data[column].astype("string").str.strip()
    date_strings = data["date"].astype("string")
    valid_format = date_strings.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False)
    data["date"] = pd.to_datetime(date_strings.where(valid_format), format="%Y-%m-%d", errors="coerce")
    for column in NUMERIC:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    return data

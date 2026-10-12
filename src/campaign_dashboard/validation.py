"""Validate daily records before they reach dashboard calculations."""
import numpy as np
from .transforms.csv_transform import NUMERIC


def validate(data):
    errors = []
    if data.empty:
        return ["The CSV contains no data rows."]
    if data["date"].isna().any():
        errors.append("Dates must be valid calendar dates in YYYY-MM-DD format.")
    for column in ["campaign_id", "campaign_name", "channel"]:
        if (data[column].isna() | data[column].eq("")).any():
            errors.append(f"{column} must be populated on every row.")
    for column in NUMERIC:
        values = data[column]
        if (values.isna() | ~np.isfinite(values) | values.lt(0)).any():
            errors.append(f"{column} must contain finite, nonnegative numbers on every row.")
    for column in ["clicks", "purchases"]:
        if data[column].dropna().mod(1).ne(0).any():
            errors.append(f"{column} must contain whole numbers.")
    if data.duplicated(["date", "campaign_id", "channel"]).any():
        errors.append("Only one row per date, campaign_id, and channel is allowed.")
    if data.groupby("campaign_id")["campaign_name"].nunique().gt(1).any():
        errors.append("Each campaign_id must have one consistent campaign_name.")
    return errors

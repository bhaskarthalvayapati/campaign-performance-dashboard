"""First-touch attribution for the auditable synthetic supporting records."""
import pandas as pd


def attribute_first_touch(opportunities, touches):
    won = opportunities.loc[opportunities["stage"].eq("Closed Won")].copy()
    won["close_date"] = pd.to_datetime(won["close_date"])
    joined = touches.merge(won, on="opportunity_id", validate="many_to_one")
    joined["touch_timestamp"] = pd.to_datetime(joined["touch_timestamp"])
    # Touches on the close date are eligible; the reporting input has day precision.
    joined = joined.loc[joined["touch_timestamp"].dt.normalize().le(joined["close_date"])]
    # Equal timestamps use touch_id as a deterministic synthetic-data tie-breaker.
    first = joined.sort_values(["touch_timestamp", "touch_id"]).drop_duplicates("opportunity_id")
    first = first.rename(columns={"close_date": "date", "amount": "revenue"})
    first["purchases"] = 1
    return first[["opportunity_id", "date", "campaign_id", "channel", "purchases", "revenue"]]

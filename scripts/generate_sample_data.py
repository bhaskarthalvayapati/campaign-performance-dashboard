"""Generate four distinct monthly scenarios with auditable first-touch outcomes."""
from pathlib import Path
import sys
import random
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from campaign_dashboard.transforms.attribution import attribute_first_touch

MONTHS = (6, 7, 8, 9)
CAMPAIGNS = {"C001": "Autumn Launch", "C002": "Customer Winback", "C003": "Product Discovery"}
PAIRS = [("C001", "Meta"), ("C001", "LinkedIn"), ("C002", "Email"), ("C003", "YouTube"), ("C003", "Meta")]
# Different budgets, deal sizes, win rates, and channel mixes create visible changes.
PROFILES = {
    6: dict(opportunities=110, wins=45, budget=0.65, cpc=1.0, deal=0.8, weights=[4, 1, 2, 1, 0]),
    7: dict(opportunities=210, wins=125, budget=1.25, cpc=0.8, deal=1.1, weights=[6, 2, 1, 2, 2]),
    8: dict(opportunities=190, wins=62, budget=1.4, cpc=1.5, deal=0.75, weights=[1, 1, 1, 6, 0]),
    9: dict(opportunities=260, wins=188, budget=1.0, cpc=0.85, deal=1.3, weights=[2, 1, 7, 1, 2]),
}
BASE_SPEND = {"Meta": 100, "LinkedIn": 160, "Email": 22, "YouTube": 130}
BASE_CPC = {"Meta": 0.75, "LinkedIn": 2.4, "Email": 0.18, "YouTube": 0.95}


def active(month, pair, date):
    if month == 6:
        return [True, date.day <= 15 and date.weekday() < 5,
                date.weekday() in (0, 2, 4), date.day >= 12, False][pair]
    if month == 7:
        return pair < 4 or 7 <= date.day <= 27
    if month == 8:
        return [date.day <= 20, date.weekday() < 5,
                date.weekday() in (2, 4), date.day >= 10, False][pair]
    return pair < 4 or date.day >= 16


def pulse(month, day):
    if month == 6:
        return 0.8 + day / 75
    if month == 7:
        return 1.8 if 8 <= day <= 17 else 1.0
    if month == 8:
        return 1.2 if day <= 14 else 0.7
    return 0.85 if day <= 15 else 1.45


def generate_month(month):
    rng = random.Random(202600 + month)
    profile = PROFILES[month]
    prefix = "" if month == 9 else f"2026{month:02d}-"
    start = pd.Timestamp(year=2026, month=month, day=1)
    dates = pd.date_range(start, start + pd.offsets.MonthEnd(0))
    activity, available = [], {}
    for pair_index, (campaign, channel) in enumerate(PAIRS):
        available[pair_index] = [date for date in dates if active(month, pair_index, date)]
        for date in available[pair_index]:
            weekend = 0.8 if date.weekday() >= 5 else 1.0
            spend = round(BASE_SPEND[channel] * profile["budget"] * pulse(month, date.day)
                          * weekend * rng.uniform(0.8, 1.2), 2)
            clicks = max(1, round(spend / (BASE_CPC[channel] * profile["cpc"] * rng.uniform(0.8, 1.2))))
            activity.append(dict(date=date, campaign_id=campaign, campaign_name=CAMPAIGNS[campaign],
                                 channel=channel, spend=spend, clicks=clicks))
    opportunities, touches = [], []
    stages = ["Closed Won"] * profile["wins"] + ["Closed Lost"] * (profile["opportunities"] - profile["wins"])
    rng.shuffle(stages)
    for index, stage in enumerate(stages, start=1):
        opportunity_id = f"O{prefix}{index:04d}"
        pair_index = rng.choices(range(len(PAIRS)), weights=profile["weights"])[0]
        campaign, channel = PAIRS[pair_index]
        # Closing-day row and first-touch row both exist even for intermittent campaigns.
        close_date = rng.choices(available[pair_index], weights=[pulse(month, date.day) for date in available[pair_index]])[0]
        first_candidates = [date for date in available[pair_index] if close_date - pd.Timedelta(days=7) <= date <= close_date]
        first_date = rng.choice(first_candidates)
        opportunities.append(dict(opportunity_id=opportunity_id,
                                  amount=round(rng.choice([100, 250, 500, 750, 1000]) * profile["deal"], 2),
                                  stage=stage, close_date=close_date.strftime("%Y-%m-%d")))
        touches.append(dict(touch_id=f"T{prefix}{index:04d}-0", opportunity_id=opportunity_id,
                            campaign_id=campaign, channel=channel,
                            touch_timestamp=(first_date + pd.Timedelta(hours=9)).isoformat()))
        later = [(other_campaign, other_channel, date) for other_index, (other_campaign, other_channel) in enumerate(PAIRS)
                 for date in available[other_index] if first_date <= date <= close_date]
        for offset in range(1, rng.choice([2, 2, 3])):
            other_campaign, other_channel, date = rng.choice(later)
            touches.append(dict(touch_id=f"T{prefix}{index:04d}-{offset}", opportunity_id=opportunity_id,
                                campaign_id=other_campaign, channel=other_channel,
                                touch_timestamp=(date + pd.Timedelta(hours=12 + offset)).isoformat()))
    opp, touch = pd.DataFrame(opportunities), pd.DataFrame(touches)
    attributed = attribute_first_touch(opp, touch)
    summary = attributed.groupby(["date", "campaign_id", "channel"], as_index=False)[["purchases", "revenue"]].sum()
    performance = pd.DataFrame(activity).merge(summary, on=["date", "campaign_id", "channel"], how="left")
    performance[["purchases", "revenue"]] = performance[["purchases", "revenue"]].fillna(0)
    performance["purchases"] = performance["purchases"].astype(int)
    performance = performance.sort_values(["date", "campaign_id", "channel"]).reset_index(drop=True)
    return performance, opp, touch


def main():
    output = ROOT / "data"
    output.mkdir(exist_ok=True)
    kinds = ("campaign_performance", "opportunities", "campaign_touches")
    combined = {kind: [] for kind in kinds}
    for month in MONTHS:
        for kind, records in zip(kinds, generate_month(month)):
            records.to_csv(output / f"sample_{kind}_2026_{month:02d}.csv", index=False, date_format="%Y-%m-%d")
            combined[kind].append(records)
            if month == 9:
                records.to_csv(output / f"sample_{kind}.csv", index=False, date_format="%Y-%m-%d")
    for kind, frames in combined.items():
        pd.concat(frames, ignore_index=True).to_csv(
            output / f"sample_{kind}_2026_06_to_09.csv", index=False, date_format="%Y-%m-%d")


if __name__ == "__main__":
    main()

import sys
import unittest
from pathlib import Path
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from campaign_dashboard.sources.csv_source import read_csv
from campaign_dashboard.transforms.csv_transform import normalize_csv
from campaign_dashboard.transforms.attribution import attribute_first_touch
from campaign_dashboard.validation import validate
from campaign_dashboard.metrics import totals, summarize, filter_data


class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.data = normalize_csv(read_csv(ROOT / "data/sample_campaign_performance.csv"))

    def test_sample_schema(self):
        self.assertEqual(validate(self.data), [])
        self.assertEqual(len(self.data), 135)

    def test_four_month_data_and_attribution(self):
        monthly = []
        for month, days, rows in [(6, 30, 73), (7, 31, 145), (8, 31, 71), (9, 30, 135)]:
            data = normalize_csv(read_csv(ROOT / f"data/sample_campaign_performance_2026_{month:02d}.csv"))
            self.assertEqual(validate(data), [])
            self.assertEqual(len(data), rows)
            self.assertEqual(set(data["date"].dt.month), {month})
            self.assertEqual(data["date"].nunique(), days)
            monthly.append(data)
        combined = normalize_csv(read_csv(ROOT / "data/sample_campaign_performance_2026_06_to_09.csv"))
        self.assertEqual(validate(combined), [])
        pd.testing.assert_frame_equal(combined, pd.concat(monthly, ignore_index=True))
        self.assertEqual(combined["date"].min(), pd.Timestamp("2026-06-01"))
        self.assertEqual(combined["date"].max(), pd.Timestamp("2026-09-30"))
        opp = pd.read_csv(ROOT / "data/sample_opportunities_2026_06_to_09.csv")
        touch = pd.read_csv(ROOT / "data/sample_campaign_touches_2026_06_to_09.csv")
        self.assertTrue(opp["opportunity_id"].is_unique)
        self.assertTrue(touch["touch_id"].is_unique)
        self.assertTrue(touch["opportunity_id"].isin(opp["opportunity_id"]).all())
        expected = attribute_first_touch(opp, touch).groupby(["date", "campaign_id", "channel"])[["purchases", "revenue"]].sum()
        actual = combined.set_index(["date", "campaign_id", "channel"])[["purchases", "revenue"]]
        expected = expected.reindex(actual.index, fill_value=0)
        pd.testing.assert_frame_equal(actual, expected, check_dtype=False)
        self.assertEqual(combined["purchases"].sum(), 420)

    def test_months_have_visible_performance_and_volume_variation(self):
        months = {month: normalize_csv(read_csv(ROOT / f"data/sample_campaign_performance_2026_{month:02d}.csv"))
                  for month in (6, 7, 8, 9)}
        summaries = {month: totals(data) for month, data in months.items()}
        self.assertEqual(len({len(data) for data in months.values()}), 4)
        for metric in ["spend", "clicks", "purchases", "revenue", "roas"]:
            self.assertEqual(len({round(value[metric], 2) for value in summaries.values()}), 4)
        self.assertGreater(summaries[7]["clicks"], 2 * summaries[6]["clicks"])
        self.assertLess(summaries[8]["roas"], summaries[7]["roas"])
        self.assertGreater(summaries[9]["roas"], summaries[8]["roas"])
        for month, leader in [(7, "Meta"), (8, "YouTube"), (9, "Email")]:
            self.assertEqual(months[month].groupby("channel")["purchases"].sum().idxmax(), leader)
        self.assertTrue(months[6].groupby(["campaign_id", "channel"]).size().lt(30).any())

    def test_invalid_records(self):
        invalid = self.data.copy()
        invalid["clicks"] = invalid["clicks"].astype(float)
        invalid.loc[0, "spend"] = float("inf")
        invalid.loc[1, "clicks"] = 1.5
        invalid.loc[2, "date"] = pd.NaT
        invalid = pd.concat([invalid, invalid.iloc[[3]]], ignore_index=True)
        errors = validate(invalid)
        self.assertTrue(any("finite" in error for error in errors))
        self.assertTrue(any("whole" in error for error in errors))
        self.assertTrue(any("Dates" in error for error in errors))
        self.assertTrue(any("Only one" in error for error in errors))

    def test_missing_columns_and_bad_date(self):
        with self.assertRaises(ValueError):
            normalize_csv(pd.DataFrame({"date": ["2026-09-01"]}))
        raw = self.data.copy()
        raw["date"] = "09/01/2026"
        self.assertTrue(validate(normalize_csv(raw)))
        with self.assertRaises(ValueError):
            read_csv(StringIO(""))

    def test_weighted_ratios_and_zero_denominators(self):
        data = pd.DataFrame([dict(channel="Meta", spend=100, clicks=10, purchases=1, revenue=200),
                             dict(channel="Meta", spend=100, clicks=90, purchases=9, revenue=800)])
        self.assertEqual(totals(data)["cpc"], 2)
        self.assertEqual(summarize(data, ["channel"]).iloc[0]["roas"], 5)
        self.assertIsNone(totals(data.assign(spend=0))["roas"])
        self.assertIsNone(totals(data.assign(purchases=0))["cost_per_purchase"])

    def test_filters(self):
        result = filter_data(self.data, "2026-09-01", "2026-09-02", ["C001"], ["Meta"])
        self.assertEqual(len(result), 2)
        self.assertTrue(filter_data(self.data, "2026-09-01", "2026-09-30", [], ["Meta"]).empty)

    def test_first_touch_and_closed_won_only(self):
        opportunities = pd.DataFrame([
            dict(opportunity_id="O1", amount=500, stage="Closed Won", close_date="2026-09-10"),
            dict(opportunity_id="O2", amount=900, stage="Closed Lost", close_date="2026-09-10")])
        touches = pd.DataFrame([
            dict(touch_id="T2", opportunity_id="O1", campaign_id="C002", channel="Email", touch_timestamp="2026-09-05T09:00:00"),
            dict(touch_id="T1", opportunity_id="O1", campaign_id="C001", channel="Meta", touch_timestamp="2026-09-01T09:00:00"),
            dict(touch_id="T3", opportunity_id="O2", campaign_id="C002", channel="Email", touch_timestamp="2026-09-01T09:00:00"),
            dict(touch_id="T4", opportunity_id="O1", campaign_id="C003", channel="YouTube", touch_timestamp="2026-09-11T09:00:00")])
        result = attribute_first_touch(opportunities, touches)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["campaign_id"], "C001")
        self.assertEqual(result.iloc[0]["date"], pd.Timestamp("2026-09-10"))
        self.assertEqual(result.iloc[0]["revenue"], 500)

    def test_supporting_records_reconcile(self):
        opportunities = pd.read_csv(ROOT / "data/sample_opportunities.csv")
        touches = pd.read_csv(ROOT / "data/sample_campaign_touches.csv")
        expected = attribute_first_touch(opportunities, touches)
        grouped = expected.groupby(["date", "campaign_id", "channel"], as_index=False)[["purchases", "revenue"]].sum()
        actual = self.data.merge(grouped, on=["date", "campaign_id", "channel"], how="left", suffixes=("", "_expected")).fillna(0)
        for column in ["purchases", "revenue"]:
            self.assertTrue(actual[column].eq(actual[column + "_expected"]).all())
        self.assertEqual(self.data["purchases"].sum(), len(opportunities.query('stage == "Closed Won"')))


if __name__ == "__main__":
    unittest.main()

import unittest
from io import BytesIO
from unittest.mock import patch
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def test_sample_and_filters(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 7)
        self.assertEqual(app.metric[2].value, "420")
        app.multiselect[1].set_value(["Meta"]).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe), 3)
        self.assertEqual(set(app.dataframe[2].value["channel"]), {"Meta"})
        app.multiselect[0].set_value([]).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("No records" in info.value for info in app.info))

    def test_monthly_sample_selection(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertEqual(len(app.dataframe[2].value), 424)
        for month, rows, purchases in [("June", 73, 45), ("July", 145, 125), ("August", 71, 62), ("September", 135, 188)]:
            app.selectbox[0].set_value(f"{month} 2026").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.dataframe[2].value), rows)
            self.assertEqual(app.metric[2].value, str(purchases))

    def test_upload_prompt(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        app.radio[0].set_value("Upload CSV").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Upload a CSV" in info.value for info in app.info))

    def test_valid_and_invalid_csv_upload(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        sample = (ROOT / "data/sample_campaign_performance_2026_06_to_09.csv").read_bytes()
        with patch("streamlit.delta_generator.DeltaGenerator.file_uploader", return_value=BytesIO(sample)):
            app.radio[0].set_value("Upload CSV").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[2].value, "420")
        with patch("streamlit.delta_generator.DeltaGenerator.file_uploader", return_value=BytesIO(b"date,spend\n2026-09-01,10\n")):
            app.run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Missing required columns" in error.value for error in app.error))


if __name__ == "__main__":
    unittest.main()

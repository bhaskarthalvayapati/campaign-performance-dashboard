"""Local Streamlit entry point."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st
from campaign_dashboard.sources.csv_source import read_csv
from campaign_dashboard.transforms.csv_transform import normalize_csv
from campaign_dashboard.validation import validate
from campaign_dashboard.ui.filters import render_filters
from campaign_dashboard.ui.dashboard import render_dashboard
from campaign_dashboard.ui.styles import apply_styles, heading

st.set_page_config(page_title="Campaign Performance", page_icon="📊", layout="wide")
palette = apply_styles()
heading("Campaign Performance", tone="blue", level=1)
st.caption("Week 01 · Daily channel reporting · First-touch attribution · USD")
heading("Data source", tone="amber", container=st.sidebar)
mode = st.sidebar.radio("Choose data", ["Sample dataset", "Upload CSV"])
upload = st.sidebar.file_uploader("Campaign performance CSV", type=["csv"]) if mode == "Upload CSV" else None
if mode == "Upload CSV" and upload is None:
    st.info("Upload a CSV with date, campaign_id, campaign_name, channel, spend, clicks, purchases, and revenue.")
    st.stop()
if mode == "Sample dataset":
    sample_files = {
        "June–September 2026 (all four months)": "sample_campaign_performance_2026_06_to_09.csv",
        "June 2026": "sample_campaign_performance_2026_06.csv",
        "July 2026": "sample_campaign_performance_2026_07.csv",
        "August 2026": "sample_campaign_performance_2026_08.csv",
        "September 2026": "sample_campaign_performance_2026_09.csv",
    }
    selected = st.sidebar.selectbox("Sample period", list(sample_files))
    source = ROOT / "data" / sample_files[selected]
    st.sidebar.download_button("Download sample CSV", source.read_bytes(),
                               file_name=source.name, mime="text/csv", icon=":material/download:",
                               type="secondary", width="stretch", on_click="ignore",
                               help="Download the selected month or all four months.")
else:
    source = upload
try:
    data = normalize_csv(read_csv(source))
except (ValueError, OSError) as exc:
    st.error(str(exc))
    st.stop()
errors = validate(data)
if errors:
    st.error("Please correct the CSV before continuing.")
    for error in errors:
        st.write(f"• {error}")
    st.stop()
st.sidebar.caption(f"{len(data):,} daily records loaded. Data stays in this local session; uploads are not saved.")
# Different datasets get independent filter widget state.
import hashlib
signature = hashlib.sha256(data.to_csv(index=False).encode()).hexdigest()
render_dashboard(render_filters(data, signature), palette)

import streamlit as st
from ..metrics import filter_data
from .styles import heading


def render_filters(data, signature):
    heading("Filters", tone="teal", container=st.sidebar)
    earliest, latest = data["date"].min().date(), data["date"].max().date()
    dates = st.sidebar.date_input("Date range", value=(earliest, latest), min_value=earliest, max_value=latest, key=f"dates_{signature}")
    names = data.drop_duplicates("campaign_id").set_index("campaign_id")["campaign_name"].to_dict()
    campaigns = st.sidebar.multiselect("Campaigns", list(names), default=list(names),
                                      format_func=lambda key: f"{names[key]} ({key})", key=f"campaigns_{signature}")
    channels = sorted(data["channel"].unique().tolist())
    selected_channels = st.sidebar.multiselect("Channels", channels, default=channels, key=f"channels_{signature}")
    if len(dates) != 2:
        st.info("Select both a start date and an end date.")
        st.stop()
    return filter_data(data, dates[0], dates[1], campaigns, selected_channels)

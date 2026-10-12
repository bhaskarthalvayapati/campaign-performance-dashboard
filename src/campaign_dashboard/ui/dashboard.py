import streamlit as st
from ..metrics import totals, summarize
from ..charts import daily_chart, channel_chart
from .styles import heading


def money(value):
    return "N/A" if value is None else f"${value:,.2f}"


def render_dashboard(data, palette):
    if data.empty:
        st.info("No records match these filters. Expand the date range or select campaigns and channels.")
        return
    values = totals(data)
    cards = st.columns(4)
    for card, label, value in zip(cards, ["Spend", "Clicks", "Purchases", "Attributed revenue"],
                                  [money(values["spend"]), f'{values["clicks"]:,.0f}',
                                   f'{values["purchases"]:,.0f}', money(values["revenue"])]):
        card.metric(label, value)
    cards = st.columns(3)
    for card, label, value in zip(cards, ["Cost per click", "Cost per purchase", "ROAS"],
                                  [money(values["cpc"]), money(values["cost_per_purchase"]),
                                   "N/A" if values["roas"] is None else f'{values["roas"]:.2f}×']):
        card.metric(label, value)
    daily = summarize(data, ["date"])
    channels = summarize(data, ["channel"])
    st.plotly_chart(daily_chart(daily, title_color=palette["blue"]), use_container_width=True)
    st.plotly_chart(channel_chart(channels, title_color=palette["teal"]), use_container_width=True)
    heading("Channel comparison", tone="teal")
    st.dataframe(channels, hide_index=True, width="stretch")
    heading("Campaign comparison", tone="purple")
    st.dataframe(summarize(data, ["campaign_id", "campaign_name"]), hide_index=True, width="stretch")
    with st.expander("Metric definitions"):
        st.markdown("Cost per click = spend ÷ clicks. Cost per purchase = spend ÷ purchases. "
                    "ROAS = attributed revenue ÷ spend. Undefined ratios display N/A. "
                    "Purchases and revenue are recorded on the Closed Won opportunity's close date "
                    "and assigned entirely to its earliest eligible campaign touch. "
                    "Spend and clicks reflect activity on each row's date. Uploaded aggregates cannot "
                    "independently prove attribution. All monetary values must use USD for V1.")
    display = data.sort_values(["date", "campaign_id", "channel"]).copy()
    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    with st.container(key="records_toolbar"):
        title, action = st.columns([3, 2], vertical_alignment="center")
        heading("Daily records", tone="muted", container=title)
        action.download_button("Export filtered CSV", display.to_csv(index=False),
                               file_name="filtered_campaign_performance.csv", mime="text/csv",
                               icon=":material/download:", type="primary", width="stretch",
                               on_click="ignore", help="Export only the records matching your current filters.")
    st.caption(f"{len(display):,} records match your filters.")
    st.dataframe(display, hide_index=True, width="stretch")

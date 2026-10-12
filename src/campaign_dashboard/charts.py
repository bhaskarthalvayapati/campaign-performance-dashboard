"""Build figures from prepared reporting data."""
import plotly.express as px


def daily_chart(daily, title_color="#2455A4"):
    long = daily.melt(id_vars="date", value_vars=["spend", "revenue"], var_name="Metric", value_name="Amount (USD)")
    figure = px.line(long, x="date", y="Amount (USD)", color="Metric", markers=True,
                   title="Daily spend and attributed revenue", template="plotly_white")
    figure.update_layout(title_font_color=title_color)
    return figure


def channel_chart(channels, title_color="#087F78"):
    figure = px.bar(channels, x="channel", y="purchases", color="channel",
                  title="First-touch purchases by channel", template="plotly_white")
    figure.update_layout(title_font_color=title_color)
    return figure

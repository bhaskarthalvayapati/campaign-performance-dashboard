"""Centralized, theme-aware colors for dashboard headings and labels."""
from html import escape
import streamlit as st

PALETTES = {
    "light": {
        "blue": "#2455A4", "teal": "#087F78", "purple": "#7047A3",
        "amber": "#946012", "muted": "#465A72",
        "button_text": "#FFFFFF", "button_hover": "#1C4383", "button_surface": "#EDF3FC",
    },
    "dark": {
        "blue": "#92B9FF", "teal": "#76D7CA", "purple": "#C4AFF5",
        "amber": "#EAC17B", "muted": "#B3C4DA",
        "button_text": "#12233C", "button_hover": "#B1CDFF", "button_surface": "#1D2B42",
    },
}


def apply_styles():
    palette = PALETTES.get(st.context.theme.type, PALETTES["light"])
    st.html(f"""
    <style>
        .campaign-heading {{ line-height: 1.3; letter-spacing: -0.015em; }}
        h1.campaign-heading {{ font-weight: 750; padding: 0.5rem 0 0.8rem; }}
        h2.campaign-heading {{ font-size: 1.5rem; padding: 1.3rem 0 0.7rem; }}
        [data-testid="stSidebar"] h2.campaign-heading {{
            font-size: 1.35rem; padding: 0.8rem 0 0.7rem;
        }}
        [data-testid="stMetricLabel"] p {{ color: {palette['teal']}; font-weight: 600; }}
        [data-testid="stWidgetLabel"] p {{ color: {palette['muted']}; font-weight: 600; }}
        [data-testid="stExpander"] summary p {{ color: {palette['purple']}; font-weight: 600; }}
        [data-testid="stDownloadButton"] button,
        [data-testid="stFileUploader"] button {{
            min-height: 2.8rem;
            padding: 0.65rem 1rem;
            border-radius: 0.75rem;
            font-weight: 600;
            transition: background-color 150ms ease, box-shadow 150ms ease;
        }}
        [data-testid="stDownloadButton"] button p,
        [data-testid="stFileUploader"] button p {{ font-weight: 600; }}
        [data-testid="stDownloadButton"] button[kind="primary"] {{
            background: {palette['blue']};
            color: {palette['button_text']};
            border: 1px solid {palette['blue']};
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
        }}
        [data-testid="stDownloadButton"] button[kind="primary"]:hover:not(:disabled) {{
            background: {palette['button_hover']};
            border-color: {palette['button_hover']};
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.18);
        }}
        [data-testid="stDownloadButton"] button[kind="secondary"],
        [data-testid="stFileUploader"] button {{
            color: {palette['blue']};
            background: transparent;
            border: 1px solid {palette['blue']};
        }}
        [data-testid="stDownloadButton"] button[kind="secondary"]:hover:not(:disabled),
        [data-testid="stFileUploader"] button:hover:not(:disabled) {{
            background: {palette['button_surface']};
            color: {palette['blue']};
            border-color: {palette['blue']};
        }}
        [data-testid="stDownloadButton"] button:focus-visible,
        [data-testid="stFileUploader"] button:focus-visible {{
            outline: 3px solid {palette['teal']};
            outline-offset: 3px;
        }}
        [data-testid="stDownloadButton"] button:disabled,
        [data-testid="stFileUploader"] button:disabled {{ opacity: 0.5; box-shadow: none; }}
        .st-key-records_toolbar h2.campaign-heading {{ padding: 0; margin: 0; }}
        @media (prefers-reduced-motion: reduce) {{
            [data-testid="stDownloadButton"] button,
            [data-testid="stFileUploader"] button {{ transition: none; }}
        }}
    </style>
    """)
    return palette


def heading(text, tone="teal", level=2, container=None):
    palette = PALETTES.get(st.context.theme.type, PALETTES["light"])
    target = st if container is None else container
    target.markdown(
        f'<h{level} class="campaign-heading" style="color: {palette[tone]}">{escape(text)}</h{level}>',
        unsafe_allow_html=True,
    )

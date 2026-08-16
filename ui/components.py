"""
components.py

Small, reusable pieces of Streamlit UI that get used on more than one
screen (e.g. a coloured priority badge, a metric card). Keeping these
in one place avoids repeating the same HTML/CSS snippet in several
files.
"""

import streamlit as st

PRIORITY_COLORS = {
    "High": "#D64545",
    "Medium": "#E2A030",
    "Low": "#5B8A72",
}

STATUS_COLORS = {
    "Measurable": "#2E7D5B",
    "Gap": "#B23B3B",
}


def priority_badge(priority):
    """Render a small coloured badge for a priority level."""
    color = PRIORITY_COLORS.get(priority, "#888888")
    st.markdown(
        f"""<span style="background-color:{color}22; color:{color};
        border:1px solid {color}; padding:2px 10px; border-radius:12px;
        font-size:0.8rem; font-weight:600;">{priority} priority</span>""",
        unsafe_allow_html=True,
    )


def status_badge(status_text):
    """Render 'Measurable' or 'Gap' as a coloured badge."""
    color = STATUS_COLORS.get(status_text, "#888888")
    st.markdown(
        f"""<span style="background-color:{color}22; color:{color};
        border:1px solid {color}; padding:2px 10px; border-radius:12px;
        font-size:0.8rem; font-weight:600;">{status_text}</span>""",
        unsafe_allow_html=True,
    )


def section_header(title, subtitle=None):
    """A consistent section heading style used across dashboard screens."""
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def metric_card(label, value, help_text=None):
    """Thin wrapper around st.metric for visual consistency."""
    st.metric(label=label, value=value, help=help_text)


def prototype_banner():
    """Small reminder banner shown on most screens."""
    st.markdown(
        """<div style="background-color:#EFF3FA; border-left:4px solid #4A6FA5;
        padding:8px 14px; border-radius:4px; font-size:0.85rem; color:#33475B;
        margin-bottom:1rem;">
        Prototype / Concept Demonstration &mdash; all data shown is synthetic and fictional.
        </div>""",
        unsafe_allow_html=True,
    )

"""
app.py

The entry point for the Streamlit application. Run with:
    streamlit run app.py

This file is intentionally thin: it just sets up the page, manages
which "screen" is currently showing (using st.session_state, since
Streamlit re-runs this whole script on every button click), and calls
into the relevant ui/ module to render that screen.

The actual analysis logic lives in engine/, and each screen's layout
lives in its own file under ui/, so this file stays easy to scan.
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # loads OPENAI_API_KEY from .env if present; harmless if not

from ui import journey_builder, upload, dashboard, gaps
from ui.components import prototype_banner

st.set_page_config(
    page_title="Journey Measurement Analyzer",
    page_icon="📊",
    layout="wide",
)

if "screen" not in st.session_state:
    st.session_state.screen = "home"


def render_home():
    prototype_banner()
    st.title("Journey Measurement Analyzer")
    st.subheader("Understand what you can measure today and identify the data gaps preventing deeper journey measurement.")

    st.markdown(
        "Define a customer journey, upload the data currently available, and assess your "
        "current measurement capability."
    )

    if st.button("Create New Journey", type="primary"):
        st.session_state.screen = "journey"
        st.rerun()

    st.divider()
    st.markdown("#### How it works")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**1. Define**  \nDescribe your customer journey and its stages.")
    with col2:
        st.markdown("**2. Upload**  \nUpload the event data you currently collect.")
    with col3:
        st.markdown("**3. Analyze**  \nSee what's measurable, and what isn't.")
    with col4:
        st.markdown("**4. Improve**  \nGet concrete recommendations for closing gaps.")

    st.divider()
    _render_future_enterprise_section()


def _render_future_enterprise_section():
    st.markdown("#### Future Enterprise Capabilities")
    st.caption("Conceptual only — these are not implemented in this prototype.")
    future_cards = [
        "Enterprise data integrations", "Real-time data pipelines", "Multiple journey types",
        "Cross-channel journey analysis", "Customer segmentation", "Historical journey comparison",
        "AI-assisted measurement recommendations", "Data governance", "Role-based access",
        "Enterprise reporting", "Journey repository",
    ]
    cols = st.columns(3)
    for index, card in enumerate(future_cards):
        with cols[index % 3]:
            st.markdown(
                f"""<div style="border:1px dashed #B7C4D6; border-radius:6px; padding:10px 14px;
                margin-bottom:10px; color:#5A6B80; font-size:0.9rem;">{card}</div>""",
                unsafe_allow_html=True,
            )


def render_navigation_sidebar():
    """A simple sidebar showing the workflow and allowing backward navigation."""
    with st.sidebar:
        st.markdown("### Journey Measurement Analyzer")
        st.caption("Prototype / Concept Demonstration")
        st.divider()

        steps = [
            ("home", "Home"),
            ("journey", "Define Journey"),
            ("upload", "Upload Data"),
            ("dashboard", "Measurement Dashboard"),
            ("gaps", "Measurement Gaps"),
        ]
        current = st.session_state.screen
        for key, label in steps:
            is_current = (key == current)
            # Only allow jumping forward if the underlying data for that
            # screen already exists in session_state, so users can't skip
            # ahead to a screen that has nothing to show yet.
            can_visit = key in ("home", "journey") or (
                key == "upload" and "journey" in st.session_state
            ) or (
                key in ("dashboard", "gaps") and "metric_results" in st.session_state
            )
            prefix = "➤ " if is_current else "‣ " if can_visit else "· "
            if can_visit and not is_current:
                if st.button(f"{prefix}{label}", key=f"nav_{key}"):
                    st.session_state.screen = key
                    st.rerun()
            else:
                st.markdown(f"{prefix}{label}")


def main():
    render_navigation_sidebar()

    screen = st.session_state.screen

    if screen == "home":
        render_home()
    elif screen == "journey":
        journey_builder.render()
    elif screen == "upload":
        upload.render()
    elif screen == "dashboard":
        if "metric_results" not in st.session_state:
            st.warning("Please upload and analyze data first.")
            st.session_state.screen = "upload"
            st.rerun()
        else:
            dashboard.render(
                st.session_state.dataframe,
                st.session_state.profile,
                st.session_state.metric_results,
                st.session_state.journey,
            )
    elif screen == "gaps":
        if "metric_results" not in st.session_state:
            st.warning("Please upload and analyze data first.")
            st.session_state.screen = "upload"
            st.rerun()
        else:
            gaps.render(
                st.session_state.dataframe,
                st.session_state.profile,
                st.session_state.metric_results,
                st.session_state.journey,
            )
    else:
        st.session_state.screen = "home"
        st.rerun()


if __name__ == "__main__":
    main()

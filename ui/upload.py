"""
upload.py

Screen 3 of the app: Data Upload. Lets the user upload a CSV, shows a
dataset summary (rows, columns, detected fields) and a preview of the
first rows, with clear validation messages if something is wrong.

Also offers the three bundled demo datasets as a quick-start option,
since a brand-new user may not have their own CSV ready yet.
"""

import os
import streamlit as st

from engine.data_loader import load_csv, REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from engine.data_profiler import profile_dataframe
from engine.metric_engine import calculate_all_metrics
from ui.components import prototype_banner, section_header

DEMO_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

DEMO_OPTIONS = {
    "Normal (intentional measurement gaps)": "demo_online_shopping_data.csv",
    "Better data (includes satisfaction & reason fields)": "demo_online_shopping_data_better.csv",
    "Poor / incomplete data": "demo_online_shopping_data_poor.csv",
}


def _run_analysis(dataframe):
    """Profile the data and calculate every defined metric, storing results in session_state."""
    profile = profile_dataframe(dataframe)
    metric_results = calculate_all_metrics(dataframe, profile)
    st.session_state.dataframe = dataframe
    st.session_state.profile = profile
    st.session_state.metric_results = metric_results


def render():
    prototype_banner()
    st.title("Upload Your Data")
    section_header(
        "Data Upload",
        "Upload the customer event data currently collected for this journey. "
        "The app will tell you what it can and cannot measure from it.",
    )

    st.markdown("**Quick start:** try one of the bundled synthetic demo datasets.")
    demo_choice = st.selectbox("Demo dataset", ["— None, I'll upload my own —"] + list(DEMO_OPTIONS.keys()))

    uploaded_file = st.file_uploader("Or upload your own CSV", type=["csv"])

    source_file = None
    source_label = None
    if uploaded_file is not None:
        source_file = uploaded_file
        source_label = uploaded_file.name
    elif demo_choice != "— None, I'll upload my own —":
        demo_path = os.path.join(DEMO_DATA_DIR, DEMO_OPTIONS[demo_choice])
        if os.path.exists(demo_path):
            source_file = demo_path
            source_label = DEMO_OPTIONS[demo_choice]

    if source_file is not None:
        result = load_csv(source_file)

        if not result.success:
            st.error(result.error_message)
            if result.missing_required:
                st.markdown(f"**Required columns:** {', '.join(REQUIRED_COLUMNS)}")
        else:
            if result.error_message:  # non-fatal note, e.g. skipped rows
                st.info(result.error_message)

            dataframe = result.dataframe
            st.success(f"Loaded **{source_label}** successfully.")

            # --- Dataset summary ---
            section_header("Dataset Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", f"{dataframe.shape[0]:,}")
            col2.metric("Columns", dataframe.shape[1])
            col3.metric("Unique Customers", f"{dataframe['customer_id'].nunique():,}")

            st.markdown("**Detected fields:**")
            all_known_columns = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
            detected_lines = []
            for col in all_known_columns:
                if col in dataframe.columns:
                    detected_lines.append(f"✓ {col}")
            extra_columns = [c for c in dataframe.columns if c not in all_known_columns]
            st.markdown(" &nbsp;&nbsp; ".join(detected_lines) if detected_lines else "_None of the expected columns were found._")
            if extra_columns:
                st.caption(f"Additional columns present (not used by the engine): {', '.join(extra_columns)}")

            st.markdown("**Data preview (first 15 rows):**")
            st.dataframe(dataframe.head(15), use_container_width=True)

            st.divider()
            col_back, col_next = st.columns([1, 1])
            with col_back:
                if st.button("← Back to Journey Builder"):
                    st.session_state.screen = "journey"
                    st.rerun()
            with col_next:
                if st.button("Analyze →", type="primary"):
                    _run_analysis(dataframe)
                    st.session_state.screen = "dashboard"
                    st.rerun()
    else:
        st.divider()
        if st.button("← Back to Journey Builder"):
            st.session_state.screen = "journey"
            st.rerun()

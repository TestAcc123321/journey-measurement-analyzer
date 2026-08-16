"""
gaps.py

Screen 6/7 of the app: Measurement Gaps and Recommendations, plus the
optional AI business summary and the export report button.

This is where we show, one by one, everything the data CANNOT
currently tell us - why not, what's missing, and what additional data
would help. Each gap also gets a transparent priority label.
"""

import streamlit as st

from engine.gap_detector import detect_gaps
from engine.scoring import calculate_coverage_score, find_largest_dropoff
from engine.ai_summary import is_ai_available, generate_summary
from utils.helpers import build_excel_report
from ui.components import prototype_banner, section_header, priority_badge


def render(dataframe, profile, metric_results, journey):
    prototype_banner()
    st.title("Measurement Gaps & Recommendations")

    coverage = calculate_coverage_score(metric_results)
    largest_dropoff_id, from_stage, to_stage, dropoff_percent = find_largest_dropoff(metric_results)
    gaps = detect_gaps(metric_results, largest_dropoff_id)

    section_header(
        "What We Cannot Currently Measure",
        "Each item below is a measurement gap: something the current data does not let us calculate, "
        "along with a plain-language reason why and what additional data could close the gap.",
    )

    if not gaps:
        st.success("No measurement gaps were detected — every defined metric could be calculated from this dataset.")
    else:
        for gap in gaps:
            with st.container(border=True):
                col_title, col_badge = st.columns([4, 1])
                with col_title:
                    st.markdown(f"**{gap.name}**  \n*{gap.category}*")
                with col_badge:
                    priority_badge(gap.priority)

                st.markdown(f"**Status:** Not currently measurable")
                st.markdown(f"**Why:** {gap.why_not}")
                st.markdown("**Potential data to collect:**")
                for item in gap.recommended_data:
                    st.markdown(f"- {item}")

    st.divider()

    section_header(
        "Important Reminder",
        "These are possible explanations and possible data to collect — not confirmed facts. "
        "The app never claims a specific cause (e.g. price) unless the uploaded data actually proves it.",
    )

    st.divider()

    # --- Optional AI summary ---
    section_header("Optional: AI Business Summary")
    st.caption("The AI only rephrases numbers already calculated above — it never invents figures.")

    if not is_ai_available():
        st.info("AI summary is disabled because no OPENAI_API_KEY is configured. The rest of the app works fully without it.")
    else:
        if st.button("Generate AI Business Summary"):
            with st.spinner("Generating summary..."):
                success, text = generate_summary(journey, coverage, gaps, (from_stage, to_stage, dropoff_percent))
            if success:
                st.success(text)
            else:
                st.warning(text)

    st.divider()

    # --- Export ---
    section_header("Export")
    report_bytes = build_excel_report(journey, metric_results, gaps, coverage)
    st.download_button(
        label="⬇ Download Measurement Report (Excel)",
        data=report_bytes,
        file_name="journey_measurement_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.divider()
    col_back, col_home = st.columns([1, 1])
    with col_back:
        if st.button("← Back to Dashboard"):
            st.session_state.screen = "dashboard"
            st.rerun()
    with col_home:
        if st.button("Start Over (Home)"):
            for key in ["journey", "dataframe", "profile", "metric_results"]:
                st.session_state.pop(key, None)
            st.session_state.screen = "home"
            st.rerun()

"""
dashboard.py

Screen 5 of the app: the main Measurement Dashboard. Shows:
    - the overall Measurement Coverage score
    - top-line counts (customers, events, measurable metrics, gaps)
    - a funnel chart of the core journey stages
    - a journey stage table
    - "Behavioural Findings" (facts the data DOES tell us)

This screen intentionally does NOT show measurement gaps in detail -
that lives on its own screen (ui/gaps.py) to keep the two concepts
(what we know vs what we don't) visually and structurally separate,
per the project brief's core analytical distinction.
"""

import streamlit as st
import plotly.graph_objects as go

from engine.scoring import calculate_coverage_score, find_largest_dropoff, FUNNEL_TRANSITIONS
from ui.components import prototype_banner, section_header, metric_card


def _build_funnel_chart(dataframe, profile):
    """
    Build a Plotly funnel chart of unique customers reaching each core
    stage. Stages whose underlying event isn't present in the data are
    simply skipped (rather than shown as a false zero).
    """
    stage_events = [
        ("Product Views", "product_view"),
        ("Add to Cart", "cart_add"),
        ("Checkout", "checkout_start"),
        ("Payment Attempt", "payment_attempt"),
        ("Order Confirmation", "order_confirmation"),
        ("Delivery", "delivery"),
    ]

    labels, values = [], []
    for label, event_name in stage_events:
        if profile.has_event(event_name):
            unique_customers = dataframe[dataframe["event"] == event_name]["customer_id"].nunique()
            labels.append(label)
            values.append(unique_customers)

    if not labels:
        return None

    fig = go.Figure(go.Funnel(
        y=labels,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ["#4A6FA5", "#5B87BC", "#6C9FD3", "#7DB7EA", "#8FC9F0", "#A6D8F5"][:len(labels)]},
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        font=dict(size=13),
    )
    return fig


def _build_stage_table(dataframe, profile, journey):
    """Build the journey stage table described in section 21 of the brief."""
    stage_event_map = {
        "product view": "product_view",
        "add to cart": "cart_add",
        "checkout": "checkout_start",
        "payment": "payment_attempt",
        "order confirmation": "order_confirmation",
        "delivery": "delivery",
        "return / review": "return",
    }

    rows = []
    previous_count = None
    for stage_name in journey["stages"]:
        key = stage_name.strip().lower()
        matched_event = None
        for label, event_name in stage_event_map.items():
            if label in key or key in label:
                matched_event = event_name
                break

        if matched_event and profile.has_event(matched_event):
            raw_count = dataframe[dataframe["event"] == matched_event]["customer_id"].nunique()
            if previous_count is None or previous_count == 0:
                conversion = "100%"
            else:
                conversion = f"{round((raw_count / previous_count) * 100, 1)}%"
            status = "Measurable"
            previous_count = raw_count
            customer_count = f"{raw_count:,}"
        else:
            customer_count = "N/A"
            conversion = "N/A"
            status = "Gap"

        rows.append({
            "Stage": stage_name,
            "Customers": customer_count,
            "Conversion": conversion,
            "Status": status,
        })

    return rows


def render(dataframe, profile, metric_results, journey):
    prototype_banner()
    st.title("Measurement Dashboard")

    coverage = calculate_coverage_score(metric_results)
    largest_dropoff_id, from_stage, to_stage, dropoff_percent = find_largest_dropoff(metric_results)

    # --- Top-line numbers ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Measurement Coverage", f"{coverage['score']}%")
    with col2:
        metric_card("Metrics Measurable", f"{coverage['measurable_count']} / {coverage['total']}")
    with col3:
        metric_card("Measurement Gaps", coverage["total"] - coverage["measurable_count"])
    with col4:
        metric_card("Customers Analyzed", f"{profile.customer_count:,}")

    st.caption(
        "Prototype measurement coverage score based on the percentage of defined metrics "
        "that can currently be calculated. This is a demonstration metric, not a scientifically "
        "validated business KPI."
    )
    st.caption(f"Events analyzed: {profile.row_count:,}")

    st.divider()

    # --- Funnel chart ---
    section_header("Journey Funnel", "Unique customers reaching each stage, based on the uploaded data.")
    funnel_fig = _build_funnel_chart(dataframe, profile)
    if funnel_fig is not None:
        st.plotly_chart(funnel_fig, use_container_width=True)
    else:
        st.info("No funnel stages could be built from the events present in this dataset.")

    if from_stage:
        st.warning(f"**Largest observed drop-off:** {from_stage} → {to_stage} ({dropoff_percent}% did not continue to the next stage).")

    st.divider()

    # --- Stage table ---
    section_header("Journey Stage Table")
    stage_rows = _build_stage_table(dataframe, profile, journey)
    st.dataframe(stage_rows, use_container_width=True, hide_index=True)

    st.divider()

    # --- Behavioural findings ---
    section_header(
        "Behavioural Findings",
        "Facts the data directly tells us. These are different from measurement gaps (see the Measurement Gaps screen).",
    )
    measurable_results = [r for r in metric_results if r.measurable and r.display_value not in (None, "N/A")]
    if not measurable_results:
        st.info("No metrics were measurable from the uploaded data.")
    else:
        for result in measurable_results:
            st.markdown(f"- **{result.name}:** {result.display_value} — {result.description}")

    st.divider()
    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Back to Upload"):
            st.session_state.screen = "upload"
            st.rerun()
    with col_next:
        if st.button("View Measurement Gaps →", type="primary"):
            st.session_state.screen = "gaps"
            st.rerun()

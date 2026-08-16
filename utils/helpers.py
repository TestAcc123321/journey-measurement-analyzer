"""
helpers.py

Small utility functions that don't belong to any one screen or engine
module: the default journey definition, and building the downloadable
Excel report.
"""

import io
import pandas as pd


DEFAULT_JOURNEY_STAGES = [
    "Product Discovery",
    "Product View",
    "Add to Cart",
    "Checkout",
    "Payment",
    "Order Confirmation",
    "Delivery",
    "Return / Review",
]


def default_journey():
    """Return the default TechMart demo journey as a dictionary."""
    return {
        "name": "Online Shopping Journey",
        "business": "TechMart",
        "description": (
            "The journey a customer follows from discovering a product "
            "through purchasing and receiving the product."
        ),
        "stages": list(DEFAULT_JOURNEY_STAGES),
    }


def build_excel_report(journey, metric_results, gaps, coverage):
    """
    Build an in-memory Excel workbook summarising the analysis, so it
    can be offered as a download via st.download_button without
    writing anything to disk.

    Returns raw bytes.
    """
    metrics_rows = []
    for result in metric_results:
        metrics_rows.append({
            "Metric ID": result.metric_id,
            "Metric Name": result.name,
            "Category": result.category,
            "Status": "Measurable" if result.measurable else "Measurement Gap",
            "Calculated Value": result.display_value if result.measurable else "N/A",
            "Missing Information": "" if result.measurable else result.gap_reason,
            "Priority": result.priority,
        })
    metrics_df = pd.DataFrame(metrics_rows)

    gaps_rows = []
    for gap in gaps:
        gaps_rows.append({
            "Metric ID": gap.metric_id,
            "Gap Name": gap.name,
            "Category": gap.category,
            "Why Not Measurable": gap.why_not,
            "Recommended Additional Data": "; ".join(gap.recommended_data),
            "Priority": gap.priority,
        })
    gaps_df = pd.DataFrame(gaps_rows)

    stages_df = pd.DataFrame({"Journey Stage": journey["stages"]})

    summary_df = pd.DataFrame([
        {"Item": "Journey Name", "Value": journey["name"]},
        {"Item": "Business", "Value": journey["business"]},
        {"Item": "Measurement Coverage", "Value": f"{coverage['score']}%"},
        {"Item": "Measurable Metrics", "Value": f"{coverage['measurable_count']} / {coverage['total']}"},
        {"Item": "Measurement Gaps", "Value": coverage["total"] - coverage["measurable_count"]},
    ])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        stages_df.to_excel(writer, sheet_name="Journey Stages", index=False)
        metrics_df.to_excel(writer, sheet_name="Metrics", index=False)
        gaps_df.to_excel(writer, sheet_name="Measurement Gaps", index=False)

    buffer.seek(0)
    return buffer.getvalue()

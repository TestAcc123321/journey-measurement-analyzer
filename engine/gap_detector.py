"""
gap_detector.py

Takes the list of MetricResult objects produced by metric_engine.py
and turns the ones that are NOT measurable into rich "MeasurementGap"
objects: what's missing, why, what data could fix it, and how
important the gap is.

This file also holds the simple, transparent priority rules described
in the project brief - no machine learning, just readable logic.
"""

# For each metric_id, a short list of realistic additional data points
# that would make the metric measurable. This is deliberately a plain
# lookup table (not AI-generated) so recommendations stay predictable
# and easy to explain.
RECOMMENDED_DATA = {
    "M011": ["Post-purchase CSAT survey", "Net Promoter Score (NPS)", "Customer feedback form"],
    "M012": ["Cart exit survey", "Checkout exit survey", "Session behaviour tracking"],
    "M013": ["Post-purchase 'why did you buy' survey", "Marketing attribution data"],
    "M014": ["Post-delivery satisfaction survey", "Delivery experience rating"],
}

# Fallback recommendations for any other event-based gap (e.g. a
# conversion metric that's missing an event entirely).
GENERIC_RECOMMENDATIONS = [
    "Instrument the missing event in the website/app so it is logged",
    "Add an exit survey at the relevant stage",
    "Review analytics tracking configuration for gaps",
]


class MeasurementGap:
    """Describes one thing we currently cannot measure, and why."""

    def __init__(self, metric_id, name, category, why_not, missing_data, recommended_data, priority):
        self.metric_id = metric_id
        self.name = name
        self.category = category
        self.why_not = why_not
        self.missing_data = missing_data
        self.recommended_data = recommended_data
        self.priority = priority


def _priority_for_gap(metric_result, largest_dropoff_metric_id):
    """
    Simple, transparent priority rules (per project brief section 23):

    High priority when:
        - the metric's own defined priority is "High", OR
        - this metric represents the single largest drop-off point
          found in the funnel (see scoring.py)

    Medium priority when the metric's own defined priority is "Medium".

    Low priority otherwise.

    This is intentionally simple rule-based logic, not a sophisticated
    scoring model - the app should never claim more sophistication
    than it actually has.
    """
    if metric_result.metric_id == largest_dropoff_metric_id:
        return "High"
    return metric_result.priority


def detect_gaps(metric_results, largest_dropoff_metric_id=None):
    """
    Walk through every metric result. For each one that is NOT
    measurable, build a MeasurementGap explaining the situation.

    Measurable metrics are skipped entirely - they belong in the
    "Behavioural Findings" part of the dashboard, not here.
    """
    gaps = []

    for result in metric_results:
        if result.measurable:
            continue

        missing_data = result.gap_reason or "The data required for this metric was not found."
        recommended = RECOMMENDED_DATA.get(result.metric_id, GENERIC_RECOMMENDATIONS)
        priority = _priority_for_gap(result, largest_dropoff_metric_id)

        gaps.append(MeasurementGap(
            metric_id=result.metric_id,
            name=result.name,
            category=result.category,
            why_not=missing_data,
            missing_data=missing_data,
            recommended_data=recommended,
            priority=priority,
        ))

    # Sort so High priority gaps appear first, then Medium, then Low.
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    gaps.sort(key=lambda gap: priority_order.get(gap.priority, 3))

    return gaps

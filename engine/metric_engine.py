"""
metric_engine.py

This is the deterministic heart of the application. It NEVER uses AI.
Every number it produces comes from real arithmetic on the uploaded
data, so the app keeps working (minus the optional AI summary) even
with no internet connection or API key.

For every metric defined in config/measurement_definitions.py, this
engine:
    1. Checks whether the data contains what the metric needs
       (using the DataProfile from data_profiler.py)
    2. If yes: calculates the metric and returns the real value
    3. If no: returns a "Measurement Gap" result instead

We deliberately keep one function per "calculation_type" rather than
one function per metric. Since several metrics share the same shape
of calculation (e.g. "what fraction of people who did A also did B"),
this avoids repeating the same logic fourteen times.
"""

import pandas as pd
from config.measurement_definitions import MEASUREMENT_DEFINITIONS


class MetricResult:
    """The outcome of trying to calculate one metric."""

    def __init__(self, metric_id, name, category, priority, description,
                 measurable, value=None, display_value=None,
                 numerator=None, denominator=None, gap_reason=None):
        self.metric_id = metric_id
        self.name = name
        self.category = category
        self.priority = priority
        self.description = description
        self.measurable = measurable          # True/False
        self.value = value                    # raw numeric value, or None
        self.display_value = display_value    # human-readable string, e.g. "42.0%"
        self.numerator = numerator
        self.denominator = denominator
        self.gap_reason = gap_reason          # why it's not measurable, if applicable


def _customers_who_did(dataframe, event_name):
    """Return the set of unique customer_ids who performed a given event."""
    matching_rows = dataframe[dataframe["event"] == event_name]
    return set(matching_rows["customer_id"].unique())


def _safe_percentage(numerator, denominator):
    """
    Calculate numerator/denominator as a percentage, without ever
    crashing on division by zero. Returns None if the denominator is 0,
    which the caller should treat as "not measurable right now"
    (e.g. there were zero payment attempts in the data).
    """
    if denominator == 0:
        return None
    return round((numerator / denominator) * 100, 1)


def _requirements_met(definition, profile):
    """
    Check whether the DataProfile satisfies everything a metric
    definition requires: every required event must be present, and
    every required field (column) must be present.
    """
    for event_name in definition["required_events"]:
        if not profile.has_event(event_name):
            return False, f"The event '{event_name}' does not appear anywhere in the uploaded data."
    for field_name in definition["required_fields"]:
        if not profile.has_field(field_name):
            return False, f"The column '{field_name}' is not present in the uploaded data."
    return True, None


def _calculate_stage_conversion(dataframe, definition):
    """A -> B conversion: of the customers who did A, how many also did B?"""
    from_customers = _customers_who_did(dataframe, definition["from_event"])
    to_customers = _customers_who_did(dataframe, definition["to_event"])
    numerator = len(from_customers & to_customers)
    denominator = len(from_customers)
    percentage = _safe_percentage(numerator, denominator)
    return numerator, denominator, percentage


def _calculate_abandonment(dataframe, definition):
    """The inverse of a stage conversion: did A, but never did B."""
    from_customers = _customers_who_did(dataframe, definition["from_event"])
    to_customers = _customers_who_did(dataframe, definition["to_event"])
    numerator = len(from_customers - to_customers)
    denominator = len(from_customers)
    percentage = _safe_percentage(numerator, denominator)
    return numerator, denominator, percentage


def _calculate_event_ratio(dataframe, definition):
    """Ratio of two event ROW COUNTS (not unique customers) - e.g. payment outcomes."""
    numerator = int((dataframe["event"] == definition["numerator_event"]).sum())
    denominator = int((dataframe["event"] == definition["denominator_event"]).sum())
    percentage = _safe_percentage(numerator, denominator)
    return numerator, denominator, percentage


def _calculate_unique_customer_count(dataframe, definition):
    """Just a raw count of unique customers who triggered the required event."""
    event_name = definition["required_events"][0]
    customers = _customers_who_did(dataframe, event_name)
    return len(customers), None, None


def _calculate_field_average(dataframe, definition):
    """Average of a numeric enrichment field, e.g. customer_satisfaction (1-5)."""
    field = definition["field"]
    numeric_values = pd.to_numeric(dataframe[field], errors="coerce").dropna()
    if len(numeric_values) == 0:
        return None, None, None
    average_value = round(numeric_values.mean(), 2)
    return average_value, len(numeric_values), None


def _calculate_field_breakdown(dataframe, definition):
    """Most common values of a text enrichment field, e.g. abandonment_reason."""
    field = definition["field"]
    text_values = dataframe[field].dropna()
    text_values = text_values[text_values.astype(str).str.strip() != ""]
    if len(text_values) == 0:
        return None, None, None
    breakdown = text_values.value_counts().to_dict()
    return breakdown, len(text_values), None


def calculate_all_metrics(dataframe, profile):
    """
    The main entry point for this file. Loops through every metric
    definition, checks whether it's measurable, and calculates it if so.

    Returns a list of MetricResult objects - one per defined metric,
    in the same order as MEASUREMENT_DEFINITIONS.
    """
    results = []

    for definition in MEASUREMENT_DEFINITIONS:
        can_measure, reason = _requirements_met(definition, profile)

        if not can_measure:
            results.append(MetricResult(
                metric_id=definition["metric_id"],
                name=definition["name"],
                category=definition["category"],
                priority=definition["priority"],
                description=definition["description"],
                measurable=False,
                gap_reason=reason,
            ))
            continue

        calc_type = definition["calculation_type"]

        try:
            if calc_type == "stage_conversion":
                numerator, denominator, value = _calculate_stage_conversion(dataframe, definition)
                display = f"{value}%" if value is not None else "N/A"
            elif calc_type == "abandonment":
                numerator, denominator, value = _calculate_abandonment(dataframe, definition)
                display = f"{value}%" if value is not None else "N/A"
            elif calc_type == "event_ratio":
                numerator, denominator, value = _calculate_event_ratio(dataframe, definition)
                display = f"{value}%" if value is not None else "N/A"
            elif calc_type == "unique_customer_count":
                value, _, _ = _calculate_unique_customer_count(dataframe, definition)
                numerator, denominator = value, None
                display = f"{value:,}"
            elif calc_type == "field_average":
                value, sample_size, _ = _calculate_field_average(dataframe, definition)
                numerator, denominator = value, sample_size
                display = f"{value} (avg, n={sample_size})" if value is not None else "N/A"
            elif calc_type == "field_breakdown":
                value, sample_size, _ = _calculate_field_breakdown(dataframe, definition)
                numerator, denominator = sample_size, None
                display = f"{sample_size} responses" if value is not None else "N/A"
            else:
                # Unknown calculation type - treat as not measurable
                # rather than crashing the app.
                results.append(MetricResult(
                    metric_id=definition["metric_id"], name=definition["name"],
                    category=definition["category"], priority=definition["priority"],
                    description=definition["description"], measurable=False,
                    gap_reason="No calculation method is defined for this metric.",
                ))
                continue

            # If the calculation produced None (e.g. zero denominator or
            # no usable rows), treat this as a measurement gap rather
            # than showing a broken value.
            if value is None:
                results.append(MetricResult(
                    metric_id=definition["metric_id"], name=definition["name"],
                    category=definition["category"], priority=definition["priority"],
                    description=definition["description"], measurable=False,
                    gap_reason="The required events exist in the data, but there were zero qualifying records to calculate this from (e.g. zero attempts).",
                ))
                continue

            results.append(MetricResult(
                metric_id=definition["metric_id"], name=definition["name"],
                category=definition["category"], priority=definition["priority"],
                description=definition["description"], measurable=True,
                value=value, display_value=display,
                numerator=numerator, denominator=denominator,
            ))

        except Exception as error:
            # Defensive catch-all: a single broken metric should never
            # take down the whole dashboard.
            results.append(MetricResult(
                metric_id=definition["metric_id"], name=definition["name"],
                category=definition["category"], priority=definition["priority"],
                description=definition["description"], measurable=False,
                gap_reason=f"This metric could not be calculated due to a data issue ({type(error).__name__}).",
            ))

    return results

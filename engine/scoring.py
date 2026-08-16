"""
scoring.py

Two small, focused jobs:

1. Calculate the overall "Measurement Coverage" score - simply the
   percentage of defined metrics that turned out to be measurable.
   This is explicitly a demonstration statistic, not an
   industry-standard KPI (see project brief section 18).

2. Work out which stage-to-stage transition in the funnel had the
   single largest drop-off, so the gap detector can flag the related
   measurement gap as higher priority (per section 23's "critical
   stage" rule).
"""

from config.measurement_definitions import MEASUREMENT_DEFINITIONS


def calculate_coverage_score(metric_results):
    """
    Measurement Coverage = (measurable metrics / total defined metrics) x 100

    Returns a dict with the score plus the raw counts, since the
    dashboard displays both ("57%" and "8 / 14").
    """
    total = len(metric_results)
    measurable_count = sum(1 for result in metric_results if result.measurable)

    if total == 0:
        return {"score": 0, "measurable_count": 0, "total": 0}

    score = round((measurable_count / total) * 100)
    return {"score": score, "measurable_count": measurable_count, "total": total}


# The ordered list of stage-to-stage transitions that make up the core
# funnel. Each entry maps to the metric_id of the corresponding
# stage-conversion metric, so we can look up its numerator/denominator.
FUNNEL_TRANSITIONS = [
    ("Product View", "Add to Cart", "M002"),
    ("Add to Cart", "Checkout", "M003"),
    ("Checkout", "Payment Attempt", "M004"),
    ("Payment Success", "Order Confirmation", "M008"),
    ("Order Confirmation", "Delivery", "M009"),
]


def find_largest_dropoff(metric_results):
    """
    Look across the funnel-stage metrics and find which transition had
    the largest percentage of customers NOT continuing to the next
    stage. Returns (metric_id, from_stage, to_stage, dropoff_percent)
    or (None, None, None, None) if no funnel metrics were measurable.
    """
    results_by_id = {result.metric_id: result for result in metric_results}

    largest_dropoff_percent = -1
    largest_metric_id = None
    largest_from_stage = None
    largest_to_stage = None

    for from_stage, to_stage, metric_id in FUNNEL_TRANSITIONS:
        result = results_by_id.get(metric_id)
        if result is None or not result.measurable or result.value is None:
            continue
        dropoff_percent = round(100 - result.value, 1)
        if dropoff_percent > largest_dropoff_percent:
            largest_dropoff_percent = dropoff_percent
            largest_metric_id = metric_id
            largest_from_stage = from_stage
            largest_to_stage = to_stage

    if largest_metric_id is None:
        return None, None, None, None

    return largest_metric_id, largest_from_stage, largest_to_stage, largest_dropoff_percent

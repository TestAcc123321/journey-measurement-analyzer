"""
test_gap_detection.py

Tests that metrics missing their required events/fields are correctly
flagged as measurement gaps, with sensible explanations and priorities.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from engine.data_profiler import profile_dataframe
from engine.metric_engine import calculate_all_metrics
from engine.gap_detector import detect_gaps


def _make_dataframe(rows):
    df = pd.DataFrame(rows, columns=["customer_id", "timestamp", "event"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def test_missing_enrichment_fields_become_gaps():
    rows = [
        ("C1", "2026-01-01", "product_view"),
        ("C1", "2026-01-01", "cart_add"),
    ]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    gaps = detect_gaps(results)

    gap_ids = {gap.metric_id for gap in gaps}
    for expected_gap_id in ["M011", "M012", "M013", "M014"]:
        assert expected_gap_id in gap_ids, f"expected {expected_gap_id} to be a gap"
    print("test_missing_enrichment_fields_become_gaps passed")


def test_measurable_metrics_are_not_gaps():
    rows = [
        ("C1", "2026-01-01", "product_view"),
        ("C1", "2026-01-01", "cart_add"),
    ]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    gaps = detect_gaps(results)
    gap_ids = {gap.metric_id for gap in gaps}
    assert "M002" not in gap_ids, "Add-to-Cart Rate was measurable and should not appear as a gap"
    print("test_measurable_metrics_are_not_gaps passed")


def test_gap_has_recommendation():
    rows = [("C1", "2026-01-01", "product_view")]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    gaps = detect_gaps(results)
    for gap in gaps:
        assert len(gap.recommended_data) > 0, f"{gap.metric_id} has no recommendations"
    print("test_gap_has_recommendation passed")


def test_missing_field_detection_via_data_loader():
    from engine.data_loader import load_csv
    import io
    bad_csv = io.StringIO("customer_id,timestamp\nC1,2026-01-01")
    result = load_csv(bad_csv)
    assert result.success is False
    assert "event" in result.missing_required
    print("test_missing_field_detection_via_data_loader passed")


if __name__ == "__main__":
    test_missing_enrichment_fields_become_gaps()
    test_measurable_metrics_are_not_gaps()
    test_gap_has_recommendation()
    test_missing_field_detection_via_data_loader()
    print("\nAll gap detection tests passed.")

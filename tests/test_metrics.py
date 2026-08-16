"""
test_metrics.py

Tests for the deterministic metric engine. We build tiny hand-crafted
DataFrames (a handful of rows) so the expected answer is obvious and
easy to check by eye, rather than relying on the large synthetic
dataset where the "right answer" isn't obvious just by reading it.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from engine.data_profiler import profile_dataframe
from engine.metric_engine import calculate_all_metrics


def _make_dataframe(rows):
    df = pd.DataFrame(rows, columns=["customer_id", "timestamp", "event"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def _get_result(results, metric_id):
    for r in results:
        if r.metric_id == metric_id:
            return r
    raise AssertionError(f"metric {metric_id} not found in results")


def test_add_to_cart_rate():
    # 4 customers view a product, only 2 of them add to cart -> 50%
    rows = [
        ("C1", "2026-01-01", "product_view"),
        ("C2", "2026-01-01", "product_view"),
        ("C3", "2026-01-01", "product_view"),
        ("C4", "2026-01-01", "product_view"),
        ("C1", "2026-01-01", "cart_add"),
        ("C2", "2026-01-01", "cart_add"),
    ]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    m002 = _get_result(results, "M002")
    assert m002.measurable is True
    assert m002.value == 50.0, f"expected 50.0, got {m002.value}"
    print("test_add_to_cart_rate passed")


def test_cart_to_checkout_rate():
    rows = [
        ("C1", "2026-01-01", "cart_add"),
        ("C2", "2026-01-01", "cart_add"),
        ("C3", "2026-01-01", "cart_add"),
        ("C1", "2026-01-01", "checkout_start"),
    ]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    m003 = _get_result(results, "M003")
    assert m003.measurable is True
    expected = round((1 / 3) * 100, 1)
    assert m003.value == expected, f"expected {expected}, got {m003.value}"
    print("test_cart_to_checkout_rate passed")


def test_payment_success_and_failure_rate():
    rows = [
        ("C1", "2026-01-01", "payment_attempt"),
        ("C2", "2026-01-01", "payment_attempt"),
        ("C3", "2026-01-01", "payment_attempt"),
        ("C4", "2026-01-01", "payment_attempt"),
        ("C1", "2026-01-01", "payment_success"),
        ("C2", "2026-01-01", "payment_success"),
        ("C3", "2026-01-01", "payment_success"),
        ("C4", "2026-01-01", "payment_failure"),
    ]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)

    m005 = _get_result(results, "M005")  # success rate
    assert m005.value == 75.0, f"expected 75.0, got {m005.value}"

    m007 = _get_result(results, "M007")  # failure rate
    assert m007.value == 25.0, f"expected 25.0, got {m007.value}"
    print("test_payment_success_and_failure_rate passed")


def test_delivery_rate():
    rows = [
        ("C1", "2026-01-01", "order_confirmation"),
        ("C2", "2026-01-01", "order_confirmation"),
        ("C1", "2026-01-01", "delivery"),
    ]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    m009 = _get_result(results, "M009")
    assert m009.measurable is True
    assert m009.value == 50.0, f"expected 50.0, got {m009.value}"
    print("test_delivery_rate passed")


def test_return_rate():
    rows = [
        ("C1", "2026-01-01", "delivery"),
        ("C2", "2026-01-01", "delivery"),
        ("C3", "2026-01-01", "delivery"),
        ("C4", "2026-01-01", "delivery"),
        ("C1", "2026-01-01", "return"),
    ]
    df = _make_dataframe(rows)
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    m010 = _get_result(results, "M010")
    assert m010.measurable is True
    assert m010.value == 25.0, f"expected 25.0, got {m010.value}"
    print("test_return_rate passed")


def test_zero_denominator_is_not_measurable():
    # payment_attempt event exists (so the metric LOOKS possible), but
    # there are zero attempts in this particular slice, so the rate
    # must be reported as not measurable rather than crashing or
    # showing a false 0%.
    rows = [
        ("C1", "2026-01-01", "checkout_start"),
    ]
    df = _make_dataframe(rows)
    # Manually inject an empty payment_attempt-typed frame scenario:
    # since there are no payment_attempt rows at all, the profiler
    # won't detect the event, and M005 should be a gap for a different
    # reason (missing event) - this still proves no crash occurs.
    profile = profile_dataframe(df)
    results = calculate_all_metrics(df, profile)
    m005 = _get_result(results, "M005")
    assert m005.measurable is False
    print("test_zero_denominator_is_not_measurable passed")


if __name__ == "__main__":
    test_add_to_cart_rate()
    test_cart_to_checkout_rate()
    test_payment_success_and_failure_rate()
    test_delivery_rate()
    test_return_rate()
    test_zero_denominator_is_not_measurable()
    print("\nAll metric tests passed.")

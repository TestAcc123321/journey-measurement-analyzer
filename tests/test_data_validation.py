"""
test_data_validation.py

Tests that the data loader handles messy/invalid input gracefully -
never raising an exception up to the caller, and always giving a
clear, human-readable explanation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
from engine.data_loader import load_csv


def test_empty_file():
    empty = io.StringIO("")
    result = load_csv(empty)
    assert result.success is False
    print("test_empty_file passed")


def test_missing_required_columns():
    csv_text = "foo,bar\n1,2\n"
    result = load_csv(io.StringIO(csv_text))
    assert result.success is False
    assert "customer_id" in result.missing_required
    assert "timestamp" in result.missing_required
    assert "event" in result.missing_required
    print("test_missing_required_columns passed")


def test_valid_minimal_file():
    csv_text = "customer_id,timestamp,event\nC1,2026-01-01 10:00:00,product_view\n"
    result = load_csv(io.StringIO(csv_text))
    assert result.success is True
    assert result.dataframe.shape[0] == 1
    print("test_valid_minimal_file passed")


def test_column_name_normalisation():
    # Columns with mixed case / extra whitespace should still be recognised.
    csv_text = " Customer_ID , Timestamp , Event \nC1,2026-01-01,product_view\n"
    result = load_csv(io.StringIO(csv_text))
    assert result.success is True, result.error_message
    assert "customer_id" in result.dataframe.columns
    print("test_column_name_normalisation passed")


def test_unparsable_timestamps_are_skipped_not_fatal():
    csv_text = "customer_id,timestamp,event\nC1,not-a-date,product_view\nC2,2026-01-01,product_view\n"
    result = load_csv(io.StringIO(csv_text))
    assert result.success is True
    assert result.dataframe.shape[0] == 1  # the bad row was dropped
    print("test_unparsable_timestamps_are_skipped_not_fatal passed")


def test_all_unparsable_timestamps_is_fatal():
    csv_text = "customer_id,timestamp,event\nC1,not-a-date,product_view\n"
    result = load_csv(io.StringIO(csv_text))
    assert result.success is False
    print("test_all_unparsable_timestamps_is_fatal passed")


if __name__ == "__main__":
    test_empty_file()
    test_missing_required_columns()
    test_valid_minimal_file()
    test_column_name_normalisation()
    test_unparsable_timestamps_are_skipped_not_fatal()
    test_all_unparsable_timestamps_is_fatal()
    print("\nAll data validation tests passed.")

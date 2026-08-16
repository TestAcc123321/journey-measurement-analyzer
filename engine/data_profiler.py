"""
data_profiler.py

Once a CSV has been loaded (see data_loader.py), we need to answer a
simple question: "What does this dataset actually contain?"

This file inspects the DataFrame and produces a summary describing:
    - which columns exist
    - which known events actually appear in the data
    - basic counts (rows, customers, events)

This summary (a "DataProfile") is then used by the metric engine to
decide which metrics can be calculated, and by the gap detector to
explain why others cannot.
"""

from config.measurement_definitions import KNOWN_EVENTS, OPTIONAL_ENRICHMENT_FIELDS


class DataProfile:
    """A plain summary of what a dataset contains."""

    def __init__(self, columns_present, events_present, row_count, customer_count, event_counts):
        self.columns_present = columns_present
        self.events_present = events_present
        self.row_count = row_count
        self.customer_count = customer_count
        self.event_counts = event_counts  # dict: event name -> number of rows

    def has_event(self, event_name):
        return event_name in self.events_present

    def has_field(self, field_name):
        return field_name in self.columns_present


def profile_dataframe(dataframe):
    """
    Look at a cleaned DataFrame (from data_loader.load_csv) and work
    out which columns and events are actually present and usable.

    An "enrichment" field like customer_satisfaction only counts as
    present if it exists AND has at least one non-empty value -
    a column full of blank cells doesn't really give us usable data.
    """
    columns_present = list(dataframe.columns)

    # Work out which of our KNOWN_EVENTS actually show up in the
    # "event" column of this dataset.
    events_in_data = set(dataframe["event"].unique())
    events_present = [event for event in KNOWN_EVENTS if event in events_in_data]

    # Count how many rows correspond to each event, useful for the
    # dashboard and for metric calculations later.
    event_counts = dataframe["event"].value_counts().to_dict()

    # For optional enrichment fields (e.g. customer_satisfaction),
    # only treat the field as "usable" if the column exists AND has
    # at least one actual (non-null, non-blank) value.
    usable_columns = list(columns_present)
    for field in OPTIONAL_ENRICHMENT_FIELDS:
        if field in dataframe.columns:
            has_real_values = dataframe[field].notna().any() and (dataframe[field].astype(str).str.strip() != "").any()
            if not has_real_values and field in usable_columns:
                usable_columns.remove(field)

    row_count = dataframe.shape[0]
    customer_count = dataframe["customer_id"].nunique()

    return DataProfile(
        columns_present=usable_columns,
        events_present=events_present,
        row_count=row_count,
        customer_count=customer_count,
        event_counts=event_counts,
    )

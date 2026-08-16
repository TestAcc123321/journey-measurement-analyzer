"""
data_loader.py

Responsible for one job: safely reading a CSV file into a pandas
DataFrame and checking that it has the columns we need.

We separate "loading" from "profiling" (data_profiler.py) so each
file stays focused on one responsibility. This makes the code easier
to read, test, and change later.
"""

import pandas as pd

# These columns MUST be present for the app to do anything useful.
# If any of these are missing, we cannot analyze the journey at all.
REQUIRED_COLUMNS = ["customer_id", "timestamp", "event"]

# These columns are nice to have but not strictly required. If they
# are missing, some metrics simply won't be calculable - that is the
# whole point of the "measurement gap" concept in this app.
OPTIONAL_COLUMNS = [
    "product_id",
    "status",
    "channel",
    "transaction_id",
    "order_id",
    "customer_satisfaction",
    "abandonment_reason",
    "purchase_reason",
    "delivery_satisfaction",
]


class LoadResult:
    """
    A simple container for the outcome of trying to load a file.

    Using a small class like this (instead of just returning a
    DataFrame or None) lets us pass back BOTH the data AND a clear,
    human-readable explanation of what went wrong, if anything did.
    """

    def __init__(self, success, dataframe=None, error_message=None, missing_required=None):
        self.success = success
        self.dataframe = dataframe
        self.error_message = error_message
        self.missing_required = missing_required or []


def load_csv(uploaded_file):
    """
    Attempt to read an uploaded CSV file into a pandas DataFrame.

    uploaded_file: a file-like object, e.g. from Streamlit's
                   st.file_uploader(), or a plain file path string.

    Returns a LoadResult. This function is intentionally defensive -
    it tries to catch every realistic way a CSV upload can go wrong
    so the rest of the app never has to deal with a raw exception.
    """
    # Step 1: try to actually parse the CSV text into a DataFrame.
    try:
        dataframe = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        return LoadResult(False, error_message="The uploaded file is empty. Please upload a CSV with data in it.")
    except pd.errors.ParserError:
        return LoadResult(False, error_message="The file could not be parsed as a CSV. Please check the file format.")
    except UnicodeDecodeError:
        return LoadResult(False, error_message="The file encoding could not be read. Please save the CSV as UTF-8 and try again.")
    except Exception:
        # Catch-all so a normal user never sees a Python stack trace.
        return LoadResult(False, error_message="The file could not be read. Please confirm it is a valid CSV file.")

    # Step 2: make sure there is actually at least one row of data.
    if dataframe.shape[0] == 0:
        return LoadResult(False, error_message="The uploaded file has no rows. Please upload a CSV that contains event data.")

    # Step 3: normalise column names (strip whitespace, lowercase)
    # so that "Customer_ID" and "customer_id " are both recognised.
    dataframe.columns = [str(col).strip().lower() for col in dataframe.columns]

    # Step 4: check that the required columns are present.
    missing_required = [col for col in REQUIRED_COLUMNS if col not in dataframe.columns]
    if missing_required:
        readable_missing = ", ".join(missing_required)
        return LoadResult(
            False,
            error_message=(
                f"The file is missing required column(s): {readable_missing}. "
                f"The app needs at least: {', '.join(REQUIRED_COLUMNS)}."
            ),
            missing_required=missing_required,
        )

    # Step 5: try to parse the timestamp column. If some rows fail,
    # we don't crash - we just drop those specific rows and keep going,
    # since a few bad rows shouldn't block the whole analysis.
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], errors="coerce")
    unparsable_count = dataframe["timestamp"].isna().sum()
    dataframe = dataframe.dropna(subset=["timestamp"]).copy()

    if dataframe.shape[0] == 0:
        return LoadResult(False, error_message="No rows had a valid, readable timestamp. Please check the timestamp column.")

    # Step 6: clean up event and customer_id text fields so that
    # stray whitespace or inconsistent casing doesn't create
    # "phantom" events that don't match our known event list.
    dataframe["event"] = dataframe["event"].astype(str).str.strip().str.lower()
    dataframe["customer_id"] = dataframe["customer_id"].astype(str).str.strip()

    result = LoadResult(True, dataframe=dataframe)
    if unparsable_count > 0:
        # Not a fatal error, just something worth surfacing to the user.
        result.error_message = f"Note: {unparsable_count} row(s) had an unreadable timestamp and were skipped."
    return result

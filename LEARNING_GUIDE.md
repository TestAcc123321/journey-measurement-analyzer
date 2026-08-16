# Learning Guide

This guide explains the Journey Measurement Analyzer codebase in plain English, aimed
at someone learning Python and about to start a Computer Science degree. Read this
*after* you've run the app at least once and clicked through every screen.

---

## Part 1: Big picture

Imagine a spreadsheet where every row is "one thing a customer did" — viewed a
product, added it to a cart, paid, etc. The app reads that spreadsheet (a CSV file)
and tries to answer questions like "what percentage of people who viewed a product
went on to buy it?"

Some questions can be answered directly from the data (e.g. the conversion rate
above). Other questions **cannot** be answered because the data was never collected
(e.g. "why didn't they buy it?"). The app's whole job is to sort every possible
question into one of those two buckets, and explain itself clearly either way.

The three layers of the app:

1. **`config/`** — a big list of *what we'd like to measure* (14 metrics), described
   as data (Python dictionaries), not as code.
2. **`engine/`** — the calculator. Reads the config, checks the uploaded data, and
   either produces a real number or explains why it can't.
3. **`ui/`** — the Streamlit screens. Purely responsible for displaying things nicely;
   it never does its own calculations.

## Part 2: How data flows

```
CSV file uploaded by the user
        ↓
engine/data_loader.py       →  reads the CSV safely, checks required columns exist
        ↓
engine/data_profiler.py     →  figures out which events/columns are actually present
        ↓
engine/metric_engine.py     →  for each of the 14 metrics, calculate it OR mark as a gap
        ↓
engine/gap_detector.py      →  turns "not measurable" results into explained gaps
        ↓
engine/scoring.py           →  works out the overall Measurement Coverage %
        ↓
ui/dashboard.py + ui/gaps.py → display everything to the user
```

Every arrow above is a real function call you can trace by reading `app.py`,
which decides which `ui/` screen to show and passes it the results from `engine/`.

## Part 3: Important files

| File | What it does |
|---|---|
| `app.py` | The entry point. Decides which screen to show based on `st.session_state.screen`. |
| `config/measurement_definitions.py` | The list of all 14 metrics we might want to measure, described as data. |
| `engine/data_loader.py` | Safely reads a CSV, validates required columns, never crashes on bad input. |
| `engine/data_profiler.py` | Looks at the loaded data and works out which events/columns are actually present. |
| `engine/metric_engine.py` | The deterministic calculator — no AI. Produces a `MetricResult` for every metric. |
| `engine/gap_detector.py` | Turns unmeasurable metrics into `MeasurementGap` objects with reasons and recommendations. |
| `engine/scoring.py` | Calculates the overall Measurement Coverage score and finds the biggest funnel drop-off. |
| `engine/ai_summary.py` | The *only* file that talks to an AI model. Entirely optional. |
| `ui/journey_builder.py` | The "Define Journey" screen. |
| `ui/upload.py` | The "Upload Data" screen. |
| `ui/dashboard.py` | The main dashboard: coverage score, funnel chart, stage table, findings. |
| `ui/gaps.py` | The measurement gaps, AI summary, and export screen. |
| `ui/components.py` | Small reusable bits of UI (badges, banners) shared across screens. |
| `utils/helpers.py` | The default journey definition, and building the Excel export file. |
| `generate_demo_data.py` | Creates the synthetic CSV files in `data/`. |

## Part 4: Important functions (plain English)

- **`load_csv(uploaded_file)`** (`data_loader.py`) — Try to read the file. If anything
  goes wrong (empty file, missing columns, unreadable dates), return a clear error
  message instead of crashing.

- **`profile_dataframe(dataframe)`** (`data_profiler.py`) — Look at the "event" column
  and work out which of our known event names (`product_view`, `cart_add`, etc.)
  actually show up.

- **`calculate_all_metrics(dataframe, profile)`** (`metric_engine.py`) — The main loop.
  For each of the 14 metric definitions, check if the data profile has what's needed.
  If yes, run the matching calculation function (e.g. `_calculate_stage_conversion`)
  and return a real value. If no, return a result marked "not measurable."

- **`_safe_percentage(numerator, denominator)`** (`metric_engine.py`) — Divides two
  numbers as a percentage, but returns `None` instead of crashing if the denominator
  is zero. This one function prevents a huge class of bugs.

- **`detect_gaps(metric_results, largest_dropoff_metric_id)`** (`gap_detector.py`) —
  Filters the metric results down to only the unmeasurable ones, and attaches
  recommended data and a priority to each.

- **`calculate_coverage_score(metric_results)`** (`scoring.py`) — Simple arithmetic:
  `(number measurable / total number of metrics) * 100`.

## Part 5: Important Python concepts used

- **Variables** — e.g. `customer_count = dataframe["customer_id"].nunique()` — a name
  that stores a value so we can use it again later.
- **Functions** — reusable blocks of code, like `_safe_percentage()`. We use small,
  focused functions throughout so each one is easy to test in isolation (see `tests/`).
- **Lists** — e.g. `MEASUREMENT_DEFINITIONS` is a list of dictionaries. We loop over
  it with `for definition in MEASUREMENT_DEFINITIONS:`.
- **Dictionaries** — e.g. each metric definition is a dictionary like
  `{"metric_id": "M002", "name": "Add-to-Cart Rate", ...}`. Dictionaries store data
  as labelled key/value pairs, which is why we can write `definition["name"]`.
- **Loops** — `for` loops appear everywhere we need to do the same thing to every
  item in a list (e.g. calculating every metric, or building every gap).
- **Conditions (`if`/`elif`/`else`)** — used constantly to branch behaviour, e.g.
  "if the required event exists, calculate it; otherwise, mark it as a gap."
- **Pandas DataFrames** — think of a DataFrame as a spreadsheet living in Python
  memory. `dataframe["event"]` grabs one column; `dataframe[dataframe["event"] ==
  "cart_add"]` filters to only the rows where that's true.
- **Filtering** — e.g. `dataframe[dataframe["event"] == "product_view"]` — keep only
  the rows matching a condition.
- **Grouping** — e.g. `dataframe["event"].value_counts()` — count how many rows fall
  into each category.
- **Functions returning values** — almost every engine function returns something
  (a number, a list, an object) rather than just printing it, so the calling code can
  use the result.
- **Imports** — e.g. `from config.measurement_definitions import
  MEASUREMENT_DEFINITIONS` — pulling code/data defined in one file into another.
- **Modules** — each `.py` file is a module. Folders like `engine/` and `ui/` are
  "packages" (a folder becomes a package when it contains an `__init__.py` file).

## Part 6: How to rebuild it

Don't copy this code. Instead, build your own version in roughly this order (see
`REBUILD_ROADMAP.md` for a week-by-week plan):

1. Write a tiny Python script that reads a CSV with pandas and prints its shape.
2. Add validation: what happens if a required column is missing?
3. Pick ONE metric (e.g. add-to-cart rate) and calculate it by hand from a small
   DataFrame you make up yourself, with print statements.
4. Generalise: write a list of metric definitions (start with 2-3, not 14) and a loop
   that calculates whichever ones it can.
5. Add the "gap" half: what happens when a metric *can't* be calculated? Return a
   clear reason instead of crashing.
6. Only once the calculation logic works and is tested, wrap it in a simple Streamlit
   UI — start with just `st.file_uploader()` and `st.write()`, then add polish.

Building the calculation logic first (and testing it without any UI at all) is the
single most valuable habit you can take from this project.

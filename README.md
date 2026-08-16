# Journey Measurement Analyzer

A working prototype that demonstrates a simple but important idea:

> **Having data is not the same thing as being able to measure everything you want to understand.**

This is a **proof-of-concept**, not an enterprise analytics platform. It uses a fictional
online retailer ("TechMart") and entirely synthetic (fake) data.

---

## 1. What this project is

You define a customer journey (e.g. "view a product → add to cart → checkout → pay →
receive delivery"), upload the event data your business currently collects, and the
application tells you:

- What you **can** currently measure from that data
- What you **cannot** currently measure, and **why**
- What additional data you'd need to collect to close each gap

## 2. What problem it demonstrates

Businesses often assume that because they have "a lot of data," they can measure
anything they want. In reality, most datasets only capture certain *events*
(e.g. "customer added a product to cart") and rarely capture the *reasons* behind
customer behaviour (e.g. "customer didn't add to cart because the price felt too high").

This app makes that gap visible and concrete, instead of leaving it as an abstract idea.

## 3. How the application works (high level)

```
Define Journey  →  Upload Data  →  Analyze  →  Dashboard  →  Measurement Gaps
```

1. **Define Journey** — name your journey and list its stages.
2. **Upload Data** — upload a CSV of customer events (or use a bundled demo dataset).
3. **Analyze** — a deterministic engine (no AI) checks each of 14 predefined metrics
   against the uploaded data.
4. **Dashboard** — see your overall "Measurement Coverage" score, a funnel chart, a
   stage-by-stage table, and the behavioural findings the data *does* support.
5. **Measurement Gaps** — see everything the data *cannot* currently tell you, why not,
   and what additional data would help. Optionally generate an AI-written summary, and
   export everything to an Excel report.

## 4. Installation

Requires Python 3.10+.

```bash
cd journey-measurement-analyzer
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 5. How to run it

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

On the **Upload Data** screen, pick one of the three bundled demo datasets from the
dropdown to try it immediately — no file of your own required.

### Optional: AI Business Summary

If you want the "Generate AI Business Summary" button on the Measurement Gaps screen
to work, copy `.env.example` to `.env` and add an OpenAI API key:

```bash
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=sk-...
pip install openai
```

Without a key, the app works exactly the same in every other respect — the AI button
is simply disabled with a clear explanation.

## 6. How the measurement engine works

The engine never guesses. For every metric defined in
`config/measurement_definitions.py`, it checks whether the uploaded data actually
contains the events/fields that metric needs:

- If **yes**, it performs a real calculation (e.g. `cart_add customers / product_view
  customers`) and shows the result.
- If **no**, it marks the metric as a **Measurement Gap** and explains exactly which
  event or column is missing.

This means the app can never fabricate a number. See `engine/metric_engine.py`.

## 7. What the synthetic dataset represents

`generate_demo_data.py` simulates ~1,000-1,600 fictional customers moving through the
TechMart journey stage by stage, with realistic drop-off probabilities at each step
(not every customer behaves identically). Three versions are bundled in `data/`:

| File | Scenario |
|---|---|
| `demo_online_shopping_data.csv` | **Normal.** Core funnel events only — intentional gaps around *why* customers behave as they do. |
| `demo_online_shopping_data_better.csv` | **Better data.** Adds satisfaction/reason fields — measurement coverage jumps to 100%. |
| `demo_online_shopping_data_poor.csv` | **Poor data.** Fewer events and columns tracked — more gaps appear. |

Regenerate them anytime with:

```bash
python3 generate_demo_data.py
```

No real customer, payment, or business data is used anywhere in this project.

## 8. How to add a new measurement definition

Open `config/measurement_definitions.py` and add a new dictionary to
`MEASUREMENT_DEFINITIONS`, e.g.:

```python
{
    "metric_id": "M015",
    "name": "Repeat Purchase Rate",
    "description": "Percentage of customers who purchased more than once.",
    "category": "Retention",
    "priority": "Medium",
    "required_events": ["payment_success"],
    "required_fields": [],
    "calculation_type": "stage_conversion",  # or add a new calculation_type
    "from_event": "...",
    "to_event": "...",
}
```

If it needs a new *kind* of calculation, add a small function for it in
`engine/metric_engine.py` and register it in the `if/elif` block inside
`calculate_all_metrics()`.

## 9. How the gap detection works

`engine/gap_detector.py` looks at every metric the engine marked as "not measurable"
and turns it into a `MeasurementGap`: a plain-language reason, a list of recommended
additional data to collect, and a priority (High/Medium/Low) based on simple, visible
rules — see `engine/scoring.py`'s `find_largest_dropoff()` and
`gap_detector._priority_for_gap()`. There is no machine learning involved.

## 10. How the optional AI layer works

Only `engine/ai_summary.py` touches an AI model. It is given the numbers the
deterministic engine already calculated and asked only to phrase them as a short
paragraph — it is explicitly instructed not to invent figures or guess at causes.
If no API key is set, this feature is simply disabled.

## 11. Limitations

- Uses **synthetic data only** — never connects to any real business system.
- Does **not** prove causal relationships (e.g. it will never claim customers left
  "because of price" unless the data literally contains that reason).
- Gap prioritisation uses simple, transparent rules — not statistical modelling.
- This is a concept demonstration, not a production analytics system.

## 12. Possible future enterprise development

The Home screen includes a "Future Enterprise Capabilities" section (deliberately
non-functional) sketching out what a full product might eventually include: real-time
pipelines, multi-journey support, customer segmentation, role-based access, and so on.

---

See also: **`LEARNING_GUIDE.md`** (how the code works, for study) and
**`REBUILD_ROADMAP.md`** (a suggested 2-3 week plan to rebuild this yourself).

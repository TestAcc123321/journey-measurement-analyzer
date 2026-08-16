# Rebuild Roadmap (2-3 Weeks)

Goal: rebuild a simplified version of this project **without copying the existing
code**. Look at this prototype only to check your understanding after you've tried
something yourself, not as a template to retype.

Treat each day as roughly 1-2 hours. Adjust freely — this is a guide, not a contract.

---

## Week 1 — Foundations: reading data and understanding the domain

**Day 1-2: Python & pandas refresher**
- Variables, functions, lists, dictionaries, loops, conditions.
- Load any small CSV with `pandas.read_csv()` and explore it: `.shape`, `.columns`,
  `.head()`, `.dtypes`.

**Day 3: CSV loading with validation**
- Write a function `load_csv(path)` that reads a file and checks that specific
  required columns exist. Return a clear message if they don't.
- Test it against a good CSV, an empty CSV, and a CSV missing a column.

**Day 4: Filtering and grouping in pandas**
- Practice: `df[df["event"] == "cart_add"]`, `df["customer_id"].nunique()`,
  `df["event"].value_counts()`.
- Try answering a question like "how many unique customers added something to
  their cart?" using only these tools.

**Day 5: Journey definition**
- Write a small function or class representing "a journey": a name and an ordered
  list of stages (just a Python list of strings is fine to start).

**Day 6-7: Streamlit basics**
- Install Streamlit. Build a one-page app with `st.title`, `st.file_uploader`,
  `st.dataframe`. Get comfortable with the idea that Streamlit re-runs your whole
  script every time the user interacts with something.

---

## Week 2 — The measurement engine

**Day 8: Pick ONE metric**
- By hand, calculate "add-to-cart rate" from a small DataFrame you type out yourself
  (5-10 rows). Confirm your code's answer matches what you calculated on paper.

**Day 9: Generalise to a metric definition**
- Represent that one metric as a dictionary: name, required events, description.
  Write a function that checks whether a DataFrame has those events, and if so,
  calculates the metric.

**Day 10: Add 2-3 more metrics**
- Add cart-to-checkout rate and payment success rate. Notice which parts of your
  code you can reuse rather than duplicating.

**Day 11: Handle the "can't calculate" case**
- What happens if a required event is missing? Make sure your code returns a clear
  explanation rather than crashing (watch out for division by zero!).

**Day 12: Build a small measurement definitions list**
- Put 5-6 metric dictionaries in a list. Write a loop that calculates every one it
  can and reports a gap for every one it can't.

**Day 13: Simple charts**
- Use Plotly (or even just `st.bar_chart`) to show one metric visually.

**Day 14: Review**
- Compare your approach to `engine/metric_engine.py` in this prototype. Where did
  you do something differently? Is your way simpler or more complex? Either is fine
  — the goal is understanding, not matching this code exactly.

---

## Week 3 — Polish, gaps, testing, and (optional) AI

**Day 15: Gap detection & recommendations**
- For each unmeasurable metric, attach a short list of "data you could collect
  instead." A plain Python dictionary lookup is enough — no AI needed here.

**Day 16: Priority rules**
- Write simple, explainable rules for whether a gap is High/Medium/Low priority.
  Keep it to a few `if` statements you could explain out loud to someone else.

**Day 17: A coverage score**
- Calculate `(measurable metrics / total metrics) * 100` and display it.

**Day 18: Testing**
- Write a few test functions (see `tests/` in this project for examples) that check
  your metric calculations against hand-computed expected values.

**Day 19: Error handling pass**
- Deliberately try to break your own app: empty file, missing columns, all-zero
  denominators, weird data types. Fix whatever crashes.

**Day 20: Optional AI layer**
- If you want to try it, write ONE function that takes your already-calculated
  numbers and asks an AI model to phrase them as a paragraph. Make sure your app
  still works completely if that function is never called.

**Day 21: Rebuild independently**
- Without looking at this prototype's code, try adding one new metric of your own
  choosing (e.g. "review rate") end-to-end: definition → calculation → gap handling
  → display. If you can do this smoothly, you've genuinely learned the pattern.

---

## After the roadmap

Once you're comfortable, try extending your version in a direction this prototype
deliberately left out — e.g. supporting more than one journey at a time, or reading
data from more than one file. That's a good bridge into the "Future Enterprise
Capabilities" ideas shown on the Home screen of this prototype.

"""
measurement_definitions.py

This file is the "brain" of what the application WANTS to measure.

Instead of writing a separate Python function for every single metric,
we describe each metric as a dictionary (a set of key/value pairs).
The measurement engine (see engine/metric_engine.py) then reads this
list and decides, for each metric, whether it can be calculated from
the data that was uploaded.

Why do it this way?
--------------------
If we hard-coded 14 separate "calculate_this_metric()" functions with
no shared structure, adding a 15th metric later would mean writing a
lot of new, mostly-repeated code. By describing metrics as data
(a list of dictionaries), we can add a new metric just by adding a
new dictionary to this list. The engine already knows how to handle
any metric that follows this shape.

Each metric definition contains:
    metric_id        - a short unique code, e.g. "M001"
    name              - human-readable name shown in the UI
    description       - one sentence explaining what the metric means
    category          - groups metrics together (e.g. "Conversion")
    priority          - how important this metric is if it turns out
                         to be a measurement gap ("High", "Medium", "Low")
    required_events   - which event names (from the event column) must
                         be present in the uploaded data for this metric
                         to be calculable. An empty list means the
                         metric instead depends on a required_field.
    required_fields   - which optional COLUMNS must exist in the data
                         (used for metrics like "Customer Satisfaction"
                         that depend on a field rather than an event)
    calculation_type  - tells the metric engine which calculation
                         "recipe" to use (see engine/metric_engine.py)
"""

# The full list of events we might see in the "event" column of the
# uploaded data. This is used elsewhere (data_profiler.py) to check
# which of these events are actually present in a given file.
KNOWN_EVENTS = [
    "product_discovery",
    "product_view",
    "cart_add",
    "checkout_start",
    "payment_attempt",
    "payment_success",
    "payment_failure",
    "order_confirmation",
    "delivery",
    "return",
    "review",
]

# Optional columns that are NOT part of the core event log, but which
# would unlock additional metrics if they existed in the uploaded data.
OPTIONAL_ENRICHMENT_FIELDS = [
    "customer_satisfaction",
    "abandonment_reason",
    "purchase_reason",
    "delivery_satisfaction",
]

MEASUREMENT_DEFINITIONS = [
    {
        "metric_id": "M001",
        "name": "Product View Volume",
        "description": "How many unique customers viewed at least one product.",
        "category": "Reach",
        "priority": "Low",
        "required_events": ["product_view"],
        "required_fields": [],
        "calculation_type": "unique_customer_count",
    },
    {
        "metric_id": "M002",
        "name": "Add-to-Cart Rate",
        "description": "Percentage of product viewers who added a product to their cart.",
        "category": "Conversion",
        "priority": "High",
        "required_events": ["product_view", "cart_add"],
        "required_fields": [],
        "calculation_type": "stage_conversion",
        "from_event": "product_view",
        "to_event": "cart_add",
    },
    {
        "metric_id": "M003",
        "name": "Cart-to-Checkout Rate",
        "description": "Percentage of customers with a cart addition who reached checkout.",
        "category": "Conversion",
        "priority": "High",
        "required_events": ["cart_add", "checkout_start"],
        "required_fields": [],
        "calculation_type": "stage_conversion",
        "from_event": "cart_add",
        "to_event": "checkout_start",
    },
    {
        "metric_id": "M004",
        "name": "Checkout Completion Rate",
        "description": "Percentage of customers who started checkout and attempted payment.",
        "category": "Conversion",
        "priority": "High",
        "required_events": ["checkout_start", "payment_attempt"],
        "required_fields": [],
        "calculation_type": "stage_conversion",
        "from_event": "checkout_start",
        "to_event": "payment_attempt",
    },
    {
        "metric_id": "M005",
        "name": "Payment Success Rate",
        "description": "Percentage of payment attempts that succeeded.",
        "category": "Conversion",
        "priority": "High",
        "required_events": ["payment_attempt", "payment_success"],
        "required_fields": [],
        "calculation_type": "event_ratio",
        "numerator_event": "payment_success",
        "denominator_event": "payment_attempt",
    },
    {
        "metric_id": "M006",
        "name": "Cart Abandonment Rate",
        "description": "Percentage of customers who added a product to cart but never reached checkout.",
        "category": "Drop-off",
        "priority": "High",
        "required_events": ["cart_add", "checkout_start"],
        "required_fields": [],
        "calculation_type": "abandonment",
        "from_event": "cart_add",
        "to_event": "checkout_start",
    },
    {
        "metric_id": "M007",
        "name": "Payment Failure Rate",
        "description": "Percentage of payment attempts that failed.",
        "category": "Drop-off",
        "priority": "Medium",
        "required_events": ["payment_attempt", "payment_failure"],
        "required_fields": [],
        "calculation_type": "event_ratio",
        "numerator_event": "payment_failure",
        "denominator_event": "payment_attempt",
    },
    {
        "metric_id": "M008",
        "name": "Order Completion Rate",
        "description": "Percentage of successful payments that resulted in a confirmed order.",
        "category": "Fulfilment",
        "priority": "Medium",
        "required_events": ["payment_success", "order_confirmation"],
        "required_fields": [],
        "calculation_type": "stage_conversion",
        "from_event": "payment_success",
        "to_event": "order_confirmation",
    },
    {
        "metric_id": "M009",
        "name": "Delivery Completion Rate",
        "description": "Percentage of confirmed orders that were delivered.",
        "category": "Fulfilment",
        "priority": "Medium",
        "required_events": ["order_confirmation", "delivery"],
        "required_fields": [],
        "calculation_type": "stage_conversion",
        "from_event": "order_confirmation",
        "to_event": "delivery",
    },
    {
        "metric_id": "M010",
        "name": "Return Rate",
        "description": "Percentage of delivered orders that were later returned.",
        "category": "Post-purchase",
        "priority": "Medium",
        "required_events": ["delivery", "return"],
        "required_fields": [],
        "calculation_type": "stage_conversion",
        "from_event": "delivery",
        "to_event": "return",
    },
    {
        "metric_id": "M011",
        "name": "Customer Satisfaction",
        "description": "Average reported customer satisfaction after purchase.",
        "category": "Experience",
        "priority": "Medium",
        "required_events": [],
        "required_fields": ["customer_satisfaction"],
        "calculation_type": "field_average",
        "field": "customer_satisfaction",
    },
    {
        "metric_id": "M012",
        "name": "Abandonment Reason",
        "description": "The stated reasons customers give for abandoning a cart or checkout.",
        "category": "Experience",
        "priority": "High",
        "required_events": [],
        "required_fields": ["abandonment_reason"],
        "calculation_type": "field_breakdown",
        "field": "abandonment_reason",
    },
    {
        "metric_id": "M013",
        "name": "Purchase Reason",
        "description": "The stated reasons customers give for completing a purchase.",
        "category": "Experience",
        "priority": "Low",
        "required_events": [],
        "required_fields": ["purchase_reason"],
        "calculation_type": "field_breakdown",
        "field": "purchase_reason",
    },
    {
        "metric_id": "M014",
        "name": "Delivery Satisfaction",
        "description": "Average reported satisfaction with the delivery experience.",
        "category": "Experience",
        "priority": "Low",
        "required_events": [],
        "required_fields": ["delivery_satisfaction"],
        "calculation_type": "field_average",
        "field": "delivery_satisfaction",
    },
]


def get_definition(metric_id):
    """Look up a single metric definition by its metric_id. Returns None if not found."""
    for definition in MEASUREMENT_DEFINITIONS:
        if definition["metric_id"] == metric_id:
            return definition
    return None

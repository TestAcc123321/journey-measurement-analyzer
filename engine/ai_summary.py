"""
ai_summary.py

This is the ONLY file in the whole application that talks to an AI
model, and it is entirely optional. Every number the AI is given
comes from the deterministic engine (metric_engine.py, scoring.py) -
the AI's job is only to turn those numbers into a readable paragraph.
It is never asked to calculate anything itself.

If no API key is configured, `is_ai_available()` returns False and
the rest of the app simply hides the "Generate AI Business Summary"
button - nothing else breaks.
"""

import os


def is_ai_available():
    """Check whether an OpenAI API key has been configured."""
    return bool(os.environ.get("OPENAI_API_KEY"))


def _build_prompt(journey, coverage, gaps, largest_dropoff):
    """
    Build the text prompt sent to the AI. Notice that every number
    here (coverage score, gap count, drop-off percentage) was already
    calculated by the deterministic engine - we are only asking the
    AI to phrase it, not compute it.
    """
    from_stage, to_stage, dropoff_percent = largest_dropoff
    top_gap_names = ", ".join(gap.name for gap in gaps[:5]) if gaps else "none"

    prompt = f"""You are summarising a customer journey measurement analysis for a business audience.
Use ONLY the facts given below. Do not invent any numbers, causes, or customer motivations
that are not explicitly stated. Where the data cannot explain something, say so plainly.

Journey: {journey['name']} ({journey['business']})
Measurement Coverage: {coverage['score']}%
Measurable metrics: {coverage['measurable_count']} of {coverage['total']}
Measurement gaps: {coverage['total'] - coverage['measurable_count']}
Largest observed drop-off: {from_stage} -> {to_stage} ({dropoff_percent}% did not continue)
Top measurement gaps: {top_gap_names}

Write a concise (3-5 sentence) business-friendly summary. Clearly separate what the data
shows from what the data cannot currently explain. Do not use the word "probably" to guess
at customer motivations - only state that the reason is currently unknown."""
    return prompt


def generate_summary(journey, coverage, gaps, largest_dropoff):
    """
    Call the OpenAI API to produce a natural-language summary.

    Returns (success: bool, text: str). On any failure (missing key,
    network error, API error), returns success=False and a clear
    explanation - never raises an exception up into the UI layer.
    """
    if not is_ai_available():
        return False, "No OpenAI API key is configured. Set OPENAI_API_KEY in your .env file to enable this feature."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        prompt = _build_prompt(journey, coverage, gaps, largest_dropoff)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        summary_text = response.choices[0].message.content.strip()
        return True, summary_text
    except ImportError:
        return False, "The 'openai' package is not installed. Run: pip install openai"
    except Exception as error:
        return False, f"The AI summary could not be generated ({type(error).__name__}). The rest of the app is unaffected."

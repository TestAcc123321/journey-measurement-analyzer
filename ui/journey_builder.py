"""
journey_builder.py

Screen 2 of the app: lets the user define (or accept the default)
customer journey - a name, the business it belongs to, a description,
and an ordered list of stages.

All of this is stored in st.session_state so it persists as the user
navigates between screens (Streamlit re-runs the whole script on
every interaction, so anything that needs to survive that must live
in session_state rather than a plain local variable).
"""

import streamlit as st
from utils.helpers import default_journey
from ui.components import prototype_banner, section_header


def render():
    prototype_banner()
    st.title("Define Your Journey")
    section_header(
        "Journey Builder",
        "Describe the customer journey you want to understand, and list its stages in order.",
    )

    if "journey" not in st.session_state:
        st.session_state.journey = default_journey()

    journey = st.session_state.journey

    journey["name"] = st.text_input("Journey Name", value=journey["name"])
    journey["business"] = st.text_input("Business / Example", value=journey["business"])
    journey["description"] = st.text_area("Journey Description", value=journey["description"], height=80)

    st.markdown("#### Journey Stages")
    st.caption("Add, rename, reorder, or remove stages below.")

    stages = journey["stages"]

    for index, stage in enumerate(stages):
        col_text, col_up, col_down, col_remove = st.columns([6, 1, 1, 1])
        with col_text:
            stages[index] = st.text_input(f"Stage {index + 1}", value=stage, key=f"stage_{index}", label_visibility="collapsed")
        with col_up:
            if st.button("↑", key=f"up_{index}", disabled=(index == 0)):
                stages[index - 1], stages[index] = stages[index], stages[index - 1]
                st.rerun()
        with col_down:
            if st.button("↓", key=f"down_{index}", disabled=(index == len(stages) - 1)):
                stages[index + 1], stages[index] = stages[index], stages[index + 1]
                st.rerun()
        with col_remove:
            if st.button("✕", key=f"remove_{index}", disabled=(len(stages) <= 1)):
                stages.pop(index)
                st.rerun()

    if st.button("+ Add Stage"):
        stages.append(f"Stage {len(stages) + 1}")
        st.rerun()

    st.session_state.journey["stages"] = stages

    st.divider()
    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Back to Home"):
            st.session_state.screen = "home"
            st.rerun()
    with col_next:
        if st.button("Continue to Data →", type="primary"):
            st.session_state.screen = "upload"
            st.rerun()

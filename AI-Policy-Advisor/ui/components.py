"""ui/components.py — reusable Streamlit UI components for the dashboard."""

import streamlit as st


def metric_row(metrics: dict):
    """Render a row of st.metric() cards from a dict of {label: value}."""
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label, value)


def section_card(title: str, content: str):
    """Render a titled markdown card for one agent's output section."""
    with st.container(border=True):
        st.subheader(title)
        st.markdown(content if content else "_No content generated._")


def progress_steps(current_step: int, steps: list):
    """Render a simple progress bar labeled with the current pipeline step."""
    progress = current_step / len(steps)
    st.progress(progress, text=f"Step {current_step}/{len(steps)}: {steps[current_step - 1]}")

from datetime import date

import streamlit as st

from workout_app import db
from workout_app.cards import CARD_QUEUE
from workout_app.rotation import next_card
from workout_app.rotation_models import CommitmentOverride, CommitmentSchedule
from workout_app.streamlit_data import (
    get_client,
    load_all_sessions,
    load_rotation_state,
    load_commitment_overrides,
)

client = get_client()

all_sessions = load_all_sessions(client)
rotation_state = load_rotation_state(client)
overrides = load_commitment_overrides(client)
commitment_schedule = CommitmentSchedule(overrides=overrides)

st.title("Gym Sensai")

st.subheader("Today")
st.caption(date.today().strftime("%A, %d %B %Y"))
result = next_card(rotation_state, CARD_QUEUE, commitment_schedule, date.today())
today_card = result["card"]
if result["caution"]:
    st.warning(result["caution"])

if commitment_schedule.has_commitment_on(date.today()):
    if st.button("I skipped my sport session today", use_container_width=True):
        db.save_commitment_override(client, CommitmentOverride(on_date=date.today(), has_commitment=False))
        load_commitment_overrides.clear()
        st.rerun()

if st.button(f"Go to today's session: {today_card.name}", type="primary", use_container_width=True):
    st.switch_page("views/session.py")

st.divider()

st.subheader("Last session")
if all_sessions:
    last = max(all_sessions, key=lambda s: s.session_date)
    with st.container(border=True):
        st.markdown(f"**{last.session_day}** · {last.session_date.strftime('%d %b %Y')}")
        for se in last.exercises:
            st.caption(se.exercise_name)
else:
    st.caption("No sessions logged yet — head to Session to log your first one.")

st.divider()

st.subheader("Personal bests")
with st.container(border=True):
    st.caption("Coming soon — best weight and reps per exercise across your history.")

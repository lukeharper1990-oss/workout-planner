"""Cached Supabase access shared across every page. Streamlit reruns the
current page's whole script on every widget interaction (typing a rep
count, ticking a set done, moving a pill) — without caching this would mean
a fresh Supabase round-trip, including the full session history, on every
single keystroke. No TTL: each of these is explicitly cleared at its own
write site (session.py's FINISH button, the sport-status save), so there's
nothing to go stale between writes — no need to eat a network round-trip on
a timer in between."""

import streamlit as st

from workout_app import db


@st.cache_resource
def get_client():
    return db.get_client(url=st.secrets["SUPABASE_URL"], key=st.secrets["SUPABASE_KEY"])


@st.cache_data
def load_rotation_state(_client):
    return db.load_rotation_state(_client)


@st.cache_data
def load_commitment_overrides(_client):
    return db.load_commitment_overrides(_client)


@st.cache_data
def load_all_sessions(_client):
    return db.load_all_sessions(_client)


@st.cache_data
def load_user_preferences(_client):
    return db.load_user_preferences(_client)

import streamlit as st

st.set_page_config(page_title="Gym Sensai", page_icon="static/icon.png", layout="centered")

# --- Home-screen icon / app-like feel on iOS/Android ---
# NOTE: not yet verified on a real phone. Streamlit injects this inside the
# app's own frame, not necessarily the outer document head, so "Add to Home
# Screen" picking this up correctly needs testing on an actual device.
# Served via server.enableStaticServing (see .streamlit/config.toml) rather
# than inlined as a data URI — the source icon is ~1.2MB, and a data URI
# would re-embed that in the page HTML on every single rerun.
st.markdown(
    """
    <link rel="apple-touch-icon" href="/app/static/icon.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="Gym Sensai">
    <meta name="mobile-web-app-capable" content="yes">
    """,
    unsafe_allow_html=True,
)

dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏠", default=True)
session_page = st.Page("views/session.py", title="Session", icon="🏋️")

# Top tabs rather than the sidebar default — on a narrow phone the sidebar
# collapses behind a hamburger tap, which is one extra tap on every single
# page load for what's meant to be a quick, phone-first, two-page app.
pg = st.navigation([dashboard_page, session_page], position="top")
pg.run()

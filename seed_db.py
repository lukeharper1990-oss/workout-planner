"""One-off script to push the real seed sessions into Supabase. Run once."""

import tomllib
from pathlib import Path

from workout_app import db
from workout_app.seed_data import ALL_SESSIONS

secrets = tomllib.loads((Path(__file__).parent / ".streamlit" / "secrets.toml").read_text())
client = db.get_client(url=secrets["SUPABASE_URL"], key=secrets["SUPABASE_KEY"])

for session in ALL_SESSIONS:
    db.save_session(client, session)
    print(f"Saved {session.session_day} ({session.session_date})")

print("Done.")

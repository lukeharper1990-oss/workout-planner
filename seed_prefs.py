"""One-off script to push local preferences into Supabase. Run once."""

import tomllib
from pathlib import Path

from workout_app import db
from workout_app.users import load_user_preferences

secrets = tomllib.loads((Path(__file__).parent / ".streamlit" / "secrets.toml").read_text())
client = db.get_client(url=secrets["SUPABASE_URL"], key=secrets["SUPABASE_KEY"])

prefs = load_user_preferences(Path(__file__).parent / "data" / "users" / "example.json")
for pref in prefs.values():
    db.save_user_preference(client, pref)
    print(f"Saved preference: {pref.exercise_name}")

print("Done.")

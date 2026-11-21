from pathlib import Path

from workout_app.cards import CARD_QUEUE
from workout_app.progression import recommend_next
from workout_app.seed_data import ALL_SESSIONS
from workout_app.users import load_user_preferences

user_prefs = load_user_preferences(Path(__file__).parent / "data" / "users" / "example.json")

for card in CARD_QUEUE:
    print(f"\nNext {card.name}:\n")
    for ce in card.exercises:
        rec = recommend_next(ce.exercise_name, ALL_SESSIONS, ce.rep_range, user_preferences=user_prefs)
        print(f"{ce.exercise_name}: {rec}")

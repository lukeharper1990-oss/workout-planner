import json
from pathlib import Path

from workout_app.models import UserExercisePreference


def load_user_preferences(path: str | Path) -> dict[str, UserExercisePreference]:
    data = json.loads(Path(path).read_text())
    return {
        entry["exercise_name"]: UserExercisePreference(**entry) for entry in data
    }

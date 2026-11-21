from workout_app.models import Exercise, UserExercisePreference

# Universal exercise catalog. Substitute pairings here are general
# movement-equivalence facts (e.g. a machine chest press is a reasonable
# substitute for a dumbbell press), not any one user's preference. Personal
# exclusions and access constraints live in per-user preference files
# (see workout_app.users).

CATALOG: list[Exercise] = [
    # --- Push: chest, shoulders, triceps ---
    Exercise(
        name="Bench Press",
        muscle_groups=["chest", "triceps", "shoulders"],
        category="push",
        equipment="barbell",
        substitutes=["Chest Press Machine"],
    ),
    Exercise(
        name="Chest Press Machine",
        muscle_groups=["chest", "triceps", "shoulders"],
        category="push",
        equipment="machine",
        substitutes=["Bench Press"],
    ),
    Exercise(
        name="Incline Barbell Press",
        muscle_groups=["chest", "shoulders", "triceps"],
        category="push",
        equipment="barbell",
        substitutes=["Chest Press Machine"],
    ),
    Exercise(
        name="Incline Dumbbell Press",
        muscle_groups=["chest", "shoulders", "triceps"],
        category="push",
        equipment="dumbbell",
        substitutes=["Chest Press Machine"],
    ),
    Exercise(
        name="Dumbbell Chest Fly",
        muscle_groups=["chest"],
        category="push",
        equipment="dumbbell",
        substitutes=["Cable Chest Fly", "Pec Deck"],
    ),
    Exercise(
        name="Cable Chest Fly",
        muscle_groups=["chest"],
        category="push",
        equipment="machine",
        substitutes=["Dumbbell Chest Fly", "Pec Deck"],
    ),
    Exercise(
        name="Pec Deck",
        muscle_groups=["chest"],
        category="push",
        equipment="machine",
        substitutes=["Dumbbell Chest Fly", "Cable Chest Fly"],
    ),
    Exercise(
        name="Push-Up",
        muscle_groups=["chest", "triceps", "shoulders"],
        category="push",
        equipment="bodyweight",
        substitutes=["Chest Press Machine"],
    ),
    Exercise(
        name="Overhead Press",
        muscle_groups=["shoulders", "triceps"],
        category="push",
        equipment="barbell",
        substitutes=["Dumbbell Shoulder Press", "Machine Shoulder Press"],
    ),
    Exercise(
        name="Dumbbell Shoulder Press",
        muscle_groups=["shoulders", "triceps"],
        category="push",
        equipment="dumbbell",
        substitutes=["Overhead Press", "Machine Shoulder Press"],
    ),
    Exercise(
        name="Machine Shoulder Press",
        muscle_groups=["shoulders", "triceps"],
        category="push",
        equipment="machine",
        substitutes=["Overhead Press", "Dumbbell Shoulder Press"],
    ),
    Exercise(
        name="Dumbbell Lateral Raise",
        muscle_groups=["shoulders"],
        category="push",
        equipment="dumbbell",
        substitutes=["Cable Lateral Raise"],
    ),
    Exercise(
        name="Cable Lateral Raise",
        muscle_groups=["shoulders"],
        category="push",
        equipment="machine",
        substitutes=["Dumbbell Lateral Raise"],
    ),
    Exercise(
        name="Tricep Pushdown",
        muscle_groups=["triceps"],
        category="push",
        equipment="machine",
        substitutes=["Overhead Tricep Extension", "Skull Crusher"],
    ),
    Exercise(
        name="Overhead Tricep Extension",
        muscle_groups=["triceps"],
        category="push",
        equipment="dumbbell",
        substitutes=["Tricep Pushdown", "Skull Crusher"],
    ),
    Exercise(
        name="Skull Crusher",
        muscle_groups=["triceps"],
        category="push",
        equipment="barbell",
        substitutes=["Tricep Pushdown", "Overhead Tricep Extension"],
    ),
    Exercise(
        name="Dip",
        muscle_groups=["chest", "triceps", "shoulders"],
        category="push",
        equipment="bodyweight",
        substitutes=["Chest Press Machine", "Tricep Pushdown"],
    ),
    # --- Pull: back, biceps, rear delts ---
    Exercise(
        name="Deadlift",
        muscle_groups=["hamstrings", "glutes", "back"],
        category="pull",
        equipment="barbell",
        substitutes=["Romanian Deadlift"],
    ),
    Exercise(
        name="Romanian Deadlift",
        muscle_groups=["hamstrings", "glutes"],
        category="pull",
        equipment="barbell",
        substitutes=["Deadlift"],
    ),
    Exercise(
        name="Barbell Row",
        muscle_groups=["back", "biceps"],
        category="pull",
        equipment="barbell",
        substitutes=["Seated Cable Row", "Dumbbell Row"],
    ),
    Exercise(
        name="Dumbbell Row",
        muscle_groups=["back", "biceps"],
        category="pull",
        equipment="dumbbell",
        substitutes=["Seated Cable Row", "Barbell Row"],
    ),
    Exercise(
        name="Seated Cable Row",
        muscle_groups=["back", "biceps"],
        category="pull",
        equipment="machine",
        substitutes=["Barbell Row", "Dumbbell Row", "T-Bar Row"],
    ),
    Exercise(
        name="T-Bar Row",
        muscle_groups=["back", "biceps"],
        category="pull",
        equipment="machine",
        substitutes=["Barbell Row", "Dumbbell Row", "Seated Cable Row"],
    ),
    Exercise(
        name="Lat Pulldown",
        muscle_groups=["back", "biceps"],
        category="pull",
        equipment="machine",
        substitutes=["Pull-Up"],
    ),
    Exercise(
        name="Pull-Up",
        muscle_groups=["back", "biceps"],
        category="pull",
        equipment="bodyweight",
        substitutes=["Lat Pulldown"],
    ),
    Exercise(
        name="Face Pull",
        muscle_groups=["shoulders", "back"],
        category="pull",
        equipment="machine",
    ),
    Exercise(
        name="Barbell Bicep Curl",
        muscle_groups=["biceps"],
        category="pull",
        equipment="barbell",
        substitutes=["Dumbbell Bicep Curl", "Cable Bicep Curl"],
    ),
    Exercise(
        name="Dumbbell Bicep Curl",
        muscle_groups=["biceps"],
        category="pull",
        equipment="dumbbell",
        substitutes=["Barbell Bicep Curl", "Cable Bicep Curl", "Hammer Curl"],
    ),
    Exercise(
        name="Cable Bicep Curl",
        muscle_groups=["biceps"],
        category="pull",
        equipment="machine",
        substitutes=["Barbell Bicep Curl", "Dumbbell Bicep Curl"],
    ),
    Exercise(
        name="Hammer Curl",
        muscle_groups=["biceps"],
        category="pull",
        equipment="dumbbell",
        substitutes=["Dumbbell Bicep Curl"],
    ),
    # --- Legs: quads, hamstrings, glutes, calves ---
    Exercise(
        name="Back Squat",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="barbell",
    ),
    Exercise(
        name="Front Squat",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="barbell",
    ),
    Exercise(
        name="Goblet Squat",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="dumbbell",
        substitutes=["Leg Press"],
    ),
    Exercise(
        name="Zercher Squat",
        muscle_groups=["quads", "glutes", "back"],
        category="legs",
        equipment="barbell",
        substitutes=["Front Squat", "Back Squat"],
    ),
    Exercise(
        name="Bulgarian Split Squat",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="dumbbell",
        substitutes=["Walking Lunge"],
    ),
    Exercise(
        name="Leg Press",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="machine",
        substitutes=["Hack Squat", "Back Squat"],
    ),
    Exercise(
        name="Hack Squat",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="machine",
        substitutes=["Leg Press", "Back Squat"],
    ),
    Exercise(
        name="Walking Lunge",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="dumbbell",
        substitutes=["Bulgarian Split Squat"],
    ),
    Exercise(
        name="Leg Extension",
        muscle_groups=["quads"],
        category="legs",
        equipment="machine",
    ),
    Exercise(
        name="Leg Curl",
        muscle_groups=["hamstrings"],
        category="legs",
        equipment="machine",
        substitutes=["Romanian Deadlift"],
    ),
    Exercise(
        name="Hip Abduction",
        muscle_groups=["glutes", "hips"],
        category="legs",
        equipment="machine",
    ),
    Exercise(
        name="Hip Adduction",
        muscle_groups=["hips"],
        category="legs",
        equipment="machine",
    ),
    Exercise(
        name="Glute Bridge",
        muscle_groups=["glutes"],
        category="legs",
        equipment="barbell",
    ),
    Exercise(
        name="Standing Calf Raise",
        muscle_groups=["calves"],
        category="legs",
        equipment="machine",
        substitutes=["Seated Calf Raise", "Dumbbell Calf Raise"],
    ),
    Exercise(
        name="Seated Calf Raise",
        muscle_groups=["calves"],
        category="legs",
        equipment="machine",
        substitutes=["Standing Calf Raise", "Dumbbell Calf Raise"],
    ),
    Exercise(
        name="Dumbbell Calf Raise",
        muscle_groups=["calves"],
        category="legs",
        equipment="dumbbell",
        substitutes=["Standing Calf Raise", "Seated Calf Raise"],
    ),
    # Sled/carry work — genuinely new movement pattern for this catalog, not
    # a variant of anything already in it.
    Exercise(
        name="Sled Push",
        muscle_groups=["quads", "glutes"],
        category="legs",
        equipment="sled",
    ),
    Exercise(
        name="Sled Pull",
        muscle_groups=["hamstrings", "glutes", "back"],
        category="legs",
        equipment="sled",
        substitutes=["Sled Push"],
    ),
    # Carries are inherently distance-based (a fixed load walked N meters),
    # unlike sled work which can reasonably be counted as reps of pushes.
    Exercise(
        name="Farmer's Carry",
        muscle_groups=["back", "core", "hips"],
        category="legs",
        equipment="dumbbell",
        logging_unit="meters",
    ),
    # --- Core ---
    Exercise(
        name="Neck Work",
        muscle_groups=["neck"],
        category="core",
        equipment="dumbbell",
    ),
    Exercise(
        name="Plank",
        muscle_groups=["core"],
        category="core",
        equipment="bodyweight",
    ),
    Exercise(
        name="Cable Crunch",
        muscle_groups=["core"],
        category="core",
        equipment="machine",
        substitutes=["Hanging Leg Raise"],
    ),
    Exercise(
        name="Hanging Leg Raise",
        muscle_groups=["core"],
        category="core",
        equipment="bodyweight",
        substitutes=["Cable Crunch"],
    ),
    Exercise(
        name="Russian Twist",
        muscle_groups=["core"],
        category="core",
        equipment="bodyweight",
    ),
    Exercise(
        name="Ab Wheel Rollout",
        muscle_groups=["core"],
        category="core",
        equipment="bodyweight",
    ),
    # --- Cardio ---
    Exercise(
        name="Incline Treadmill Walk",
        muscle_groups=["cardio"],
        category="cardio",
        equipment="treadmill",
        substitutes=["Flat Treadmill Run", "Stationary Bike", "Rowing Machine"],
    ),
    Exercise(
        name="Flat Treadmill Run",
        muscle_groups=["cardio"],
        category="cardio",
        equipment="treadmill",
        substitutes=["Incline Treadmill Walk"],
    ),
    Exercise(
        name="Stationary Bike",
        muscle_groups=["cardio"],
        category="cardio",
        equipment="machine",
        substitutes=["Incline Treadmill Walk"],
    ),
    Exercise(
        name="Rowing Machine",
        muscle_groups=["cardio", "back"],
        category="cardio",
        equipment="machine",
        substitutes=["Incline Treadmill Walk"],
    ),
    Exercise(
        name="Burpee",
        muscle_groups=["full_body", "cardio"],
        category="cardio",
        equipment="bodyweight",
        substitutes=["Incline Treadmill Walk"],
    ),
]

# Hip thrust and assisted pull-up are still an open decision,
# so they're deliberately left out of the catalog until that's resolved.


def get_exercise(name: str) -> Exercise | None:
    for ex in CATALOG:
        if ex.name == name:
            return ex
    return None


def available_swaps_grouped(
    exercise_name: str,
    user_preferences: dict[str, UserExercisePreference] | None = None,
) -> tuple[list[Exercise], list[Exercise]]:
    """Same substitution logic as available_swaps, but keeps hand-picked
    substitutes separate from the broader category/muscle-group fallback so
    a caller (e.g. the swap picker) can show match strength instead of one
    flat, undifferentiated list. The fallback tier is sorted best-first by
    category match then muscle-group overlap, not left in catalog order."""
    target = get_exercise(exercise_name)
    if target is None:
        return [], []

    prefs = user_preferences or {}

    def is_excluded(ex: Exercise) -> bool:
        pref = prefs.get(ex.name)
        return pref is not None and pref.excluded

    explicit = [get_exercise(n) for n in target.substitutes]
    explicit = [e for e in explicit if e is not None and not is_excluded(e)]

    same_group = [
        ex
        for ex in CATALOG
        if ex.name != target.name
        and not is_excluded(ex)
        and ex not in explicit
        and (
            ex.category == target.category
            or set(ex.muscle_groups) & set(target.muscle_groups)
        )
    ]

    def relevance(ex: Exercise) -> tuple[int, int]:
        same_category = 1 if ex.category == target.category else 0
        overlap = len(set(ex.muscle_groups) & set(target.muscle_groups))
        return (same_category, overlap)

    same_group.sort(key=relevance, reverse=True)

    return explicit, same_group


def available_swaps(
    exercise_name: str,
    user_preferences: dict[str, UserExercisePreference] | None = None,
) -> list[Exercise]:
    """Exercises that can substitute for the given one: explicit substitutes
    first, then anything else in the same category/muscle groups, ranked by
    relevance. If user_preferences is given, that user's excluded exercises
    are filtered out; with no preferences supplied, nothing is excluded."""
    explicit, same_group = available_swaps_grouped(exercise_name, user_preferences)
    return explicit + same_group

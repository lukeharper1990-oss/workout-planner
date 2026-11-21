from datetime import date

from workout_app.models import CardioSet, FlatSet, Session, SessionExercise

# Sample sessions with invented numbers. They keep the shapes real training
# logs have: a light opener set before the top set, and uneven jumps
# (e.g. 35, 40, 50, 50kg) rather than a smooth ramp, because the
# progression logic has to cope with both.
LOWER_A_AUG_4 = Session(
    session_day="Lower A",
    session_date=date(2026, 8, 4),
    session_style="unspecified",
    notes="overall session length felt right",
    exercises=[
        SessionExercise(
            exercise_name="Deadlift",
            sets=[
                FlatSet(reps=3, weight_kg=60),  # opener
                FlatSet(reps=3, weight_kg=90),  # top single
                FlatSet(reps=3, weight_kg=85),
                FlatSet(reps=3, weight_kg=85),
            ],
            perceived_difficulty="hard",
            preference="liked",
        ),
        SessionExercise(
            exercise_name="Leg Press",
            sets=[
                FlatSet(reps=8, weight_kg=120),
                FlatSet(reps=10, weight_kg=120),
                FlatSet(reps=10, weight_kg=120),
            ],
            perceived_difficulty="right",
        ),
        SessionExercise(
            exercise_name="Romanian Deadlift",
            sets=[
                FlatSet(reps=8, weight_kg=50),
                FlatSet(reps=8, weight_kg=50),
                FlatSet(reps=8, weight_kg=50),
            ],
            perceived_difficulty="right",
            preference="liked",
            first_time=True,
        ),
        SessionExercise(
            exercise_name="Walking Lunge",
            sets=[
                FlatSet(reps=10, weight_kg=8),
                FlatSet(reps=10, weight_kg=8),
                FlatSet(reps=10, weight_kg=8),
            ],
            perceived_difficulty="hard",
            preference="disliked",
        ),
        SessionExercise(
            exercise_name="Hip Abduction",
            sets=[
                FlatSet(reps=12, weight_kg=40),
                FlatSet(reps=12, weight_kg=40),
                FlatSet(reps=12, weight_kg=40),
                FlatSet(reps=12, weight_kg=45),
            ],
            perceived_difficulty="right",
        ),
        SessionExercise(
            exercise_name="Standing Calf Raise",
            sets=[
                FlatSet(reps=12, weight_kg=35),
                FlatSet(reps=12, weight_kg=40),
                FlatSet(reps=12, weight_kg=50),
                FlatSet(reps=12, weight_kg=50),
            ],
        ),
        SessionExercise(
            exercise_name="Neck Work",
            sets=[
                FlatSet(reps=15, weight_kg=4),
                FlatSet(reps=15, weight_kg=4),
                FlatSet(reps=15, weight_kg=4),
            ],
        ),
        SessionExercise(
            exercise_name="Incline Treadmill Walk",
            sets=[CardioSet(duration_min=15, incline_pct=12)],
            perceived_difficulty="right",
        ),
    ],
)

# Sample session, 9 Aug. Note the Pec Deck sets (25x12, 30x10, 30x5 failure,
# 25x10). This is the pattern that exposed the top-set-vs-working-weight
# bug: naively taking the max (30kg) would credit a failed set, while
# working_weight_kg() correctly reads it as 25kg, where the session
# actually landed.
UPPER_B_AUG_9 = Session(
    session_day="Upper B",
    session_date=date(2026, 8, 9),
    session_style="unspecified",
    notes="overall session length felt right",
    exercises=[
        SessionExercise(
            exercise_name="Machine Shoulder Press",
            sets=[
                FlatSet(reps=6, weight_kg=20),
                FlatSet(reps=6, weight_kg=20),
                FlatSet(reps=6, weight_kg=20),
                FlatSet(reps=6, weight_kg=20),
            ],
            perceived_difficulty="hard",
            preference="neutral",
        ),
        SessionExercise(
            exercise_name="T-Bar Row",
            sets=[
                FlatSet(reps=6, weight_kg=25),
                FlatSet(reps=6, weight_kg=35),
                FlatSet(reps=6, weight_kg=35),
                FlatSet(reps=6, weight_kg=35),
            ],
            perceived_difficulty="right",
            preference="liked",
        ),
        SessionExercise(
            exercise_name="Pec Deck",
            sets=[
                FlatSet(reps=12, weight_kg=25),
                FlatSet(reps=10, weight_kg=30),
                FlatSet(reps=5, weight_kg=30),  # failure
                FlatSet(reps=10, weight_kg=25),
            ],
            perceived_difficulty="hard",
            preference="liked",
        ),
        SessionExercise(
            exercise_name="Lat Pulldown",
            sets=[
                FlatSet(reps=10, weight_kg=40),
                FlatSet(reps=10, weight_kg=40),
                FlatSet(reps=10, weight_kg=45),
            ],
            perceived_difficulty="hard",
            preference="liked",
        ),
        SessionExercise(
            exercise_name="Cable Bicep Curl",
            sets=[
                FlatSet(reps=10, weight_kg=20),
                FlatSet(reps=10, weight_kg=25),
                FlatSet(reps=10, weight_kg=25),
                FlatSet(reps=10, weight_kg=25),
            ],
            perceived_difficulty="right",
            preference="liked",
        ),
        SessionExercise(
            exercise_name="Tricep Pushdown",
            sets=[
                FlatSet(reps=10, weight_kg=30),
                FlatSet(reps=10, weight_kg=30),
                FlatSet(reps=10, weight_kg=30),
                FlatSet(reps=10, weight_kg=30),
            ],
            perceived_difficulty="right",
            preference="liked",
        ),
        SessionExercise(
            exercise_name="Incline Treadmill Walk",
            sets=[CardioSet(duration_min=20, incline_pct=10)],
            perceived_difficulty="right",
        ),
    ],
)

ALL_SESSIONS: list[Session] = [LOWER_A_AUG_4, UPPER_B_AUG_9]

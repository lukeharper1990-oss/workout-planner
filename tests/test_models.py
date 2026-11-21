from workout_app.models import FlatSet, RampingSet, SessionExercise


def test_working_weight_ignores_heavier_opener():
    # Real example from the log: 80kg opener, 110kg top single, then three
    # working sets at 100kg. The session's working weight is 100kg.
    se = SessionExercise(
        exercise_name="Deadlift",
        sets=[
            FlatSet(reps=3, weight_kg=80),
            FlatSet(reps=3, weight_kg=110),
            FlatSet(reps=3, weight_kg=100),
            FlatSet(reps=3, weight_kg=100),
        ],
    )
    assert se.working_weight_kg() == 100
    assert se.top_weight_kg() == 110  # still available for display


def test_working_weight_reflects_a_failed_top_set_backing_off():
    # Real example: 30x12, 35x10, 35x5 (failure), back to 30x10. The honest
    # read is 30kg, not the 35kg he failed at.
    se = SessionExercise(
        exercise_name="Pec Deck",
        sets=[
            FlatSet(reps=12, weight_kg=30),
            FlatSet(reps=10, weight_kg=35),
            FlatSet(reps=5, weight_kg=35),
            FlatSet(reps=10, weight_kg=30),
        ],
    )
    assert se.working_weight_kg() == 30
    assert se.top_weight_kg() == 35


def test_working_weight_reflects_ramping_up_to_a_genuine_top_set():
    # Opposite direction: three sets at 45kg then a heavier top set at 50kg.
    # Ending heavier is a legitimate read too, working weight tracks where
    # the session actually ended, not always "the lower number."
    se = SessionExercise(
        exercise_name="Hip Abduction",
        sets=[
            FlatSet(reps=12, weight_kg=45),
            FlatSet(reps=12, weight_kg=45),
            FlatSet(reps=12, weight_kg=45),
            FlatSet(reps=12, weight_kg=50),
        ],
    )
    assert se.working_weight_kg() == 50


def test_working_weight_handles_ramping_set_type():
    se = SessionExercise(
        exercise_name="Standing Calf Raise",
        sets=[RampingSet(start_weight_kg=40, end_weight_kg=60, num_sets=4, reps=12)],
    )
    assert se.working_weight_kg() == 60

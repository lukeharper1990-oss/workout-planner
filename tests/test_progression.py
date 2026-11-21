from datetime import date

from workout_app.models import FlatSet, Session, SessionExercise
from workout_app.progression import recommend_next, stall_streak


def _session(day_offset, exercise_name, weight, reps, tags=None, session_date=None, **kwargs):
    return Session(
        session_day="Test",
        session_date=session_date or date(2026, 1, 1 + day_offset),
        session_style="easy",
        tags=tags or [],
        exercises=[
            SessionExercise(
                exercise_name=exercise_name,
                sets=[FlatSet(reps=reps, weight_kg=weight)],
                **kwargs,
            )
        ],
    )


def test_progress_reps_when_not_all_sets_hit_top_of_range():
    # Range is 3-6; a 4-rep set hasn't reached the top yet, so double
    # progression should ask for more reps at the same weight, not more
    # weight.
    sessions = [_session(0, "Back Squat", 100, 4)]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "progress reps"
    assert rec["weight_kg"] == 100
    assert rec["reps"] == 5


def test_progress_reps_caps_at_top_of_range():
    sessions = [_session(0, "Back Squat", 100, 5)]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["reps"] == 6  # 5 + 1, not 6 + more


def test_progress_weight_once_every_set_hits_top_of_range():
    sessions = [_session(0, "Back Squat", 100, 6)]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "progress weight"
    assert rec["weight_kg"] == 102.5
    assert rec["reps"] == 3  # back to the floor of the range


def test_too_easy_doubles_the_weight_increment():
    sessions = [
        _session(0, "Back Squat", 100, 6, perceived_difficulty="too_easy")
    ]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "progress weight"
    assert rec["weight_kg"] == 105.0  # double the normal +2.5kg


def test_too_easy_adds_two_reps_instead_of_one():
    sessions = [
        _session(0, "Back Squat", 100, 3, perceived_difficulty="too_easy")
    ]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "progress reps"
    assert rec["reps"] == 5  # 3 + 2


def test_too_hard_holds_and_consolidates_rather_than_reducing():
    # Even though every set hit the top of the range (which would normally
    # trigger a weight increase), "too hard" should hold instead — the plan
    # is explicit that this consolidates, it does not reduce.
    sessions = [
        _session(0, "Back Squat", 100, 6, perceived_difficulty="too_hard", preference="neutral")
    ]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "hold"
    assert rec["weight_kg"] == 100
    assert rec["reps"] == 6


def test_hard_and_disliked_triggers_hold_and_swap_suggestion():
    sessions = [
        _session(
            0, "Walking Lunge", 10, 10,
            perceived_difficulty="hard", preference="disliked",
        )
    ]
    rec = recommend_next("Walking Lunge", sessions, (8, 12), today=date(2026, 1, 10))
    assert rec["recommendation"] == "hold, consider swap"
    assert "swap_options" in rec


def test_staleness_decay_between_22_and_42_days():
    sessions = [_session(0, "Back Squat", 100, 6, session_date=date(2026, 1, 1))]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 25))
    assert rec["recommendation"] == "staleness decay"
    assert rec["weight_kg"] == 95.0
    assert rec["reps"] == 3


def test_long_gap_re_entry_after_43_plus_days():
    sessions = [_session(0, "Back Squat", 100, 6, session_date=date(2026, 1, 1))]
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 2, 15))
    assert rec["recommendation"] == "re-entry after long gap"
    assert rec["weight_kg"] == 90.0
    assert rec["reps"] == 3


def test_deload_after_two_stalled_sessions():
    sessions = [
        _session(0, "Back Squat", 100, 4),
        _session(1, "Back Squat", 100, 4),
        _session(2, "Back Squat", 100, 4),
    ]
    assert stall_streak("Back Squat", sessions) == 2
    rec = recommend_next("Back Squat", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "deload"
    assert rec["weight_kg"] == 90.0


def test_deload_never_drops_below_empty_barbell_weight():
    sessions = [
        _session(0, "Deadlift", 20, 4),
        _session(1, "Deadlift", 20, 4),
        _session(2, "Deadlift", 20, 4),
    ]
    rec = recommend_next("Deadlift", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "deload"
    assert rec["weight_kg"] == 20.0


def test_sport_adjacent_session_discounted_from_stall_streak():
    sessions = [
        _session(0, "Back Squat", 100, 4),
        _session(1, "Back Squat", 100, 4),
        _session(2, "Back Squat", 90, 3, tags=["near_commitment"]),
        _session(3, "Back Squat", 100, 4),
    ]
    assert stall_streak("Back Squat", sessions) == 2


def test_low_energy_session_discounted_and_streak_broken_correctly():
    sessions = [
        _session(0, "Back Squat", 100, 4),
        _session(1, "Back Squat", 105, 4),
        _session(2, "Back Squat", 80, 4, tags=["low_energy"]),
        _session(3, "Back Squat", 107.5, 4),
    ]
    assert stall_streak("Back Squat", sessions) == 0


def test_no_history_anywhere_prompts_for_baseline():
    # A bodyweight exercise has no meaningful loaded weight to estimate at
    # all, and there's no history for anything else either — this is the
    # one case that should still ask for a blind calibration session.
    rec = recommend_next("Push-Up", [], (8, 12))
    assert "no history" in rec["recommendation"]


def test_first_exposure_estimates_from_a_related_exercises_history():
    # Romanian Deadlift has never been logged, but Deadlift has — the
    # explicit cold-start coefficient (0.6x) should give a real starting
    # number instead of just asking for a blind calibration session.
    sessions = [_session(0, "Deadlift", 100, 6)]
    rec = recommend_next("Romanian Deadlift", sessions, (8, 10), today=date(2026, 1, 10))
    assert rec["recommendation"] == "first exposure, estimated"
    assert rec["weight_kg"] == 60.0  # 60% of 100kg, rounded to a 2.5kg step
    assert rec["reps"] == 8


def test_first_exposure_falls_back_to_same_equipment_muscle_overlap():
    # Incline Barbell Press has no explicit coefficient and no history of
    # its own, but Bench Press (also barbell, same muscle groups) does —
    # should estimate from that, conservatively scaled down.
    sessions = [_session(0, "Bench Press", 100, 6)]
    rec = recommend_next("Incline Barbell Press", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "first exposure, estimated from related exercise"
    assert rec["weight_kg"] == 70.0  # 70% of 100kg, rounded to a 2.5kg step
    assert rec["reps"] == 3


def test_first_exposure_falls_back_to_entry_level_when_nothing_relates():
    # No history anywhere, but it's a barbell exercise, so a conservative
    # entry-level weight beats just asking for a blind calibration session.
    rec = recommend_next("Bench Press", [], (3, 6))
    assert rec["recommendation"] == "first exposure, entry-level start"
    assert rec["weight_kg"] == 20.0  # empty barbell
    assert rec["reps"] == 3


def test_light_dumbbell_progression_is_proportionate_not_flat():
    # Regression test: a flat +2.5kg on 5kg neck work was a 50% jump.
    sessions = [_session(0, "Neck Work", 5, 15)]
    rec = recommend_next("Neck Work", sessions, (15, 15), today=date(2026, 1, 10))
    assert rec["recommendation"] == "progress weight"
    assert rec["weight_kg"] == 6.0
    increase_pct = (rec["weight_kg"] - 5) / 5
    assert increase_pct < 0.25


def test_barbell_progression_lands_on_loadable_plate_increment():
    sessions = [_session(0, "Deadlift", 110, 6)]
    rec = recommend_next("Deadlift", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "progress weight"
    assert rec["weight_kg"] == 112.5  # +2.5kg, a standard total plate-pair jump


def test_recommendation_uses_working_weight_not_a_heavier_opener():
    # Integration-level regression test for the original top-priority bug: a
    # real multi-set session (80kg opener, 110kg top single, 100kg x2
    # working sets) must reason from 100kg, not the 110kg single. Every set
    # here is 3 reps against a 3-6 range, so under double progression the
    # correct call is "progress reps" at 100kg — not "progress weight" from
    # 110kg, and not from 100kg either, since 3 reps hasn't reached the top
    # of the range yet.
    sessions = [
        Session(
            session_day="Test",
            session_date=date(2026, 1, 1),
            session_style="unspecified",
            exercises=[
                SessionExercise(
                    exercise_name="Deadlift",
                    sets=[
                        FlatSet(reps=3, weight_kg=80),
                        FlatSet(reps=3, weight_kg=110),
                        FlatSet(reps=3, weight_kg=100),
                        FlatSet(reps=3, weight_kg=100),
                    ],
                    perceived_difficulty="hard",
                    preference="liked",
                )
            ],
        )
    ]
    rec = recommend_next("Deadlift", sessions, (3, 6), today=date(2026, 1, 10))
    assert rec["recommendation"] == "progress reps"
    assert rec["weight_kg"] == 100  # the working weight, not the 110kg opener
    assert rec["reps"] == 4

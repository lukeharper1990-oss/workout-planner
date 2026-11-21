from datetime import date

from workout_app.cards import LOWER_A, UPPER_B
from workout_app.rotation import RotationState, next_card
from workout_app.rotation_models import CommitmentOverride, CommitmentSchedule

QUEUE = [LOWER_A, UPPER_B]


def test_position_advances_only_on_advance_call():
    state = RotationState()
    assert state.current_card(QUEUE).name == "Lower A"
    state.advance()
    assert state.current_card(QUEUE).name == "Upper B"
    state.advance()
    assert state.current_card(QUEUE).name == "Lower A"  # wraps around


def test_missed_session_does_not_advance_the_queue():
    state = RotationState()
    # Opening the app repeatedly without finishing a session must not move
    # the position — only an explicit advance() (a completed session) does.
    assert state.current_card(QUEUE).name == "Lower A"
    assert state.current_card(QUEUE).name == "Lower A"
    assert state.current_card(QUEUE).name == "Lower A"


def test_default_sport_pattern_is_tuesday_thursday():
    schedule = CommitmentSchedule()
    # 2026-08-11 is a Tuesday
    assert schedule.has_commitment_on(date(2026, 8, 11)) is True
    # 2026-08-12 is a Wednesday
    assert schedule.has_commitment_on(date(2026, 8, 12)) is False


def test_override_wins_over_default_pattern_for_a_skipped_sport_day():
    schedule = CommitmentSchedule(overrides=[CommitmentOverride(on_date=date(2026, 8, 11), has_commitment=False)])
    assert schedule.has_commitment_on(date(2026, 8, 11)) is False  # skipped this week


def test_override_can_also_add_an_unusual_sport_day():
    schedule = CommitmentSchedule(overrides=[CommitmentOverride(on_date=date(2026, 8, 15), has_commitment=True)])
    assert schedule.has_commitment_on(date(2026, 8, 15)) is True  # Saturday, not a default day


def test_leg_heavy_card_flagged_the_day_before_commitment():
    state = RotationState(queue_position=0)  # Lower A is up
    schedule = CommitmentSchedule()
    monday = date(2026, 8, 10)  # Tuesday (sport) follows
    result = next_card(state, QUEUE, schedule, monday)
    assert result["card"].name == "Lower A"
    assert result["caution"] is not None
    assert "sport" in result["caution"]


def test_upper_card_never_flagged_regardless_of_sport():
    state = RotationState(queue_position=1)  # Upper B is up
    schedule = CommitmentSchedule()
    monday = date(2026, 8, 10)
    result = next_card(state, QUEUE, schedule, monday)
    assert result["card"].name == "Upper B"
    assert result["caution"] is None


def test_leg_heavy_card_not_flagged_when_sport_skipped_that_week():
    state = RotationState(queue_position=0)  # Lower A is up
    schedule = CommitmentSchedule(overrides=[CommitmentOverride(on_date=date(2026, 8, 11), has_commitment=False)])
    monday = date(2026, 8, 10)  # would normally precede Tuesday sport, but it's overridden off
    result = next_card(state, QUEUE, schedule, monday)
    assert result["caution"] is None


def test_position_never_gets_derailed_by_sport_caution():
    # The caution is informational only — it must never change which card
    # comes back.
    state = RotationState(queue_position=0)
    schedule = CommitmentSchedule()
    monday = date(2026, 8, 10)
    result = next_card(state, QUEUE, schedule, monday)
    assert result["card"].name == "Lower A"  # still Lower A, caution or not

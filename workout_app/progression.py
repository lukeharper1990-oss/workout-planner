from datetime import date

from workout_app.exercises import CATALOG, available_swaps, get_exercise
from workout_app.models import FlatSet, Session, SessionExercise, UserExercisePreference

PROGRESSION_PCT = 0.025
DELOAD_PCT = 0.10
STALL_STREAK_FOR_DELOAD = 2

# Real loadable increments by equipment — you can't put 1.25kg total on a
# barbell without fractional plates most gyms don't have, and fixed
# dumbbells/machines have their own fixed steps. Percentage-based scaling
# still applies, it just has to land on one of these, not an arbitrary value.
EQUIPMENT_ROUNDING_KG = {
    "barbell": 2.5,
    "machine": 2.5,
    "dumbbell": 1.0,
}
DEFAULT_ROUNDING_KG = 1.0

# A barbell's own weight is a hard floor — you can't load less than an empty
# bar. Standard Olympic bar; could become per-user/gym configurable later.
BARBELL_BASE_WEIGHT_KG = 20.0

# Staleness decay thresholds (days since last performed).
STALE_DAYS = 22
LONG_GAP_DAYS = 43
STALE_PCT = 0.95
LONG_GAP_PCT = 0.90

# Cold-start estimates for a never-performed exercise, expressed as a
# fraction of a related exercise's last working weight. Deliberately sparse
# — only exercises where a genuinely comparable movement's coefficient is
# well-established get one; inventing coefficients for the rest of the
# catalog risks suggesting an unsafe starting weight on made-up numbers.
# Everything else falls back to "log a baseline session first."
COLD_START_COEFFICIENTS: dict[str, tuple[str, float]] = {
    "Romanian Deadlift": ("Deadlift", 0.6),
}

# When no explicit coefficient exists, fall back to the user's own history
# on a same-equipment, muscle-group-overlapping exercise, scaled down
# conservatively — restricted to the same equipment type deliberately.
# Crossing equipment (e.g. Leg Press vs Back Squat) can differ 2-3x in
# absolute loadable weight for a similar level of difficulty, which isn't
# imprecise, it's actually unsafe to guess at. Same-equipment matches are
# still only approximate, hence the haircut rather than using the weight
# as-is.
RELATED_MATCH_COEFFICIENT = 0.7

# Last-resort starting points when there's no history to estimate from at
# all — deliberately conservative, meant to be adjusted up immediately if
# too light, never guessed to be "about right." Equipment types with no
# meaningful loaded weight (bodyweight, cardio machines) are intentionally
# absent — those still fall back to "log a baseline session first."
ENTRY_LEVEL_KG: dict[str, float] = {
    "barbell": BARBELL_BASE_WEIGHT_KG,
    "dumbbell": 5.0,
    "machine": 10.0,
    "sled": 20.0,
}


def rounding_for(exercise_name: str) -> float:
    exercise = get_exercise(exercise_name)
    equipment = exercise.equipment if exercise else None
    return EQUIPMENT_ROUNDING_KG.get(equipment, DEFAULT_ROUNDING_KG)


def _floor_for(exercise_name: str) -> float:
    exercise = get_exercise(exercise_name)
    if exercise and exercise.equipment == "barbell":
        return BARBELL_BASE_WEIGHT_KG
    return 0.0


def _round_to_increment(weight_kg: float, rounding: float) -> float:
    return round(weight_kg / rounding) * rounding


def _progression_increment(current_weight_kg: float, rounding: float, doubled: bool = False) -> float:
    """Percentage-based, not flat: a flat 2.5kg is ~2.3% on a 110kg deadlift
    but a 50% jump on 5kg neck work. Scaling by weight keeps light isolation
    exercises proportionate, then snapped to what's actually loadable.
    Doubled when the last session felt "too easy" — a stronger signal to
    move faster than the default pace."""
    pct = PROGRESSION_PCT * (2 if doubled else 1)
    raw = max(current_weight_kg * pct, rounding)
    steps = max(round(raw / rounding), 1)
    return steps * rounding


def _min_reps(se: SessionExercise) -> int | None:
    """The weakest set's rep count — the honest constraint on whether to
    progress, since double progression requires every set to reach the top
    of the range, not just the average or the best set."""
    flat_sets = [s for s in se.sets if isinstance(s, FlatSet)]
    if not flat_sets:
        return None
    return min(s.reps for s in flat_sets)


def _all_sets_hit(se: SessionExercise, target_reps: int) -> bool:
    flat_sets = [s for s in se.sets if isinstance(s, FlatSet)]
    if not flat_sets:
        return False
    return all(s.reps >= target_reps for s in flat_sets)


def exercise_history(
    exercise_name: str, sessions: list[Session]
) -> list[tuple[Session, SessionExercise]]:
    """Counted-session history for one exercise, oldest to newest. Sessions
    tagged near_commitment or low_energy are excluded entirely, per the user's rule."""
    history = []
    for session in sorted(sessions, key=lambda s: s.session_date):
        if not session.is_counted():
            continue
        for se in session.exercises:
            if se.exercise_name == exercise_name:
                history.append((session, se))
    return history


def _progressed(previous: SessionExercise, current: SessionExercise) -> bool:
    prev_weight = previous.working_weight_kg()
    curr_weight = current.working_weight_kg()
    if prev_weight is not None and curr_weight is not None:
        if curr_weight != prev_weight:
            return curr_weight > prev_weight
        return current.total_reps() > previous.total_reps()
    return current.total_reps() > previous.total_reps()


def stall_streak(exercise_name: str, sessions: list[Session]) -> int:
    history = exercise_history(exercise_name, sessions)
    if len(history) < 2:
        return 0

    streak = 0
    for i in range(len(history) - 1, 0, -1):
        _, current = history[i]
        _, previous = history[i - 1]
        if not _progressed(previous, current):
            streak += 1
        else:
            break
    return streak


def _best_related_exercise(
    exercise_name: str, sessions: list[Session]
) -> tuple[str, float] | None:
    """The user's own most-relevant trained exercise for estimating a
    never-done one: same equipment (see RELATED_MATCH_COEFFICIENT for why),
    ranked by muscle-group overlap, and only candidates they actually have
    history for. Returns (candidate_name, working_weight_kg) or None."""
    target = get_exercise(exercise_name)
    if target is None:
        return None

    best_name = None
    best_weight = None
    best_overlap = 0
    for candidate in CATALOG:
        if candidate.name == exercise_name or candidate.equipment != target.equipment:
            continue
        overlap = len(set(candidate.muscle_groups) & set(target.muscle_groups))
        if overlap <= best_overlap:
            continue
        history = exercise_history(candidate.name, sessions)
        if not history:
            continue
        weight = history[-1][1].working_weight_kg()
        if weight is None:
            continue
        best_name, best_weight, best_overlap = candidate.name, weight, overlap

    return (best_name, best_weight) if best_name is not None else None


def _first_exposure(
    exercise_name: str,
    sessions: list[Session],
    rep_range: tuple[int, int],
) -> dict:
    """Distinct from ordinary "no history" handling: gives a real, if
    conservative, starting number wherever possible instead of always
    asking for a blind calibration session — tries an explicit coefficient
    first, then the user's own related-exercise history, then a generic
    entry-level weight, in that order of precision."""
    floor_reps, _ = rep_range
    rounding = rounding_for(exercise_name)
    floor = _floor_for(exercise_name)

    if exercise_name in COLD_START_COEFFICIENTS:
        related_name, coeff = COLD_START_COEFFICIENTS[exercise_name]
        related_history = exercise_history(related_name, sessions)
        if related_history:
            related_weight = related_history[-1][1].working_weight_kg()
            if related_weight is not None:
                estimate = max(_round_to_increment(related_weight * coeff, rounding), floor)
                return {
                    "exercise": exercise_name,
                    "recommendation": "first exposure, estimated",
                    "weight_kg": estimate,
                    "reps": floor_reps,
                    "note": (
                        f"estimated at {int(coeff * 100)}% of your {related_name} "
                        f"working weight ({related_weight}kg) — a starting point, "
                        "not a target; adjust based on how it feels"
                    ),
                }

    related = _best_related_exercise(exercise_name, sessions)
    if related is not None:
        related_name, related_weight = related
        estimate = max(
            _round_to_increment(related_weight * RELATED_MATCH_COEFFICIENT, rounding), floor
        )
        return {
            "exercise": exercise_name,
            "recommendation": "first exposure, estimated from related exercise",
            "weight_kg": estimate,
            "reps": floor_reps,
            "note": (
                f"estimated from your {related_name} working weight "
                f"({related_weight}kg — similar muscle groups, same equipment) "
                "— a rough starting point, not a target; adjust based on how it feels"
            ),
        }

    target = get_exercise(exercise_name)
    entry_level = ENTRY_LEVEL_KG.get(target.equipment) if target else None
    if entry_level is not None:
        return {
            "exercise": exercise_name,
            "recommendation": "first exposure, entry-level start",
            "weight_kg": max(entry_level, floor),
            "reps": floor_reps,
            "note": (
                "no related history to estimate from — starting at a "
                "conservative entry-level weight; adjust based on how it feels"
            ),
        }

    return {
        "exercise": exercise_name,
        "recommendation": "no history yet, log a baseline session first",
    }


def recommend_next(
    exercise_name: str,
    sessions: list[Session],
    rep_range: tuple[int, int],
    user_preferences: dict[str, UserExercisePreference] | None = None,
    today: date | None = None,
) -> dict:
    """Double progression: fixed rep range per exercise-in-card, progress
    reps before weight, only move weight once every set hits the top of the
    range. Supersedes the old flat percentage-per-session model — that
    model progressed every session regardless of rep range, which doesn't
    match how double progression is actually meant to work."""
    floor_reps, top_reps = rep_range
    today = today or date.today()
    history = exercise_history(exercise_name, sessions)

    if not history:
        return _first_exposure(exercise_name, sessions, rep_range)

    last_session, last_perf = history[-1]
    last_weight = last_perf.working_weight_kg()
    felt = last_perf.perceived_difficulty

    if felt in ("too_hard", "hard") and last_perf.preference == "disliked":
        swaps = [e.name for e in available_swaps(exercise_name, user_preferences)]
        return {
            "exercise": exercise_name,
            "recommendation": "hold, consider swap",
            "weight_kg": last_weight,
            "reps": last_perf.total_reps(),
            "note": "hard and disliked last session",
            "swap_options": swaps,
        }

    if last_weight is None:
        # Bodyweight/time-based — no load to progress, double progression
        # doesn't apply the same way (no added-weight tracking here).
        return {
            "exercise": exercise_name,
            "recommendation": "maintain",
            "note": "no tracked weight to progress (bodyweight/time-based)",
        }

    rounding = rounding_for(exercise_name)
    floor = _floor_for(exercise_name)
    days_since = (today - last_session.session_date).days

    if days_since >= LONG_GAP_DAYS:
        weight = max(_round_to_increment(last_weight * LONG_GAP_PCT, rounding), floor)
        return {
            "exercise": exercise_name,
            "recommendation": "re-entry after long gap",
            "weight_kg": weight,
            "reps": floor_reps,
            "note": f"{days_since} days since last session — starting at 90% to re-establish form",
        }

    if days_since >= STALE_DAYS:
        weight = max(_round_to_increment(last_weight * STALE_PCT, rounding), floor)
        return {
            "exercise": exercise_name,
            "recommendation": "staleness decay",
            "weight_kg": weight,
            "reps": floor_reps,
            "note": f"{days_since} days since last session — starting at 95%",
        }

    streak = stall_streak(exercise_name, sessions)
    if streak >= STALL_STREAK_FOR_DELOAD:
        deload_weight = max(_round_to_increment(last_weight * (1 - DELOAD_PCT), rounding), floor)
        return {
            "exercise": exercise_name,
            "recommendation": "deload",
            "weight_kg": deload_weight,
            "reps": floor_reps,
            "note": f"{streak} consecutive stalled sessions, -10% from {last_weight}kg",
        }

    if felt == "too_hard":
        # Consolidate rather than reduce: hold at exactly what was achieved,
        # regardless of whether the rep target was technically hit.
        held_reps = _min_reps(last_perf) or floor_reps
        return {
            "exercise": exercise_name,
            "recommendation": "hold",
            "weight_kg": last_weight,
            "reps": held_reps,
            "note": "felt too hard last time — consolidating before pushing further",
        }

    too_easy = felt == "too_easy"

    if _all_sets_hit(last_perf, top_reps):
        increment = _progression_increment(last_weight, rounding, doubled=too_easy)
        new_weight = max(_round_to_increment(last_weight + increment, rounding), floor)
        return {
            "exercise": exercise_name,
            "recommendation": "progress weight",
            "weight_kg": new_weight,
            "reps": floor_reps,
            "note": (
                f"hit {top_reps} reps on every set — up to {new_weight}kg, "
                f"back to {floor_reps} reps"
                + (" (doubled — felt too easy)" if too_easy else "")
            ),
        }

    last_reps = _min_reps(last_perf) or floor_reps
    step = 2 if too_easy else 1
    next_reps = min(last_reps + step, top_reps)
    return {
        "exercise": exercise_name,
        "recommendation": "progress reps",
        "weight_kg": last_weight,
        "reps": next_reps,
        "note": f"same {last_weight}kg, aim for {next_reps} reps (top of range is {top_reps})",
    }

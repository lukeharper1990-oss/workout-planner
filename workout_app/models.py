from dataclasses import dataclass, field
from datetime import date


@dataclass
class Exercise:
    """Universal exercise data. No personal preference belongs here — that
    lives in UserExercisePreference, layered on top per user."""

    name: str
    muscle_groups: list[str]
    category: str  # push, pull, legs, core, cardio
    equipment: str
    substitutes: list[str] = field(default_factory=list)
    # What the second logged number means for a set of this exercise. Most
    # exercises are reps; sled/carry work is distance-based (weight pushed
    # or carried over N meters, not a rep count) — logging that as "reps"
    # would be actively wrong, not just mislabeled.
    logging_unit: str = "reps"  # "reps" | "meters"


@dataclass
class UserExercisePreference:
    """A single user's personal overlay on one exercise: exclusion and
    access constraints are opinions/circumstances, not facts about the
    exercise itself."""

    exercise_name: str
    excluded: bool = False
    exclusion_reason: str | None = None
    hard_to_access: bool = False
    access_note: str | None = None


@dataclass
class FlatSet:
    reps: int
    weight_kg: float | None  # None for bodyweight/time-based


@dataclass
class RampingSet:
    start_weight_kg: float
    end_weight_kg: float
    num_sets: int
    reps: int


@dataclass
class CardioSet:
    duration_min: float
    incline_pct: float | None = None


@dataclass
class SessionExercise:
    exercise_name: str
    sets: list[FlatSet | RampingSet | CardioSet]
    perceived_difficulty: str | None = None  # too_easy, right, hard, too_hard
    preference: str | None = None  # liked, disliked
    first_time: bool = False

    def top_weight_kg(self) -> float | None:
        """The single heaviest weight touched this session. For display/
        reference only — do NOT use this for progression. It credits a
        heavier opener or a failed top attempt as if it were sustained
        work. Use working_weight_kg() for anything progression-related."""
        weights = []
        for s in self.sets:
            if isinstance(s, FlatSet) and s.weight_kg is not None:
                weights.append(s.weight_kg)
            elif isinstance(s, RampingSet):
                weights.append(s.end_weight_kg)
        return max(weights) if weights else None

    def working_weight_kg(self) -> float | None:
        """The weight of the last set performed, not the session's max.
        Real example: Deadlift 110x3 (opener) then 100x3x3 (working sets)
        is a 100kg session, not 110kg — the opener isn't what got sustained.
        Same shape in reverse covers a failed top attempt followed by a
        backed-off set (e.g. 35x10, 35x5 failure, 30x10 — the honest read
        is 30kg, not 35kg). Whichever direction the session moved, where it
        ended is a better progression signal than its single heaviest set."""
        for s in reversed(self.sets):
            if isinstance(s, FlatSet) and s.weight_kg is not None:
                return s.weight_kg
            if isinstance(s, RampingSet):
                return s.end_weight_kg
        return None

    def total_reps(self) -> int:
        total = 0
        for s in self.sets:
            if isinstance(s, FlatSet):
                total += s.reps
            elif isinstance(s, RampingSet):
                total += s.reps * s.num_sets
        return total


@dataclass
class Session:
    session_day: str  # e.g. "Lower A"
    session_date: date
    session_style: str  # easy, hard
    exercises: list[SessionExercise]
    tags: list[str] = field(default_factory=list)  # e.g. near_commitment, low_energy
    notes: str | None = None

    def is_counted(self) -> bool:
        """Sport-adjacent or low-energy sessions are logged but excluded from
        stall-streak and deload evaluation, per the user's explicit rule."""
        return "near_commitment" not in self.tags and "low_energy" not in self.tags

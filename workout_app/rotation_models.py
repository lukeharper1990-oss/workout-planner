from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class CardExercise:
    exercise_name: str
    tier: str  # spine, primary, accessory
    rep_range: tuple[int, int]
    sets: int


@dataclass
class Card:
    name: str
    bias: str  # upper, lower
    exercises: list[CardExercise]

    def is_leg_heavy(self) -> bool:
        return self.bias == "lower"


@dataclass
class CommitmentOverride:
    on_date: date
    has_commitment: bool  # False = skipped a normal sport day, True = added one


@dataclass
class CommitmentSchedule:
    """Default weekly pattern plus explicit per-date corrections. A fixed
    weekly assumption alone is unreliable, sessions get skipped some weeks,
    so overrides always win over the default pattern."""

    default_weekdays: list[int] = field(default_factory=lambda: [1, 3])  # Tue=1, Thu=3 (Mon=0)
    overrides: list[CommitmentOverride] = field(default_factory=list)

    def has_commitment_on(self, target_date: date) -> bool:
        for o in self.overrides:
            if o.on_date == target_date:
                return o.has_commitment
        return target_date.weekday() in self.default_weekdays

    def day_before_commitment(self, target_date: date) -> bool:
        return self.has_commitment_on(target_date + timedelta(days=1))

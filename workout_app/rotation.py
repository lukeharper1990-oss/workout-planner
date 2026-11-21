import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from workout_app.cards import Card
from workout_app.rotation_models import CommitmentSchedule


@dataclass
class RotationState:
    """Position in the card queue. Advances only when a session is
    actually completed — never by date, never by opening the app. A
    missed session just leaves this exactly where it was."""

    queue_position: int = 0

    def current_card(self, queue: list[Card]) -> Card:
        return queue[self.queue_position % len(queue)]

    def advance(self) -> None:
        self.queue_position += 1


def load_rotation_state(path: str | Path) -> RotationState:
    p = Path(path)
    if not p.exists():
        return RotationState()
    return RotationState(**json.loads(p.read_text()))


def save_rotation_state(state: RotationState, path: str | Path) -> None:
    Path(path).write_text(json.dumps(asdict(state)))


def next_card(
    state: RotationState,
    queue: list[Card],
    commitment_schedule: CommitmentSchedule,
    target_date: date,
) -> dict:
    """What to serve next. Position always wins — this never skips or
    reorders the queue, even around sport sessions. It only adds a caution flag so
    the judgement call stays with the user, same principle as niggle
    reporting: flag, don't auto-remove."""
    card = state.current_card(queue)
    caution = None
    if card.is_leg_heavy() and commitment_schedule.day_before_commitment(target_date):
        caution = (
            f"{card.name} is leg-heavy and tomorrow is a sport day. "
            "Consider lighter loading, or swap out the leg accessories "
            "for this session."
        )
    return {"card": card, "caution": caution}

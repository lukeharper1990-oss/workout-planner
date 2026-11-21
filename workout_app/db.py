import json
import os
from dataclasses import asdict
from datetime import date

from supabase import Client, create_client

from workout_app.models import (
    CardioSet,
    FlatSet,
    RampingSet,
    Session,
    SessionExercise,
    UserExercisePreference,
)
from workout_app.rotation import RotationState
from workout_app.rotation_models import CommitmentOverride


def get_client(url: str | None = None, key: str | None = None) -> Client:
    url = url or os.environ["SUPABASE_URL"]
    key = key or os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def _set_to_dict(s) -> dict:
    d = asdict(s)
    d["_type"] = type(s).__name__
    return d


def _set_from_dict(d: dict):
    t = d.pop("_type")
    if t == "FlatSet":
        return FlatSet(**d)
    if t == "RampingSet":
        return RampingSet(**d)
    if t == "CardioSet":
        return CardioSet(**d)
    raise ValueError(f"unknown set type {t}")


def _session_exercise_to_dict(se: SessionExercise) -> dict:
    return {
        "exercise_name": se.exercise_name,
        "sets": [_set_to_dict(s) for s in se.sets],
        "perceived_difficulty": se.perceived_difficulty,
        "preference": se.preference,
        "first_time": se.first_time,
    }


def _session_exercise_from_dict(d: dict) -> SessionExercise:
    return SessionExercise(
        exercise_name=d["exercise_name"],
        sets=[_set_from_dict(s) for s in d["sets"]],
        perceived_difficulty=d.get("perceived_difficulty"),
        preference=d.get("preference"),
        first_time=d.get("first_time", False),
    )


def save_session(client: Client, session: Session) -> None:
    client.table("sessions").insert(
        {
            "session_day": session.session_day,
            "session_date": session.session_date.isoformat(),
            "session_style": session.session_style,
            "notes": session.notes,
            "data": {
                "tags": session.tags,
                "exercises": [_session_exercise_to_dict(se) for se in session.exercises],
            },
        }
    ).execute()


def load_all_sessions(client: Client) -> list[Session]:
    rows = client.table("sessions").select("*").order("session_date").execute().data
    sessions = []
    for row in rows:
        sessions.append(
            Session(
                session_day=row["session_day"],
                session_date=date.fromisoformat(row["session_date"]),
                session_style=row["session_style"],
                notes=row.get("notes"),
                tags=row["data"].get("tags", []),
                exercises=[_session_exercise_from_dict(se) for se in row["data"]["exercises"]],
            )
        )
    return sessions


def load_rotation_state(client: Client) -> RotationState:
    row = client.table("rotation_state").select("*").eq("id", 1).single().execute().data
    return RotationState(queue_position=row["queue_position"])


def save_rotation_state(client: Client, state: RotationState) -> None:
    client.table("rotation_state").update({"queue_position": state.queue_position}).eq(
        "id", 1
    ).execute()


def load_commitment_overrides(client: Client) -> list[CommitmentOverride]:
    rows = client.table("commitment_overrides").select("*").execute().data
    return [
        CommitmentOverride(on_date=date.fromisoformat(r["on_date"]), has_commitment=r["has_commitment"])
        for r in rows
    ]


def save_commitment_override(client: Client, override: CommitmentOverride) -> None:
    client.table("commitment_overrides").upsert(
        {"on_date": override.on_date.isoformat(), "has_commitment": override.has_commitment},
        on_conflict="on_date",
    ).execute()


def load_user_preferences(client: Client) -> dict[str, UserExercisePreference]:
    rows = client.table("user_preferences").select("*").execute().data
    return {r["exercise_name"]: UserExercisePreference(**r) for r in rows}


def save_user_preference(client: Client, pref: UserExercisePreference) -> None:
    client.table("user_preferences").upsert(asdict(pref), on_conflict="exercise_name").execute()

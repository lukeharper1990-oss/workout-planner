from datetime import date

import streamlit as st

from workout_app import db
from workout_app.cards import CARD_QUEUE
from workout_app.exercises import available_swaps_grouped, get_exercise
from workout_app.models import CardioSet, FlatSet, Session, SessionExercise
from workout_app.progression import recommend_next, rounding_for
from workout_app.rotation import next_card
from workout_app.rotation_models import CommitmentOverride, CommitmentSchedule
from workout_app.streamlit_data import (
    get_client,
    load_all_sessions,
    load_rotation_state,
    load_commitment_overrides,
    load_user_preferences,
)

# --- Force the per-set row (number, weight, reps, done) to stay on one line
# on narrow phone widths. Streamlit's columns default to flex-wrap: wrap with
# min-width: auto on each column, so once content pushes a column's
# intrinsic width past what's left on screen, the row wraps onto two lines
# instead of shrinking. Forcing nowrap + min-width: 0 lets the columns
# actually compress. The +/- step buttons stay visible (not hidden like an
# earlier pass did) — faster to tap than opening the keyboard for a single
# rep/kg adjustment — just shrunk and tightened to fit.
st.html(
    """
    <style>
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0.3rem !important;
    }
    [data-testid="stHorizontalBlock"] [data-testid="stColumn"] {
        min-width: 0 !important;
    }
    [data-testid="stNumberInputStepUp"],
    [data-testid="stNumberInputStepDown"] {
        min-width: 1.6rem !important;
        width: 1.6rem !important;
        padding: 0 !important;
    }
    [data-testid="stNumberInput"] input {
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
        text-align: center;
    }
    </style>
    """
)

client = get_client()

if "draft" not in st.session_state:
    st.session_state.draft = {}

today = date.today()

rotation_state = load_rotation_state(client)
overrides = load_commitment_overrides(client)
commitment_schedule = CommitmentSchedule(overrides=overrides)
all_sessions = load_all_sessions(client)
user_prefs = load_user_preferences(client)

result = next_card(rotation_state, CARD_QUEUE, commitment_schedule, today)
card = result["card"]
caution = result["caution"]

st.title(card.name)
st.caption(today.strftime("%A, %d %B %Y"))
if caution:
    st.warning(caution)

with st.expander("Sport sessions this week"):
    today_has_commitment = commitment_schedule.has_commitment_on(today)
    marked = st.checkbox("Sport session today", value=today_has_commitment, key="commitment_today")
    if st.button("Save sport status for today"):
        db.save_commitment_override(client, CommitmentOverride(on_date=today, has_commitment=marked))
        load_commitment_overrides.clear()
        st.success("Saved.")
        st.rerun()

st.divider()

FELT_OPTIONS = {"Too easy": "too_easy", "About right": "right", "Too hard": "too_hard"}
VERDICT_OPTIONS = {"Liked it": "liked", "Fine": "neutral", "Not again": "disliked"}

if "swaps" not in st.session_state:
    st.session_state.swaps = {}


def render_swap_ui(original_name: str) -> None:
    """Swap-out picker for one exercise slot (a card exercise or the cardio
    finisher). Shared so both places behave identically instead of the
    cardio slot silently missing the feature, as it originally did."""
    swap_open_key = f"{original_name}_swap_open"
    active_name = st.session_state.swaps.get(original_name, original_name)

    swap_col1, swap_col2 = st.columns(2)
    with swap_col1:
        if st.button("⇄ Swap out", key=f"{original_name}_swap_btn", use_container_width=True):
            st.session_state[swap_open_key] = not st.session_state.get(swap_open_key, False)
    with swap_col2:
        if active_name != original_name:
            if st.button("Revert swap", key=f"{original_name}_revert_btn", use_container_width=True):
                del st.session_state.swaps[original_name]
                st.rerun()

    if st.session_state.get(swap_open_key, False):
        best, other = available_swaps_grouped(original_name, user_prefs)
        target_muscles = set(get_exercise(original_name).muscle_groups)

        def _do_swap(name: str) -> None:
            st.session_state.swaps[original_name] = name
            st.session_state[swap_open_key] = False
            st.rerun()

        if not best and not other:
            st.caption("No swap options available for this exercise.")
        else:
            if best:
                st.caption("Best matches")
                for ex in best:
                    if st.button(
                        f"{ex.name} · {ex.equipment}",
                        key=f"{original_name}_swap_to_{ex.name}",
                        use_container_width=True,
                    ):
                        _do_swap(ex.name)
            if other:
                with st.expander(f"More options ({len(other)})"):
                    for ex in other:
                        shared = ", ".join(sorted(set(ex.muscle_groups) & target_muscles))
                        label = f"{ex.name} · {ex.equipment}"
                        if shared:
                            label += f" — also hits {shared}"
                        if st.button(
                            label,
                            key=f"{original_name}_swap_to_{ex.name}",
                            use_container_width=True,
                        ):
                            _do_swap(ex.name)


for ce in card.exercises:
    original_name = ce.exercise_name
    active_name = st.session_state.swaps.get(original_name, original_name)

    rec = recommend_next(active_name, all_sessions, ce.rep_range, user_preferences=user_prefs)
    step = rounding_for(active_name)
    target = rec.get("weight_kg")
    key_prefix = f"{original_name}_{active_name}_{today.isoformat()}"

    num_sets_key = f"{key_prefix}_num_sets"
    if num_sets_key not in st.session_state:
        st.session_state[num_sets_key] = ce.sets

    with st.container(border=True):
        st.caption(ce.tier.upper())
        st.markdown(f"### {active_name}")
        if active_name != original_name:
            st.caption(f"Swapped from {original_name}")

        unit = get_exercise(active_name).logging_unit
        floor_reps = ce.rep_range[0]
        aim_reps = ce.rep_range[1]
        target_reps = rec.get("reps", aim_reps)
        range_note = f" (range top {aim_reps})" if target_reps != aim_reps else ""
        summary = f"{st.session_state[num_sets_key]} sets · **aim {target_reps} {unit}**{range_note} · floor {floor_reps}"
        if rec["recommendation"] == "no history yet, log a baseline session first":
            summary += " · no history yet"
        st.markdown(summary)

        if rec["recommendation"] == "hold, consider swap":
            st.warning(
                f"Last time this was hard and disliked. Consider swapping for: "
                f"{', '.join(rec.get('swap_options', [])[:3])}"
            )
        elif target is not None:
            st.caption(rec.get("note", ""))

        render_swap_ui(original_name)

        set_inputs = []
        for i in range(st.session_state[num_sets_key]):
            num_col, weight_col, reps_col, done_col = st.columns([0.3, 2.2, 2.0, 0.6])
            with num_col:
                st.markdown(
                    f"<div style='padding-top:0.55em;font-size:1.2em;font-weight:700;"
                    f"color:#8B8FA3;'>{i + 1}</div>",
                    unsafe_allow_html=True,
                )
            with weight_col:
                weight = st.number_input(
                    "kg", min_value=0.0, max_value=400.0,
                    step=step, value=float(target) if target is not None else 0.0,
                    key=f"{key_prefix}_weight_{i}",
                )
            with reps_col:
                reps = st.number_input(
                    unit, min_value=0, max_value=150,
                    value=target_reps, key=f"{key_prefix}_reps_{i}",
                )
            with done_col:
                st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
                done_key = f"{key_prefix}_done_{i}"
                if done_key not in st.session_state:
                    st.session_state[done_key] = False
                is_done = st.session_state[done_key]
                if st.button(
                    "✓",
                    key=f"{done_key}_btn",
                    type="primary" if is_done else "secondary",
                    use_container_width=True,
                ):
                    st.session_state[done_key] = not is_done
                    st.rerun()
            set_inputs.append((reps, weight))

        remove_col, add_col = st.columns(2)
        with remove_col:
            if st.button(
                "− Remove set", key=f"{key_prefix}_remove_set", use_container_width=True,
                disabled=st.session_state[num_sets_key] <= 1,
            ):
                st.session_state[num_sets_key] -= 1
                st.rerun()
        with add_col:
            if st.button("+ Add set", key=f"{key_prefix}_add_set", use_container_width=True):
                st.session_state[num_sets_key] += 1
                st.rerun()

        felt_label = st.pills(
            "Felt", list(FELT_OPTIONS.keys()), default="About right",
            key=f"{key_prefix}_felt",
        )
        verdict_label = st.pills(
            "Verdict", list(VERDICT_OPTIONS.keys()), default="Fine",
            key=f"{key_prefix}_verdict",
        )

        st.session_state.draft[original_name] = SessionExercise(
            exercise_name=active_name,
            sets=[FlatSet(reps=r, weight_kg=w) for r, w in set_inputs],
            perceived_difficulty=FELT_OPTIONS.get(felt_label, "right"),
            preference=VERDICT_OPTIONS.get(verdict_label, "neutral"),
        )

original_cardio_name = "Incline Treadmill Walk"
active_cardio_name = st.session_state.swaps.get(original_cardio_name, original_cardio_name)

st.subheader(active_cardio_name)
if active_cardio_name != original_cardio_name:
    st.caption(f"Swapped from {original_cardio_name}")
render_swap_ui(original_cardio_name)

cardio_minutes = st.number_input("Minutes", min_value=0, max_value=60, value=18, key="cardio_min")
cardio_incline = st.number_input("Incline %", min_value=0, max_value=20, value=14, key="cardio_incline")

st.caption("Tick each set as you finish it")
if st.button("FINISH", type="primary", use_container_width=True):
    exercises = list(st.session_state.draft.values())
    exercises.append(
        SessionExercise(
            exercise_name=active_cardio_name,
            sets=[CardioSet(duration_min=cardio_minutes, incline_pct=cardio_incline)],
        )
    )
    session = Session(
        session_day=card.name,
        session_date=today,
        session_style="unspecified",
        exercises=exercises,
    )
    db.save_session(client, session)
    rotation_state.advance()
    db.save_rotation_state(client, rotation_state)
    load_all_sessions.clear()
    load_rotation_state.clear()
    st.session_state.draft = {}
    st.success(f"Session saved. Next up: {rotation_state.current_card(CARD_QUEUE).name}")
    st.balloons()

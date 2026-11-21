# Build Plan

**Source of truth as of 12 Aug 2026**: the v3 context dump (Google Drive,
"Workout App: complete context dump"), produced by a separate, extensive
session that stress-tested a real prototype against real gym sessions. It
supersedes the original brief on several structural points. Section 9 of
that doc (rejected decisions) is the most load-bearing part, see
DECISION-LOG.md for the ones that matter here.

This plan was rewritten from scratch against that doc rather than patched,
since several of its calls are direct reversals of what was planned before
(10 days → 6 cards, PPL → upper/lower, easy/hard days → dropped entirely).

## Phase 0 — Core logic prototype (done, needs one critical fix)

- [x] Data models, universal catalog, per-user preference layer
- [x] Deload logic (2-consecutive-failure trigger, noise-filtered for
      sport-adjacent/low-energy sessions) — already matches v3's spec
- [x] Swap logic (explicit substitutes + category/muscle-group fallback)
- [ ] **Top priority bug**: `top_weight_kg()` takes the max weight across a
      session's sets, misreading a heavier opener/top-single as the working
      weight. Confirmed against real data (Deadlift 110x3 then 100x3x3 is a
      100kg working session, not 110kg). Fix before anything else.

## Phase 1 — Exercise database (mostly done, needs reconciling)

- [x] 53 exercises across push/pull/legs/core/cardio, apparatus variety
- [ ] Add exercises confirmed real in v3: Hip Thrust, Lying Leg Curl, Box
      Jumps, T-bar Row, Pec Deck, Hack Squat, Lat Pulldown (wide variant)
- [ ] Add a `loads: []` field per exercise (body areas stressed), needed
      for niggle reporting in Phase 2

## Phase 2 — Progression engine rework (supersedes the old percentage model)

Done — `recommend_next()` now takes `rep_range` as a required argument and
implements real double progression, not percentage-per-session.

- [x] Rep ranges per exercise-in-card (e.g. Leg Press 3x8-12), not a single
      target rep count — sourced from `CardExercise.rep_range`, which
      already existed; `recommend_next()` just wasn't consuming it before
- [x] Progress weight only once all sets hit the top of the rep range;
      otherwise progress reps first — `_all_sets_hit()` / `_min_reps()`
- [x] "Too easy" feedback doubles the increment (weight) or adds 2 reps
      instead of 1 (reps branch); "too hard" holds and consolidates at
      whatever was actually achieved, checked before the weight/reps
      branch so it overrides even a technically-hit rep target
- [x] Staleness decay: 22-42 days since last performed → 95%, reps at
      range floor. 43+ days → 90%, "re-entry after long gap"
- [x] Cold-start estimation via coefficients where a related exercise
      exists — implemented as `COLD_START_COEFFICIENTS`, deliberately
      populated with only the one well-established example from the spec
      (RDL ≈ 0.6x deadlift). Inventing coefficients for the rest of the
      catalog risked suggesting unsafe starting weights on made-up numbers,
      so everything else still falls back to "log a baseline session
      first" rather than a guessed estimate
- [x] First-exposure as a distinct state from plain "no history" —
      `_first_exposure()` gives a real starting weight when a coefficient
      exists. The "short how-to" text guidance from the original bullet
      isn't part of this — that's Sensei's Tips touchpoint, not the
      progression engine
- [x] No load inheritance on swaps — verified, not actually a change: a
      swapped-in exercise is logged and looked up under its own name, so
      it always gets its own independent history already, by construction

## Phase 3 — Tiers and card structure (supersedes the 10-day PPL rotation)

- [x] All 6 cards built: **Lower A**, **Upper A**, **Lower B**, **Upper B**,
      **Lower C**, **Upper C** — Lower A/Upper B are the source doc's real
      logged sessions, the other four designed to keep push/pull balanced
      (9:10 across the whole rotation) and give every lower day real
      posterior-chain work (Lower A and B alone left Lower C with zero
      hamstring-tagged exercises — fixed by putting Leg Curl at primary
      tier on Lower C rather than skipping it). Core work on the new cards
      favors anti-rotation/anti-extension (Russian Twist, Ab Wheel Rollout)
      over spinal flexion, matching what contact sport actually demands.
- [x] Tier model: Spine (never rotates, carries progression history,
      3-6 reps x 4 sets) / Primary (6-10 reps x 3 sets) / Accessory
      (10-15 reps x 2-3 sets, rotates freely by selection score) —
      `rotation_models.py` (Card/CardExercise), cards defined in `cards.py`
- [x] Position-based queue, not calendar-based — a missed session doesn't
      advance the rotation and carries no penalty — `rotation.py`
      (RotationState), tested explicitly (opening the app repeatedly
      without finishing a session never moves the position)
- [x] Sport schedule: default Tue/Thu pattern with per-date override,
      overrides always win — `CommitmentSchedule` in `rotation_models.py`
- [x] Scheduling rule: never serve a legs-heavy card the day before a sport session —
      implemented as a caution flag, not auto-removal or reordering, the
      queue position is never derailed by it, same "flag don't auto-remove"
      principle as niggle reporting. **Not yet done**: true exercise-level
      granularity (pulling just the leg accessories rather than flagging
      the whole card) — current version flags at the whole-card level
- [x] Neck work on every card (confirmed, already how the real data looks)
- [ ] Cardio: 15-20min incline walk finisher every session, plus one
      standalone 30-40min walk on a non-gym, non-sport day

## Phase 4 — Swap-reason tracking and exclusion refinement

- [ ] `swapped_out` needs two values: `swapped_unavailable` vs
      `swapped_by_choice`. Only the second should ever feed the preference/
      exclusion system — critical, conflating them silently removes
      contended equipment (bench, cable) from the programme over time
- [ ] Contention level on availability-constrained exercises (not just a
      boolean), with a minimum-alternate-count requirement
- [ ] Three-state preference model: excluded / approved / **unsure**
      (trial state — approved after 2 "fine" ratings, excluded after 2
      skips/swaps). Needed for Assisted Pull-up, Box Jumps
- [ ] A fourth feedback signal, separate from difficulty and preference:
      "something went wrong" (cramp, pain, form failure) — suppresses an
      exercise without being read as a taste signal

## Phase 5 — Niggle / injury reporting

- [ ] Body-area tagging (neck, shoulder, elbow, lower back, hip, knee,
      hamstring, calf, other) x severity (niggle/sore/painful)
- [ ] Exercises carry a `loads: []` array; flagging an area marks affected
      exercises on the card with severity-appropriate advice — flags,
      never auto-removes
- [ ] Shoulder-impingement-specific swaps already identified: landmine
      press for overhead press, neutral-grip for wide-grip pulldown,
      shortened range on pec deck

## Phase 6 — Persistence and platform

Moved earlier than originally planned — v3's own prototype lost a full
session to browser-storage failure, so this can't be deferred to "after
the UI is built" the way Phase 0's plan assumed.

- **Platform**: PWA + Supabase (explicit recommendation in v3, with
  reasoning: native isn't worth it for a single-user tool, and browser-only
  storage already proved unreliable)
- [ ] Real backend from the start, not deferred — every tick should write
      immediately rather than batching to a "Finish" button
- [ ] Interface lessons already learned from the other prototype (worth
      designing around from the start, not rediscovering):
  - Swap control should be the exercise name itself (tap to change), with
    the "why" (unavailable vs. by choice) asked at end of session, not
    mid-set — the deliberate swap-button-at-bottom approach got ignored
    under real gym conditions
  - Rep target should default to the computed target (e.g. "aim 15, floor
    10"), not pre-fill the bottom of the range
  - Fine weight-adjust needs a real, visible, labelled control, not a
    small tap target between two buttons

## Explicitly out of scope for v1

Nutrition tracking, 1RM testing, wearable sync, social features,
periodisation blocks. All considered and rejected for now, see
DECISION-LOG.md.

## Open threads (carried over from v3, unresolved there too)

- Rotation/selection engine is "one formula in the spec," needs proper
  specification, not just this plan
- Cardio progression logic specced but barely tested
- Swap-by-renaming interface change specced but not built
- Recurring shoulder impingement: the app can route around it indefinitely,
  which the source doc itself flags as "exactly the trap" — worth an actual
  physio, not just app-level accommodation

# Decision Log

Rationale for non-obvious calls, kept separate from the code and the plan so
neither gets cluttered with "why," just "what."

**12 Aug 2026**: a separate, extensive session (on a phone) stress-
tested a real prototype against real gym sessions and produced a v3 context
dump that supersedes several decisions below. Reversed decisions are kept
here, not deleted, since the source doc itself makes the case that the
reasoning behind a rejected approach is worth more than the approach.

## Reversed since Phase 0

### 10-day rotation → 6 cards

**Original decision**: ~10 distinct days, matching what "worked well
before."

**Reversed because**: at 2-3 gym sessions a week, 10 cards means seeing
each workout roughly once a month, nowhere near enough frequency to
progress a lift or even notice progress. Cut to 6. Note from the source
doc: their old programme that "worked well" was actually 4 days, not 10 — so
whatever gave them the remembered variety, it wasn't the day count.

### Push/Pull/Legs → alternating upper/lower-biased cards

**Original decision**: PPL split, "open to it" per the original brief.

**Reversed because**: a 6-card PPL rotation at 2-3 sessions/week trains
each muscle group roughly once every 10 days. Upper/lower-biased cards get
everything hit every 5-7 days instead. Called "the single biggest
structural fix" in the source doc, independent of the exercise-count
question.

### Easy day / hard day → intensity varies within every session

**Original decision**: two whole-session styles from the user's old PT — easy
(3 sets each, ~100 total reps) and hard (ramping 5-rep rounds toward a
~20-rep-capable weight), partly used to disguise cardio inside lifting.

**Reversed because**:
- The ramp-to-20 accumulates a lot of fatigue to arrive at one number that
  moves with sleep and team-sport load — a poor thing to progress against.
- If one session does an exercise at 5x3 and another at ~100 total reps,
  both writing to the same progression history, the engine is reading
  noise. Would have needed a protocol field with separate history lines
  per protocol.
- The user wasn't sure about it, not worth the complexity on
  an "unsure."

Replaced with: intensity varies *within* every session by tier (heavy
spine lift, moderate primaries, high-rep accessories, cardio finisher).
Every session is both easy and hard, just at different tiers.

### Percentage-based progression → double progression

**Original decision** (this build's Phase 0): default increment ~2.5% of
current weight, equipment-aware rounding.

**Status**: not contradicted on the *rounding* (equipment-aware plate
increments and the barbell floor both still hold), but superseded on the
*trigger*. v3 specifies double progression: weight only goes up once all
sets hit the top of the prescribed rep range; "too easy" doubles the
increment, "too hard" holds rather than progressing. This is a more
information-rich signal than a flat percentage every session regardless of
performance, and matches how the "hit the top of the range" tiers (spine/
primary/accessory) are actually structured.

## New, not reversals

### Top-set weight ≠ working weight (critical, active bug)

**Problem**: `top_weight_kg()` in this codebase takes the max weight
across a session's sets. Real example: Deadlift 110x3 (one heavier opener)
then 100x3x3 (three actual working sets). Taking the max reads this as a
110kg session and would recommend progressing from 112.5kg — the user would
likely fail that. The source doc found the same shape of bug independently
on a pec deck session (35x10, then 35x5 failure, then back to 30) and flags
it as the top priority engine fix.

**Fix**: identify the *sustained* working weight (most-repeated weight
across sets, or the weight of the majority of sets), not the single
heaviest one. Top priority, fixed before any other Phase 1+ work.

### Swap reason must be tracked, not inferred

**Decision**: swapping an exercise needs two distinct reasons —
`swapped_unavailable` (equipment was busy/contended) vs.
`swapped_by_choice` (didn't want to do it). Only the second should ever
feed exclusion/preference logic.

**Why**: benches and cable stations are frequently contended at the user's
gym, that's a scheduling problem, not a dislike. If a swap-for-availability
silently counted the same as a swap-for-dislike, bench and cable work
would quietly disappear from the programme over about six weeks for
entirely the wrong reason.

### Preferences need a third state: unsure, not just yes/no

**Decision**: some exercises (assisted pull-up, box jumps) aren't a clean
include/exclude. They get served occasionally in low-stakes accessory
slots; two "fine" ratings graduate them to approved, two skips/swaps drop
them to excluded.

**Why**: The user can't produce a full avoid-list upfront and reacts yes/no
when shown candidates — this is stated as a feature requirement, not a
quirk. Forcing an immediate binary decision on a genuinely unsure exercise
either loses good variety or risks including something they'll actually
dislike. Letting real usage resolve it removes the need to force an
abstract decision at all.

### Don't generalise an exclusion rule from a few data points

**Decision**: exclusions are recorded per-exercise by default. A general
rule only gets written when the pattern is confirmed by something the user
actually says, not inferred.

**Why, with two real examples**:
- After "no benches, no push-ups, no incline dumbbell press," the
  tempting inference was "supine + free weight" is the excluded pattern.
  Wrong — machine chest press is fine, benches are merely hard to access.
  Had this rule shipped, it would have quietly removed most pressing work.
- When the user asked to replace lying leg curl, the hypothesis was "prone
  position" is out (matching push-ups). Checked before acting: it was
  cramp on that specific machine. Back extension (also prone) stayed on
  the card. This is the correct process, the counter-example to the
  mistake above: check before generalising, don't infer from three points.

## Still valid from Phase 0

### Personal preferences live outside the shared catalog

Unchanged. See original rationale: this may ship to the App Store one day,
so the catalog stays neutral and personal exclusions/preferences load as a
per-user overlay at query time.

### Barbell recommendations respect real loadable increments and floor at
the empty bar's weight

Unchanged, and reinforced by v3: "machine stacks are not all in 5kg
increments, 39kg exists, fine adjust is mandatory" — confirms equipment-
aware rounding is the right general approach, not just for barbells.

### Deload at 2 consecutive failures, discounting sport-adjacent/low-energy
sessions

Already matched what v3 independently specifies, no change needed. v3 adds
one refinement not yet built: any deload should write a visible note to
history explaining itself, rather than just silently recommending a lower
number.

### Hip thrust and assisted pull-up were "deliberately absent, not
excluded"

**Update**: this is now half-resolved. Hip thrust is confirmed excluded
("out of rotation") — no longer an open question. Assisted pull-up moves
to the new "unsure" trial state (see above) rather than staying an open
binary decision. Box jumps joins it in the unsure state as a new addition.

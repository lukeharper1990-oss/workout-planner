from workout_app.rotation_models import Card, CardExercise

# A 6-card rotation. The C variants add different movement patterns rather
# than repeating A/B, and every card was checked for push/pull balance,
# posterior chain coverage on every lower day, and anti-rotation /
# anti-extension core work instead of pure flexion.

LOWER_A = Card(
    name="Lower A",
    bias="lower",
    exercises=[
        CardExercise("Deadlift", "spine", (3, 6), 4),
        CardExercise("Leg Press", "primary", (8, 12), 3),
        CardExercise("Romanian Deadlift", "primary", (8, 10), 3),
        CardExercise("Hack Squat", "accessory", (8, 12), 3),
        CardExercise("Hip Abduction", "accessory", (12, 15), 3),
        CardExercise("Standing Calf Raise", "accessory", (12, 15), 3),
    ],
)

UPPER_B = Card(
    name="Upper B",
    bias="upper",
    exercises=[
        CardExercise("Machine Shoulder Press", "spine", (6, 10), 4),
        CardExercise("T-Bar Row", "primary", (6, 10), 3),
        CardExercise("Pec Deck", "primary", (10, 12), 3),
        CardExercise("Lat Pulldown", "primary", (8, 12), 3),
        CardExercise("Dumbbell Bicep Curl", "accessory", (10, 15), 3),
        CardExercise("Overhead Tricep Extension", "accessory", (10, 15), 3),
    ],
)

UPPER_A = Card(
    name="Upper A",
    bias="upper",
    exercises=[
        CardExercise("Bench Press", "spine", (3, 6), 4),
        CardExercise("Barbell Row", "primary", (8, 10), 3),
        CardExercise("Incline Dumbbell Press", "primary", (8, 12), 3),
        CardExercise("Cable Lateral Raise", "accessory", (12, 15), 3),
        CardExercise("Barbell Bicep Curl", "accessory", (10, 15), 3),
        CardExercise("Skull Crusher", "accessory", (10, 15), 3),
    ],
)

LOWER_B = Card(
    name="Lower B",
    bias="lower",
    exercises=[
        CardExercise("Back Squat", "spine", (3, 6), 4),
        CardExercise("Leg Extension", "primary", (8, 12), 3),
        CardExercise("Bulgarian Split Squat", "primary", (8, 12), 3),
        CardExercise("Leg Curl", "accessory", (10, 15), 3),
        CardExercise("Hip Adduction", "accessory", (12, 15), 3),
        CardExercise("Dumbbell Calf Raise", "accessory", (12, 15), 3),
    ],
)

# Leg Curl sits at primary here, not accessory like Lower B — Lower A and B
# between them already carry all the program's hamstring work (Deadlift,
# RDL, one Leg Curl), leaving this card entirely quad/glute-dominant with
# zero posterior-chain work. For a team-sport player specifically that's a real
# gap, not a style choice — hamstring strains are the sport's most common
# injury. Primary tier gives it real training intensity here rather than
# being an afterthought.
LOWER_C = Card(
    name="Lower C",
    bias="lower",
    exercises=[
        CardExercise("Zercher Squat", "spine", (3, 6), 4),
        CardExercise("Walking Lunge", "primary", (8, 12), 3),
        CardExercise("Leg Curl", "primary", (8, 10), 3),
        CardExercise("Sled Push", "accessory", (10, 15), 3),
        CardExercise("Seated Calf Raise", "accessory", (12, 15), 3),
        CardExercise("Ab Wheel Rollout", "accessory", (10, 15), 3),
    ],
)

# Russian Twist over a flexion move (crunch/leg raise) deliberately — contact sport's
# core demand is absorbing rotational/off-axis force (tackling, being
# tackled, mauling), not spinal flexion.
UPPER_C = Card(
    name="Upper C",
    bias="upper",
    exercises=[
        CardExercise("Incline Barbell Press", "spine", (3, 6), 4),
        CardExercise("Pull-Up", "primary", (8, 12), 3),
        CardExercise("Seated Cable Row", "primary", (8, 12), 3),
        CardExercise("Dumbbell Lateral Raise", "accessory", (12, 15), 3),
        CardExercise("Hammer Curl", "accessory", (10, 15), 3),
        CardExercise("Russian Twist", "accessory", (15, 20), 3),
    ],
)

# Alternates lower/upper so the same muscle groups are never trained on
# back-to-back sessions.
CARD_QUEUE: list[Card] = [LOWER_A, UPPER_A, LOWER_B, UPPER_B, LOWER_C, UPPER_C]


def get_card(name: str) -> Card | None:
    for c in CARD_QUEUE:
        if c.name == name:
            return c
    return None

"""Cue Book: DRAFT English names (standard Pilates terms) for webbook poses, keyed by webbook poseId.
Every entry is emitted with nameEnDraft:true until a native speaker reviews it. Lesson titles stay Korean;
LESSON_TITLE_EN only holds subtitles where the translation is obvious (others -> titleEn null)."""
POSE_EN = {
 1: 'Supported Teaser Prep', 3: 'Rib Cage Breathing', 8: 'Plank', 9: 'Kneeling Side Plank', 11: 'Heel Slide',
 12: 'Bent Knee Fallout', 13: 'Marching', 14: 'Toe Taps', 16: 'Chest Lift', 17: 'Chest Lift with Rotation',
 18: 'The Hundred', 19: 'Half Roll Back', 20: 'Roll Up (Modified)', 21: 'Single Leg Stretch', 22: 'Double Leg Stretch',
 23: 'Scissors (Modified)', 24: 'Criss Cross', 25: 'Single Leg Circle', 26: 'Articulating Bridge', 27: 'Neutral Bridge',
 28: 'Bridge Marching', 29: 'Clam', 30: 'Side Leg Lift', 31: 'Side Kick Front/Back', 32: 'Side Leg Circles',
 33: 'Quadruped Rock Back', 34: 'Cat Stretch', 35: 'Bird Dog', 36: 'Swan Prep', 37: 'Swimming Prep',
 38: 'Spine Stretch Forward', 39: 'Saw (Modified)',
 41: 'Footwork: Parallel Heels', 42: 'Footwork: Parallel Toes', 43: 'Footwork: Small V', 44: 'Footwork: Wide Heels',
 45: 'Calf Raises & Running', 46: 'Single Leg Footwork', 47: 'Reformer Bridge', 48: 'Supine Arm Press',
 49: 'Supine Triceps', 50: 'Supine Arm Circles', 51: 'Feet in Straps: Frog', 52: 'Feet in Straps: Lower & Lift',
 53: 'Feet in Straps: Leg Circles', 54: 'Feet in Straps: Open & Close', 55: 'Coordination (Modified)',
 56: 'Seated Rowing Prep', 57: 'Kneeling Chest Expansion', 58: 'Kneeling Forward Arm Press', 59: 'Side Kneeling Single Arm',
 60: 'Long Box: Pulling Straps', 61: 'Long Box: T Pull', 62: 'Long Box: Breaststroke Prep', 63: 'Short Box: Round Back',
 64: 'Short Box: Flat Back', 65: 'Short Box: Twist', 66: 'Mermaid', 67: 'Elephant (Hip Hinge)',
 68: 'Knee Stretch: Round Back', 69: 'Knee Stretch: Neutral', 70: 'Plank Prep', 71: 'Scooter', 72: 'Supported Lunge',
 73: 'Standing Side Splits', 74: 'Side-Lying Leg Press',
 78: 'Leg Springs: Frog', 79: 'Leg Springs: Walking', 80: 'Leg Springs: Circles', 81: 'Side-Lying Leg Springs',
 82: 'Standing Arm Press (Tower)',
}
LESSON_TITLE_EN = {  # obvious only; everything else stays null
 'basic-01': 'Breathing and leg movement lying down',
 'basic-05': 'Footbar and carriage on the Reformer',
 'basic-07': 'Leg control with feet in straps',
 'basic-11': 'From quadruped to prone',
}
def label(en, kr): return f'{en} · {kr}' if en else kr

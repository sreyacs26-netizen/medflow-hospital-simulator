URGENCY = {"High": 3, "Medium": 2, "Low": 1}

# How much urgency counts compared to waiting time.
# 100 means urgency dominates: waiting time mostly breaks ties.
URGENCY_WEIGHT = 100


def calculate_priority(patient, shortage_mode=False):
    """
    Normal mode:   (urgency x 100) + waiting time
    Shortage mode: (urgency x 100 x survival chance) + waiting time

    survival_chance is a percentage from 0 to 100.
    If a patient has no survival_chance, we assume 100 (no penalty).
    """
    urgency = URGENCY.get(patient["urgency"].capitalize(), 1)
    waiting = patient["waiting_time"]

    if shortage_mode:
        chance = patient.get("survival_chance", 100)
        chance = max(0, min(100, chance))  # keep it between 0 and 100
        return round(urgency * URGENCY_WEIGHT * (chance / 100) + waiting, 1)

    return urgency * URGENCY_WEIGHT + waiting


def sort_patients(patients, shortage_mode=False):
    """Score every patient, then sort highest priority first."""
    for patient in patients:
        patient["priority"] = calculate_priority(patient, shortage_mode)

    patients.sort(key=lambda p: p["priority"], reverse=True)
    return patients

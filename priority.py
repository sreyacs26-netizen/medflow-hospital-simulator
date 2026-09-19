URGENCY = {"High": 3, "Medium": 2, "Low": 1}


def calculate_priority(patient):
    """Priority = (urgency x 10) + waiting time."""
    urgency = URGENCY.get(patient["urgency"].capitalize(), 1)
    return (urgency * 10) + patient["waiting_time"]


def sort_patients(patients):
    """Score every patient, then sort highest priority first."""
    for patient in patients:
        patient["priority"] = calculate_priority(patient)

    patients.sort(key=lambda p: p["priority"], reverse=True)
    return patients

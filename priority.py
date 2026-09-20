"""Patient priority logic used by the MEDFLOW simulator.

Integrated from the team's High/Medium/Low priority model and adapted so the
Streamlit simulator can continue using its Red/Yellow/Green triage labels.
"""

URGENCY = {"High": 3, "Medium": 2, "Low": 1}
TRIAGE_TO_URGENCY = {"Red": "High", "Yellow": "Medium", "Green": "Low"}


def calculate_priority(patient):
    """Priority = (Urgency x 100) + waiting time."""
    urgency_name = patient.get("urgency")
    if urgency_name is None:
        urgency_name = TRIAGE_TO_URGENCY.get(patient.get("triage", "Green"), "Low")
    urgency = URGENCY.get(str(urgency_name).capitalize(), 1)
    waiting_time = patient.get("waiting_time", patient.get("waiting_minutes", 0))
    return (urgency * 100) + int(waiting_time)


def sort_patients(patients):
    """Score every patient and return highest priority first."""
    for patient in patients:
        patient["priority"] = calculate_priority(patient)
    return sorted(patients, key=lambda p: p["priority"], reverse=True)

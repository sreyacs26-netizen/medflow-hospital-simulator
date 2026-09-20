from priority import sort_patients
from resources import HospitalResources

DEPARTMENT_MAP = {
    "Heart transplant": "Cardiology",
    "Fracture": "Orthopedics",
    "Brain condition": "Neurology",
    "Appendix / abdominal surgery": "General Surgery",
    "Kidney condition": "Nephrology",
    "Emergency injury": "Emergency",
    "Routine illness": "General",
    "Chest pain": "Cardiology",
}


def build_patients():
    # Synthetic demonstration cases. They are not real patient records.
    # A larger first wave is used so the simulator visibly demonstrates queuing.
    return [
        {"id":"P001", "condition":"Heart transplant", "department":"Cardiology", "triage":"Red", "resource":"ICU", "treatment_minutes":35, "arrival_time":0},
        {"id":"P002", "condition":"Fracture", "department":"Orthopedics", "triage":"Yellow", "resource":"Bed", "treatment_minutes":25, "arrival_time":0},
        {"id":"P003", "condition":"Emergency injury", "department":"Emergency", "triage":"Green", "resource":"Bed", "treatment_minutes":20, "arrival_time":0},
        {"id":"P004", "condition":"Appendix / abdominal surgery", "department":"General Surgery", "triage":"Red", "resource":"Surgery", "treatment_minutes":45, "arrival_time":0},
        {"id":"P005", "condition":"Kidney condition", "department":"Nephrology", "triage":"Yellow", "resource":"Bed", "treatment_minutes":30, "arrival_time":0},
        {"id":"P006", "condition":"Chest pain", "department":"Cardiology", "triage":"Red", "resource":"ICU", "treatment_minutes":50, "arrival_time":0},
        {"id":"P007", "condition":"Brain condition", "department":"Neurology", "triage":"Yellow", "resource":"Bed", "treatment_minutes":18, "arrival_time":0},
        {"id":"P008", "condition":"Fracture", "department":"Orthopedics", "triage":"Green", "resource":"Surgery", "treatment_minutes":15, "arrival_time":0},
        {"id":"P009", "condition":"Chest pain", "department":"Cardiology", "triage":"Red", "resource":"Bed", "treatment_minutes":25, "arrival_time":0},
        {"id":"P010", "condition":"Routine illness", "department":"General", "triage":"Green", "resource":"Bed", "treatment_minutes":20, "arrival_time":0},
        {"id":"P011", "condition":"Heart transplant", "department":"Cardiology", "triage":"Yellow", "resource":"Surgery", "treatment_minutes":40, "arrival_time":0},
        {"id":"P012", "condition":"Brain condition", "department":"Neurology", "triage":"Red", "resource":"ICU", "treatment_minutes":30, "arrival_time":0},
        {"id":"P013", "condition":"Fracture", "department":"Orthopedics", "triage":"Yellow", "resource":"Bed", "treatment_minutes":20, "arrival_time":0},
        {"id":"P014", "condition":"Appendix / abdominal surgery", "department":"General Surgery", "triage":"Yellow", "resource":"Surgery", "treatment_minutes":35, "arrival_time":0},
        {"id":"P015", "condition":"Chest pain", "department":"Cardiology", "triage":"Red", "resource":"ICU", "treatment_minutes":30, "arrival_time":0},
        {"id":"P016", "condition":"Kidney condition", "department":"Nephrology", "triage":"Green", "resource":"Bed", "treatment_minutes":25, "arrival_time":0},
        {"id":"P017", "condition":"Heart transplant", "department":"Cardiology", "triage":"Red", "resource":"ICU", "treatment_minutes":40, "arrival_time":5},
        {"id":"P018", "condition":"Fracture", "department":"Orthopedics", "triage":"Yellow", "resource":"Bed", "treatment_minutes":20, "arrival_time":5},
        {"id":"P019", "condition":"Brain condition", "department":"Neurology", "triage":"Red", "resource":"ICU", "treatment_minutes":30, "arrival_time":10},
        {"id":"P020", "condition":"Routine illness", "department":"General", "triage":"Green", "resource":"Bed", "treatment_minutes":20, "arrival_time":10},
        {"id":"P021", "condition":"Appendix / abdominal surgery", "department":"General Surgery", "triage":"Red", "resource":"Surgery", "treatment_minutes":35, "arrival_time":15},
        {"id":"P022", "condition":"Chest pain", "department":"Cardiology", "triage":"Yellow", "resource":"Bed", "treatment_minutes":25, "arrival_time":20},
    ]


def new_state():
    patients = build_patients()
    for p in patients:
        p.update({
            "status": "Not Arrived",
            "waiting_minutes": 0,
            "priority": 0,
        })
    return {"patients": patients, "resources": HospitalResources(), "clock": 0, "completed": 0, "surge_active": False, "surge_transfers": []}


def activate_arrivals(state):
    """Bring patients into the system when their scheduled arrival time is reached."""
    for patient in state["patients"]:
        if patient["status"] == "Not Arrived" and patient["arrival_time"] <= state["clock"]:
            patient["status"] = "Waiting"
            patient["waiting_minutes"] = 0
            patient.pop("waiting_reason", None)
            patient["routing_message"] = "Patient arrived"


def update_waiting_times(state):
    for patient in state["patients"]:
        if patient["status"] == "Waiting":
            patient["waiting_minutes"] = max(0, state["clock"] - patient["arrival_time"])



def waiting_reason(patient, resources):
    """Explain every currently unavailable requirement for a waiting patient."""
    reasons = resources.missing_patient_resources(patient)
    return " + ".join(reasons) if reasons else "Waiting for resource allocation"


def _route_ready_patients(state):
    """Assign specialists and treatment resources without consuming capacity that is unavailable."""
    resources = state["resources"]

    for patient in sort_patients(state["patients"]):
        if patient["status"] != "Waiting":
            continue

        # This combines Person 2's all-required-resources check with the
        # original MEDFLOW specialist-first routing.
        missing = resources.missing_patient_resources(patient)
        specialist_missing = not resources.can_assign_specialist(patient["department"])

        if specialist_missing:
            if not resources.assign_emergency(
                patient,
                reason=f"{patient['department']} specialist unavailable"
            ):
                patient["waiting_reason"] = waiting_reason(patient, resources)
            continue

        if missing:
            patient["waiting_reason"] = waiting_reason(patient, resources)
            continue

        if resources.assign_specialist_direct(patient):
            patient.pop("waiting_reason", None)
            if resources.allocate_department_resources(patient):
                patient["start_time"] = state["clock"]
            else:
                # Defensive fallback; resource availability was checked first.
                patient["status"] = "Waiting"
                patient["waiting_reason"] = waiting_reason(patient, resources)


def _finish_emergency_stabilization(state):
    """Move stabilized patients onward only when their next-step resources fit."""
    resources = state["resources"]
    for patient in sort_patients(state["patients"]):
        if patient["status"] != "Emergency Stabilization" or patient.get("emergency_remaining", 0) > 0:
            continue

        # Release the temporary Emergency doctor/nurse before checking the
        # next-step resources. They should not remain occupied after the
        # 10-minute stabilization period.
        if patient.get("emergency_doctor_assigned"):
            if patient.get("emergency_doctor_type") == "Emergency":
                resources.available_department_doctors["Emergency"] += 1
            else:
                resources.available_general_doctors += 1
            patient["emergency_doctor_assigned"] = False
            resources.available_nurses += 1

        if not resources.can_assign_specialist(patient["department"]):
            patient["status"] = "Waiting"
            patient["location"] = "Queue"
            patient["waiting_reason"] = f"{patient['department']} specialist unavailable"
            continue

        missing = resources.missing_patient_resources(patient)
        if missing:
            patient["status"] = "Waiting"
            patient["location"] = "Queue"
            patient["waiting_reason"] = waiting_reason(patient, resources)
            continue

        if resources.assign_specialist_direct(patient):
            patient.pop("waiting_reason", None)
            if resources.allocate_department_resources(patient):
                patient["start_time"] = state["clock"]
            else:
                patient["status"] = "Waiting"
                patient["waiting_reason"] = waiting_reason(patient, resources)



def trigger_emergency_surge(state):
    """Create a synthetic emergency surge and route overflow for external transfer.

    This is a demonstration mode: a sudden wave of emergency patients is added
    at the current simulation time. Emergency doctors/nurses are used first;
    patients who cannot be accepted because emergency capacity is exhausted
    are flagged for transfer to another hospital.
    """
    if state.get("surge_active"):
        return state

    state["surge_active"] = True
    state["surge_transfers"] = []
    base = len(state["patients"]) + 1

    surge_cases = [
        ("Emergency injury", "Red", "Bed", 25),
        ("Emergency injury", "Red", "ICU", 35),
        ("Emergency injury", "Red", "Bed", 20),
        ("Emergency injury", "Red", "ICU", 30),
        ("Emergency injury", "Yellow", "Bed", 25),
        ("Emergency injury", "Red", "Bed", 30),
        ("Emergency injury", "Yellow", "Bed", 20),
        ("Emergency injury", "Red", "ICU", 40),
        ("Emergency injury", "Yellow", "Bed", 25),
        ("Emergency injury", "Red", "Bed", 30),
    ]

    for i, (condition, triage, resource, treatment) in enumerate(surge_cases):
        patient = {
            "id": f"ES{base+i:03d}",
            "condition": condition,
            "department": "Emergency",
            "triage": triage,
            "resource": resource,
            "treatment_minutes": treatment,
            "arrival_time": state["clock"],
            "status": "Waiting",
            "waiting_minutes": 0,
            "priority": 0,
            "surge_patient": True,
            "routing_message": "Emergency surge arrival",
        }
        state["patients"].append(patient)

    # First attempt normal allocation in priority order.
    activate_arrivals(state)
    update_waiting_times(state)
    _route_ready_patients(state)
    _finish_emergency_stabilization(state)

    # Remaining surge patients are the simulated external-transfer overflow.
    for patient in state["patients"]:
        if patient.get("surge_patient") and patient["status"] == "Waiting":
            reason = waiting_reason(patient, state["resources"])
            patient["status"] = "External Transfer Recommended"
            patient["location"] = "Transfer Coordination"
            patient["waiting_reason"] = reason
            patient["transfer_reason"] = f"Emergency surge overflow: {reason}"
            state["surge_transfers"].append(patient["id"])

    return state

def allocate_waiting(state):
    activate_arrivals(state)
    update_waiting_times(state)
    _route_ready_patients(state)
    _finish_emergency_stabilization(state)
    return state


def tick(state, minutes=5):
    state["clock"] += minutes
    resources = state["resources"]

    # New arrivals enter every 5 simulated minutes.
    activate_arrivals(state)
    update_waiting_times(state)

    # Emergency stabilization runs for 10 simulated minutes.
    for patient in state["patients"]:
        if patient["status"] == "Emergency Stabilization":
            patient["emergency_remaining"] -= minutes

    _finish_emergency_stabilization(state)

    # Treatment continues while assigned specialist/nurse/facility are occupied.
    for patient in state["patients"]:
        if patient["status"] == "In Treatment":
            patient["remaining_minutes"] -= minutes
            if patient["remaining_minutes"] <= 0:
                # Serious/ICU cases leave ICU after treatment and enter a
                # short recovery stay in a General Bed.
                if patient.get("allocated_resource") == "ICU":
                    resources.release(patient, retain_general_bed=True)
                    patient["status"] = "Post-ICU Recovery"
                    patient["location"] = "General Bed"
                    patient["remaining_minutes"] = 10
                    patient["recovery_remaining"] = 10
                    patient["routing_message"] = "ICU treatment complete → shifted to General Bed for recovery"
                else:
                    resources.release(patient)
                    patient["status"] = "Completed"
                    patient["end_time"] = state["clock"]
                    state["completed"] += 1

    # Short post-ICU recovery in a General Bed.
    for patient in state["patients"]:
        if patient["status"] == "Post-ICU Recovery":
            patient["recovery_remaining"] -= minutes
            patient["remaining_minutes"] = max(0, patient["recovery_remaining"])
            if patient["recovery_remaining"] <= 0:
                resources.release_recovery_bed(patient)
                patient["status"] = "Completed"
                patient["location"] = "Completed"
                patient["end_time"] = state["clock"]
                patient["routing_message"] = "Post-ICU recovery complete → patient discharged from monitored bed"
                state["completed"] += 1

    # New arrivals and newly freed resources are processed immediately.
    activate_arrivals(state)
    update_waiting_times(state)
    _finish_emergency_stabilization(state)
    _route_ready_patients(state)

    return state


def metrics(state):
    patients = state["patients"]
    waiting = sum(p["status"] == "Waiting" for p in patients)
    emergency = sum(p["status"] == "Emergency Stabilization" for p in patients)
    ready = sum(p["status"] == "Ready for Resource Allocation" for p in patients)
    treating = sum(p["status"] == "In Treatment" for p in patients)
    post_icu = sum(p["status"] == "Post-ICU Recovery" for p in patients)
    completed = sum(p["status"] == "Completed" for p in patients)
    arrived = sum(p["status"] != "Not Arrived" for p in patients)
    waits = [p["waiting_minutes"] for p in patients if p["status"] != "Waiting" and p["status"] != "Not Arrived"]
    return {
        "total": arrived,
        "waiting": waiting,
        "emergency": emergency,
        "ready": ready,
        "treating": treating,
        "post_icu": post_icu,
        "completed": completed,
        "not_arrived": len(patients) - arrived,
        "avg_wait": round(sum(waits) / len(waits), 1) if waits else 0,
        "surge_transfers": len(state.get("surge_transfers", [])),
        "surge_active": bool(state.get("surge_active", False)),
    }

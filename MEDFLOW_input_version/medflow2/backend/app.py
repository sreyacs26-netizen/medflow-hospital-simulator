from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

URGENCY = {"High": 3, "Medium": 2, "Low": 1}

DEFAULT_HOSPITAL = {
    "beds": {"total": 100, "available": 63},
    "icu": {"total": 10, "available": 3},
    "doctors": {"total": 20, "available": 8},
    "nurses": {"total": 40, "available": 15},
    "operating_rooms": {"total": 5, "available": 2}
}

DEFAULT_PATIENTS = [
    {"id": "P001", "urgency": "High", "waiting_time": 5, "needs": ["icu", "doctor", "nurse"]},
    {"id": "P002", "urgency": "Medium", "waiting_time": 8, "needs": ["bed", "doctor", "nurse"]},
    {"id": "P003", "urgency": "High", "waiting_time": 2, "needs": ["icu", "doctor", "nurse"]},
    {"id": "P004", "urgency": "Low", "waiting_time": 20, "needs": ["bed", "nurse"]},
    {"id": "P005", "urgency": "Medium", "waiting_time": 12, "needs": ["bed", "doctor"]},
    {"id": "P006", "urgency": "High", "waiting_time": 10, "needs": ["operating_rooms", "doctor", "nurse"]},
]


def calculate_priority(patient):
    urgency = URGENCY.get(patient["urgency"].capitalize(), 1)
    return (urgency * 10) + patient["waiting_time"]


def normalize_hospital(data):
    result = {}
    for key, default in DEFAULT_HOSPITAL.items():
        raw = data.get(key, {}) if isinstance(data, dict) else {}
        total = int(raw.get("total", default["total"]))
        available = int(raw.get("available", total))
        total = max(0, total)
        available = max(0, min(available, total))
        result[key] = {"total": total, "available": available}
    return result


def normalize_patients(data):
    if not isinstance(data, list):
        raise ValueError("Patients must be a list.")

    clean = []
    for index, raw in enumerate(data, start=1):
        if not isinstance(raw, dict):
            raise ValueError("Each patient must be an object.")

        patient_id = str(raw.get("id", f"P{index:03d}")).strip() or f"P{index:03d}"
        urgency = str(raw.get("urgency", "Low")).capitalize()
        if urgency not in URGENCY:
            raise ValueError(f"Invalid urgency for {patient_id}.")

        waiting_time = int(raw.get("waiting_time", 0))
        if waiting_time < 0:
            raise ValueError(f"Waiting time cannot be negative for {patient_id}.")

        needs = raw.get("needs", [])
        if not isinstance(needs, list):
            raise ValueError(f"Needs must be a list for {patient_id}.")

        allowed = {"bed", "icu", "doctor", "nurse", "operating_rooms"}
        needs = [str(n) for n in needs if str(n) in allowed]

        clean.append({
            "id": patient_id,
            "urgency": urgency,
            "waiting_time": waiting_time,
            "needs": needs
        })

    return clean


def sorted_patients(patient_list):
    result = []
    for patient in patient_list:
        p = dict(patient)
        p["priority"] = calculate_priority(p)
        result.append(p)
    return sorted(result, key=lambda p: p["priority"], reverse=True)


def allocate_resources(hospital, patient_list):
    # Convert hospital resource names to the names used by patient needs.
    remaining = {
        "bed": hospital["beds"]["available"],
        "icu": hospital["icu"]["available"],
        "doctor": hospital["doctors"]["available"],
        "nurse": hospital["nurses"]["available"],
        "operating_rooms": hospital["operating_rooms"]["available"],
    }

    results = []
    for patient in sorted_patients(patient_list):
        missing = [need for need in patient["needs"] if remaining.get(need, 0) <= 0]

        if not missing:
            for need in patient["needs"]:
                remaining[need] -= 1
            status = "Allocated"
            reason = "All required resources available."
        else:
            status = "Waiting"
            reason = "Waiting for: " + ", ".join(missing) + "."

        results.append({**patient, "status": status, "reason": reason})

    return results, remaining


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/hospital")
def get_hospital():
    return jsonify(DEFAULT_HOSPITAL)


@app.route("/api/patients")
def get_patients():
    return jsonify(sorted_patients(DEFAULT_PATIENTS))


@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json(silent=True) or {}

    try:
        hospital = normalize_hospital(data.get("hospital", DEFAULT_HOSPITAL))
        patients = normalize_patients(data.get("patients", DEFAULT_PATIENTS))
        results, remaining = allocate_resources(hospital, patients)

        treated = sum(1 for p in results if p["status"] == "Allocated")
        waiting = len(results) - treated
        average_waiting = round(sum(p["waiting_time"] for p in results) / len(results), 1) if results else 0

        remaining_display = {
            "beds": remaining["bed"],
            "icu": remaining["icu"],
            "doctors": remaining["doctor"],
            "nurses": remaining["nurse"],
            "operating_rooms": remaining["operating_rooms"],
        }

        return jsonify({
            "message": "Simulation completed.",
            "patients": results,
            "metrics": {
                "total_patients": len(results),
                "treated": treated,
                "waiting": waiting,
                "average_waiting": average_waiting,
            },
            "remaining": remaining_display,
        })

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)

from priority import sort_patients

patients = [
    {"id": "P001", "urgency": "High", "waiting_time": 5},
    {"id": "P002", "urgency": "Medium", "waiting_time": 20},
    {"id": "P003", "urgency": "Low", "waiting_time": 10},
    {"id": "P004", "urgency": "High", "waiting_time": 2},
]

for p in sort_patients(patients):
    print(p["id"], "→", p["priority"])

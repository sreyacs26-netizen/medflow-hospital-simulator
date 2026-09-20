from copy import deepcopy
from priority import sort_patients

patients = [
    {"id": "P001", "urgency": "High", "waiting_time": 5, "survival_chance": 90},
    {"id": "P002", "urgency": "Medium", "waiting_time": 20, "survival_chance": 80},
    {"id": "P003", "urgency": "Low", "waiting_time": 10, "survival_chance": 95},
    {"id": "P004", "urgency": "High", "waiting_time": 2, "survival_chance": 10},
]

print("NORMAL MODE")
for p in sort_patients(deepcopy(patients)):
    print(p["id"], "->", p["priority"])

print()
print("SHORTAGE MODE")
for p in sort_patients(deepcopy(patients), shortage_mode=True):
    print(p["id"], "->", p["priority"])

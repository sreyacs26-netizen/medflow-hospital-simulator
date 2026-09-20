# MEDFLOW - Hospital Resource Management Simulator

This beginner-friendly prototype lets you enter hospital resources and patient data, then runs a simple mathematical priority and resource-allocation simulation.

## Run

From the MEDFLOW_starter folder:

```bash
pip install flask flask-cors
python backend\\app.py
```

Open http://127.0.0.1:5000

## How the simulation works

1. Enter available hospital resources.
2. Add/edit patient information.
3. Click Run MEDFLOW Simulation.
4. Backend calculates `Priority = (Urgency x 10) + Waiting Time`.
5. Patients are processed from highest priority to lowest.
6. For each patient, the backend checks whether all required resources are available.
7. The dashboard shows treated/waiting patients and remaining resources.

The patient and hospital values are synthetic demo data.

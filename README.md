# MEDFLOW — Hospital Resource Management Simulator

MEDFLOW is a Streamlit-based hospital resource management simulator developed for Hack-a-Matics 2026.

The project combines the team's three contributions into one working prototype:

- **Frontend / integration:** Streamlit operations dashboard, simulation controls, patient flow, resource tables and waiting queue.
- **Priority model:** `Priority = (Urgency × 100) + Waiting Time`, with High/Medium/Low urgency mapped to the existing Red/Yellow/Green triage labels.
- **Resource-allocation model:** checks all required resources before allocation and reports the exact bottleneck when a patient must wait.

## Simulation flow

```text
Patient arrival
      ↓
Priority calculation
      ↓
Specialist availability check
      ↓
If specialist unavailable → Emergency stabilization
      ↓
Required resource check
      ↓
Bed / ICU / Operating Room allocation
      ↓
Treatment
      ↓
Resource release
      ↓
ICU cases → short General Bed recovery → completion
```

## Emergency surge

The sidebar includes a demo **Trigger Emergency Surge** button. It creates a synthetic wave of emergency arrivals. When emergency capacity is exhausted, overflow cases are marked **External Transfer Recommended** and shown in a dedicated transfer table. This is a simulation feature, not a real transfer protocol.

## Resource checks

Each treatment case requires a doctor and nurse plus the treatment resource:

- **ICU:** ICU bed + general bed
- **General bed:** general bed
- **Surgery:** operating room + general bed

If a required resource is unavailable, the patient stays in the waiting queue and the dashboard shows the reason, for example `No ICU bed available` or `Operating room` / specialist constraints.

## Run locally

From the project folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Files

- `app.py` — Streamlit frontend and dashboard
- `simulation.py` — patient arrivals, priority ordering, routing, treatment and simulation clock
- `priority.py` — integrated team priority calculation
- `resources.py` — hospital capacity and allocation logic
- `test_priority.py` — basic priority-system test
- `DESIGN_BASIS.md` — prototype assumptions and design scope

## Scope

All patient cases, staffing levels and hospital capacities are synthetic demonstration data. The routing and scheduling rules are simplified prototype assumptions and are **not clinical decision formulas or medical advice**.

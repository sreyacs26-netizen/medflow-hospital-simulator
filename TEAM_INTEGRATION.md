# Team Integration Notes

This repository contains the integrated MEDFLOW prototype.

## Contribution 1 — Priority system

The team's High/Medium/Low priority model is used as the common priority layer:

`Priority = (Urgency × 100) + Waiting Time`

The Streamlit simulator uses Red/Yellow/Green labels, so they are mapped as:

- Red → High (3)
- Yellow → Medium (2)
- Green → Low (1)

`priority.py` also accepts `urgency` + `waiting_time` directly, so the standalone priority test remains compatible with the team's original prototype.

## Contribution 2 — Resource allocation prototype

The Flask prototype's core idea was integrated into the Streamlit simulation: before a patient is allocated, MEDFLOW checks all required resources and records the missing resources as the waiting reason.

The integrated simulator keeps the original MEDFLOW specialist routing and emergency-stabilization workflow while using the team's all-required-resources check.

## Contribution 3 — Frontend / integration

The final user interface is the Streamlit dashboard. It presents:

- hospital capacity
- doctor/department availability
- waiting patients and exact waiting reasons
- active patient flow
- treatment status
- completed operations
- simulation controls
- the integrated priority/resource model

The separate Flask/HTML/CSS/JS frontend was not copied into the final runtime because the project uses Streamlit as its single application interface. Its resource-allocation concepts are represented in the integrated Python simulation.

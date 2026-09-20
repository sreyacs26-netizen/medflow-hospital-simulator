# medflow-hospital-simulator
Hospital resource management simulator for Hack-a-Matics 2026
# MEDFLOW — Hospital Resource Management Simulator

MEDFLOW is a hospital resource management simulator developed for our hackathon.

## Problem

Hospitals have limited resources such as beds, ICU beds, doctors, nurses and operating rooms. At the same time, patients can have different urgency levels and waiting times.

MEDFLOW simulates how these limited resources can be allocated to patients.

## How it works

The system takes:

- Hospital resource availability
- Patient urgency
- Patient waiting time
- Patient resource requirements

The system then:

1. Calculates a priority score for each patient.
2. Sorts patients according to priority.
3. Checks whether the required resources are available.
4. Allocates resources when possible.
5. Keeps patients waiting when resources are unavailable.
6. Displays the results through a dashboard.

## Mathematical Model

Our current prototype uses:

Priority = (Urgency × 100) + Waiting Time

Urgency values:

- High = 3
- Medium = 2
- Low = 1

This is a simulation heuristic used to demonstrate priority-based hospital resource allocation.

## Technology

- Python
- Flask
- HTML
- CSS
- JavaScript

## Current Status

The current prototype supports:

- Hospital resource inputs
- Patient inputs
- Priority calculation
- Resource allocation
- Resource shortage simulation
- Patient evaluation
- Simulation results

## Future Improvements

- Improve the priority/optimization model
- Add more realistic hospital scenarios
- Add charts and resource utilization metrics
- Compare different allocation strategies
- Improve the simulation over time
#Prototype:1
backend/
frontend/
README.md
.gitignore

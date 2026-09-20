# MEDFLOW design basis

## 1. What comes from the hackathon problem statement
The brochure requires the simulator to represent incoming patients with different urgency levels, maintain a queue, track beds/ICU/operating rooms/doctors/nurses/emergency vehicles, assign resources, prioritize urgent cases, account for waiting time, prevent conflicts/capacity violations, calculate utilization, and display results through an operations dashboard.

## 2. What is a prototype assumption added by the team
- Every arriving patient first enters Emergency Stabilization.
- Emergency stabilization lasts 10 simulated minutes.
- After stabilization, the patient is transferred to a required specialist department when a specialist is available.
- If the specialist is busy, the patient remains under Emergency supervision rather than being left untreated.
- Department doctor counts are synthetic demo values.
- Condition-to-department mapping is simplified and is not a medical diagnostic model.

## 3. Why use synthetic staffing numbers
The project needs controllable capacity constraints to demonstrate scheduling. Real individual hospital staffing data is not needed and should not be used.

## 4. Priority logic
Priority = triage score × 100 + waiting minutes, where Red=3, Yellow=2, Green=1. This makes urgency dominant and waiting time a secondary scheduling factor. This is a demonstration formula, not a clinically validated triage or scheduling score.


## Emergency surge demonstration
The prototype includes a manual emergency-surge mode. A synthetic wave of emergency patients is added to demonstrate capacity overload. Patients that cannot be accepted because emergency resources are exhausted are flagged for external hospital transfer in a dedicated dashboard table. This is a simplified simulation assumption, not a clinical or real-world transfer protocol.

class HospitalResources:
    """Simplified synthetic hospital capacity for the MEDFLOW prototype."""

    def __init__(self):
        # Demo capacities, not real hospital staffing numbers.
        self.department_doctors = {
            "Cardiology": 2,
            "Orthopedics": 2,
            "Neurology": 1,
            "General Surgery": 2,
            "Nephrology": 1,
            "Emergency": 3,
        }
        self.general_doctors = 2
        self.total_doctors = sum(self.department_doctors.values()) + self.general_doctors
        self.total_nurses = 14
        self.total_beds = 20
        self.total_icu = 4
        self.total_or = 2

        self.available_department_doctors = dict(self.department_doctors)
        self.available_general_doctors = self.general_doctors
        self.available_nurses = self.total_nurses
        self.available_beds = self.total_beds
        self.available_icu = self.total_icu
        self.available_or = self.total_or

    def patient_needs(self, patient):
        """Return the resource names required by a patient.

        This mirrors the resource-checking model contributed in the Flask
        prototype, while using MEDFLOW's department/specialist terminology.
        """
        needs = ["doctor", "nurse"]
        resource = patient.get("resource")
        if resource == "ICU":
            needs.extend(["icu", "bed"])
        elif resource == "Bed":
            needs.append("bed")
        elif resource == "Surgery":
            needs.extend(["operating_room", "bed"])
        return needs

    def available_for_need(self, need, department=None):
        if need == "doctor":
            return self.can_assign_specialist(department)
        if need == "nurse":
            return self.available_nurses > 0
        if need == "bed":
            return self.available_beds > 0
        if need == "icu":
            return self.available_icu > 0
        if need == "operating_room":
            return self.available_or > 0
        return False

    def missing_patient_resources(self, patient):
        """Return every currently unavailable requirement for a patient."""
        department = patient.get("department")
        missing = []
        labels = {
            "doctor": f"{department} specialist",
            "nurse": "nurse",
            "bed": "general bed",
            "icu": "ICU bed",
            "operating_room": "operating room",
        }
        for need in self.patient_needs(patient):
            if not self.available_for_need(need, department):
                missing.append(labels[need])
        return missing

    def can_assign_specialist(self, department):
        if department == "General":
            return self.available_general_doctors > 0
        return self.available_department_doctors.get(department, 0) > 0

    def assign_specialist_direct(self, patient):
        """Send a patient directly to the required department when a specialist is free."""
        dept = patient["department"]
        if not self.can_assign_specialist(dept) or self.available_nurses <= 0:
            return False
        if dept == "General":
            self.available_general_doctors -= 1
        else:
            self.available_department_doctors[dept] -= 1
        self.available_nurses -= 1
        patient["specialist_assigned"] = True
        patient["assigned_department"] = dept
        patient["assigned_doctor"] = "General Doctor" if dept == "General" else dept + " Specialist"
        patient["status"] = "Ready for Resource Allocation"
        patient["location"] = dept
        patient["routing_message"] = f"Direct to {dept}: specialist available"
        return True

    def find_doctor(self, department):
        if self.available_department_doctors.get(department, 0) > 0:
            return department
        # A general doctor can cover general/non-specialist care, but not a specialty requirement.
        if department == "Emergency" and self.available_general_doctors > 0:
            return "General"
        return None

    def assign_emergency(self, patient, reason="Specialist unavailable"):
        # Every arriving patient is first stabilized in Emergency.
        # An Emergency doctor is preferred; a general doctor can temporarily
        # cover Emergency when all Emergency specialists are occupied.
        if self.available_nurses <= 0:
            return False

        if self.available_department_doctors.get("Emergency", 0) > 0:
            self.available_department_doctors["Emergency"] -= 1
            patient["emergency_doctor_type"] = "Emergency"
        elif self.available_general_doctors > 0:
            self.available_general_doctors -= 1
            patient["emergency_doctor_type"] = "General"
        else:
            return False

        self.available_nurses -= 1
        patient["emergency_doctor_assigned"] = True
        patient["status"] = "Emergency Stabilization"
        patient["location"] = "Emergency Department"
        patient["emergency_remaining"] = 10
        patient["routing_message"] = f"{reason} → sent to Emergency for temporary stabilization"
        return True

    def transfer_to_department(self, patient):
        dept = patient["department"]
        if not self.can_assign_specialist(dept):
            return False
        if self.available_nurses <= 0:
            return False

        # Release temporary emergency doctor + nurse first.
        if patient.get("emergency_doctor_assigned"):
            if patient.get("emergency_doctor_type") == "Emergency":
                self.available_department_doctors["Emergency"] += 1
            else:
                self.available_general_doctors += 1
            patient["emergency_doctor_assigned"] = False
            self.available_nurses += 1

        if dept == "General":
            self.available_general_doctors -= 1
        else:
            self.available_department_doctors[dept] -= 1
        self.available_nurses -= 1
        patient["specialist_assigned"] = True
        patient["assigned_department"] = dept
        patient["assigned_doctor"] = "General Doctor" if dept == "General" else dept + " Specialist"
        patient["status"] = "Ready for Resource Allocation"
        patient["location"] = dept
        patient["routing_message"] = f"Emergency stabilization complete → transferred to {dept}"
        return True

    def allocate_department_resources(self, patient):
        if patient["status"] != "Ready for Resource Allocation":
            return False

        r = patient["resource"]
        if r == "ICU":
            ok = self.available_icu > 0 and self.available_beds > 0
        elif r == "Bed":
            ok = self.available_beds > 0
        elif r == "Surgery":
            ok = self.available_or > 0 and self.available_beds > 0
        else:
            ok = False

        if not ok:
            return False

        if r == "ICU":
            self.available_icu -= 1
            self.available_beds -= 1
        elif r == "Bed":
            self.available_beds -= 1
        elif r == "Surgery":
            self.available_or -= 1
            self.available_beds -= 1

        patient["allocated_resource"] = r
        patient["status"] = "In Treatment"
        patient["location"] = "Operating Room" if r == "Surgery" else ("ICU" if r == "ICU" else "General Bed")
        patient["remaining_minutes"] = patient["treatment_minutes"]
        return True

    def release(self, patient, retain_general_bed=False):
        """Release treatment staff/resources.

        When ICU treatment is complete, retain the bed allocation as a
        general-bed recovery stay while releasing the ICU resource.
        """
        dept = patient.get("department")
        if patient.get("specialist_assigned"):
            if dept == "General":
                self.available_general_doctors += 1
            elif dept in self.available_department_doctors:
                self.available_department_doctors[dept] += 1
            patient["specialist_assigned"] = False

        self.available_nurses += 1
        r = patient.get("allocated_resource")
        if r == "ICU":
            self.available_icu += 1
            if retain_general_bed:
                patient["allocated_resource"] = "Bed"
                patient["location"] = "General Bed"
            else:
                self.available_beds += 1
        elif r == "Bed":
            if not retain_general_bed:
                self.available_beds += 1
        elif r == "Surgery":
            self.available_or += 1
            self.available_beds += 1

    def release_recovery_bed(self, patient):
        """Release a General Bed after the short post-ICU recovery stay."""
        if patient.get("allocated_resource") == "Bed":
            self.available_beds += 1
            patient["allocated_resource"] = None

    def status(self):
        return {
            "Beds": self.available_beds,
            "ICU Beds": self.available_icu,
            "Nurses": self.available_nurses,
            "Operating Rooms": self.available_or,
            "Doctors": sum(self.available_department_doctors.values()) + self.available_general_doctors,
        }

    def doctor_status(self):
        rows = []
        for dept, total in self.department_doctors.items():
            available = self.available_department_doctors[dept]
            rows.append({"Department": dept, "Total": total, "Available": available, "Busy": total - available})
        rows.append({"Department": "General", "Total": self.general_doctors, "Available": self.available_general_doctors, "Busy": self.general_doctors - self.available_general_doctors})
        return rows

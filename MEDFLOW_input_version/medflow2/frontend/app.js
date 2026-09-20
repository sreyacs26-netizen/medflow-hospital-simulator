const defaultPatients = [
    { id: "P001", urgency: "High", waiting_time: 5, needs: ["icu", "doctor", "nurse"] },
    { id: "P002", urgency: "Medium", waiting_time: 8, needs: ["bed", "doctor", "nurse"] },
    { id: "P003", urgency: "High", waiting_time: 2, needs: ["icu", "doctor", "nurse"] },
];

const labels = {
    bed: "Bed",
    icu: "ICU",
    doctor: "Doctor",
    nurse: "Nurse",
    operating_rooms: "Operating Room"
};

let patientCount = 0;

function addPatient(patient = null) {
    patientCount += 1;
    const id = patient?.id || `P${String(patientCount).padStart(3, "0")}`;
    const needs = patient?.needs || ["bed", "doctor"];
    const card = document.createElement("div");
    card.className = "patient-input-card";
    card.dataset.patientId = id;
    card.innerHTML = `
        <div class="patient-input-head">
            <strong>${id}</strong>
            <button type="button" class="remove-btn">Remove</button>
        </div>
        <div class="patient-fields">
            <label>Patient ID <input class="p-id" value="${id}"></label>
            <label>Urgency
                <select class="p-urgency">
                    <option ${patient?.urgency === "High" ? "selected" : ""}>High</option>
                    <option ${patient?.urgency === "Medium" ? "selected" : ""}>Medium</option>
                    <option ${patient?.urgency === "Low" ? "selected" : ""}>Low</option>
                </select>
            </label>
            <label>Waiting time (min) <input class="p-wait" type="number" min="0" value="${patient?.waiting_time ?? 5}"></label>
        </div>
        <div class="needs">
            <span>Resources needed:</span>
            ${Object.keys(labels).map(key => `
                <label class="check"><input type="checkbox" value="${key}" ${needs.includes(key) ? "checked" : ""}> ${labels[key]}</label>
            `).join("")}
        </div>
    `;

    card.querySelector(".remove-btn").addEventListener("click", () => card.remove());
    document.getElementById("patientInputs").appendChild(card);
}

function collectPatients() {
    return [...document.querySelectorAll(".patient-input-card")].map(card => ({
        id: card.querySelector(".p-id").value.trim(),
        urgency: card.querySelector(".p-urgency").value,
        waiting_time: Number(card.querySelector(".p-wait").value),
        needs: [...card.querySelectorAll(".check input:checked")].map(input => input.value)
    }));
}

function collectHospital() {
    return {
        beds: { total: Number(document.getElementById("beds").value), available: Number(document.getElementById("beds").value) },
        icu: { total: Number(document.getElementById("icu").value), available: Number(document.getElementById("icu").value) },
        doctors: { total: Number(document.getElementById("doctors").value), available: Number(document.getElementById("doctors").value) },
        nurses: { total: Number(document.getElementById("nurses").value), available: Number(document.getElementById("nurses").value) },
        operating_rooms: { total: Number(document.getElementById("operating_rooms").value), available: Number(document.getElementById("operating_rooms").value) }
    };
}

function renderResources(remaining) {
    const display = {
        beds: "🛏️ Beds",
        icu: "🚑 ICU",
        doctors: "👨‍⚕️ Doctors",
        nurses: "👩‍⚕️ Nurses",
        operating_rooms: "🏥 Operating Rooms"
    };

    document.getElementById("resourceCards").innerHTML = Object.entries(remaining).map(([key, value]) => `
        <div class="card">
            <h3>${display[key]}</h3>
            <strong>${value}</strong>
            <div>remaining after simulation</div>
        </div>
    `).join("");
}

function renderPatients(patients) {
    document.getElementById("patientTable").innerHTML = `
        <table>
            <thead><tr><th>Patient</th><th>Urgency</th><th>Waiting</th><th>Priority</th><th>Status</th><th>Reason</th></tr></thead>
            <tbody>
                ${patients.map(p => `
                    <tr>
                        <td>${p.id}</td>
                        <td>${p.urgency}</td>
                        <td>${p.waiting_time} min</td>
                        <td class="priority">${p.priority}</td>
                        <td class="${p.status === "Allocated" ? "allocated" : "waiting"}">${p.status}</td>
                        <td>${p.reason || ""}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;

    if (patients.length) {
        const p = patients[0];
        const urgencyValue = p.urgency === "High" ? 3 : p.urgency === "Medium" ? 2 : 1;
        document.getElementById("calculationExample").innerHTML =
            `<b>Example: ${p.id}</b><br>(${urgencyValue} × 10) + ${p.waiting_time} = <b>${p.priority}</b>`;
    }
}

function renderResults(result) {
    document.getElementById("results").innerHTML = `
        <div class="success">✅ ${result.message}</div>
        <div class="metric-grid">
            <div><strong>${result.metrics.total_patients}</strong><span>Total patients</span></div>
            <div><strong>${result.metrics.treated}</strong><span>Treated</span></div>
            <div><strong>${result.metrics.waiting}</strong><span>Waiting</span></div>
            <div><strong>${result.metrics.average_waiting} min</strong><span>Average waiting time</span></div>
        </div>
        <h3>Decision flow</h3>
        <p>Patients were sorted by priority, then MEDFLOW checked the required resources for each patient in that order.</p>
    `;
}

document.getElementById("addPatientBtn").addEventListener("click", () => addPatient());

document.getElementById("simulateBtn").addEventListener("click", async () => {
    const button = document.getElementById("simulateBtn");
    const patients = collectPatients();

    if (!patients.length) {
        document.getElementById("results").innerHTML = '<div class="error">Add at least one patient before running the simulation.</div>';
        return;
    }

    button.disabled = true;
    button.textContent = "Running...";

    try {
        const response = await fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ hospital: collectHospital(), patients })
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Simulation failed.");

        renderPatients(result.patients);
        renderResources(result.remaining);
        renderResults(result);
    } catch (error) {
        document.getElementById("results").innerHTML = `<div class="error">${error.message}</div>`;
    } finally {
        button.disabled = false;
        button.textContent = "▶ Run MEDFLOW Simulation";
    }
});

// Start with three easy-to-edit example patients.
defaultPatients.forEach(addPatient);

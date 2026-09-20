import streamlit as st
import pandas as pd
from simulation import new_state, tick, allocate_waiting, trigger_emergency_surge
from simulation import metrics

st.set_page_config(page_title="MEDFLOW", page_icon="🏥", layout="wide")

st.markdown("""
<style>
/* Overall page */
.stApp { background: linear-gradient(180deg, #dcecf2 0%, #cfe1e8 48%, #c5dbe3 100%); color: #102a43; }
.block-container {padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1500px;}
.main .block-container {background: transparent;}

/* Force readable text everywhere */
.stApp, .stApp p, .stApp span, .stApp label,
.stMarkdown, .stCaption, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
    color: #102a43 !important;
}

/* Sidebar text is scoped separately so the page-wide rule cannot make it unreadable. */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #f8fbff !important;
}

/* Header */
.hero {
    padding: 1.5rem 1.7rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #0b3558 0%, #176b87 55%, #2b8a78 100%);
    border: 0;
    margin-bottom: 1.1rem;
    box-shadow: 0 8px 24px rgba(16,42,67,.16);
}
.hero h1 { color: #ffffff !important; font-size: 2.35rem; margin: 0 0 .25rem 0; }
.hero p { color: #eaf6ff !important; margin: .25rem 0; }
.hero .small { color: #d7eef5 !important; }

/* Replace white-looking boxes with blue/grey cards */
.card {
    padding: 1rem 1.1rem;
    border-radius: 15px;
    border: 1px solid #c3d4e3;
    background: #dcebf4;
    color: #102a43 !important;
    margin-bottom: .7rem;
    box-shadow: 0 3px 10px rgba(16,42,67,.06);
}
.card b { color: #0b3558 !important; }
.card .small { color: #486581 !important; }

/* Metric boxes */
[data-testid="stMetric"] {
    background: #dcebf4;
    border: 1px solid #c3d4e3;
    border-radius: 14px;
    padding: .8rem;
    box-shadow: 0 3px 10px rgba(16,42,67,.06);
}
[data-testid="stMetricLabel"] { color: #486581 !important; }
[data-testid="stMetricValue"] { color: #0b3558 !important; }

/* Sidebar: clean dark-blue base + red/yellow/blue cards with high contrast */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071a33 0%, #0b2f55 52%, #092746 100%) !important;
    border-right: 4px solid #ef5350;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] b {
    color: #ffffff !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #f8fbff !important;
}
[data-testid="stSidebar"] .sidebar-title {
    color: #ffffff !important;
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: .65rem;
}

/* Info box */
[data-testid="stAlert"] { background: #d9edf2 !important; border: 1px solid #9bcbd5 !important; }

/* Tables */
[data-testid="stDataFrame"] {
    border: 1px solid #9dbac7;
    border-radius: 12px;
    overflow: hidden;
    background: #c9dfe7 !important;
}
[data-testid="stDataFrame"] * { color: #102a43 !important; }

.doctor-table { width:100%; border-collapse:separate; border-spacing:0; overflow:hidden; border-radius:14px; background:#c7dce4; border:1px solid #9dbac7; margin-bottom:1rem; }
.doctor-table th { background:#0b3558; color:#ffffff; padding:12px 16px; text-align:center; font-weight:700; }
.doctor-table th:first-child { text-align:left; }
.doctor-table td { color:#102a43; padding:11px 16px; border-top:1px solid #afc8d2; text-align:center; font-weight:600; }
.doctor-table td:first-child { text-align:left; font-weight:700; }
.doctor-table tr:nth-child(even) td { background:#d4e5eb; }

/* Buttons */
.stButton > button {
    background: #176b87 !important;
    color: #ffffff !important;
    border: 0 !important;
    border-radius: 10px !important;
    font-weight: 600;
}
.stButton > button:hover { background: #0b3558 !important; color: #ffffff !important; }

.small { color:#486581 !important; font-size:.9rem; }
.badge {display:inline-block; padding:.2rem .55rem; border-radius:999px; font-size:.78rem; font-weight:700; background:#c7e4ed; color:#0b3558 !important;}

/* Expander */
[data-testid="stExpander"] { background: #dcebf4; border: 1px solid #c3d4e3; border-radius: 14px; }

.formula-card { background:#123b63; border:1px solid #4f83b5; border-radius:12px; padding:12px; margin:9px 0; box-shadow:0 3px 10px rgba(0,0,0,.22); }
.formula-card.red { background:#7f1d1d; border-color:#ef5350; }
.formula-card.yellow { background:#6b4f00; border-color:#ffd54f; }
.formula-card.blue { background:#123b63; border-color:#64b5f6; }
.formula-title { color:#ffffff !important; font-weight:800; margin-bottom:6px; }
.formula { color:#ffffff !important; font-size:.88rem; line-height:1.55; font-weight:650; }
.formula-note { color:#fffde7 !important; font-size:.78rem; margin-top:5px; }
.sidebar-note {
    color:#ffffff !important;
    background:#0e4778;
    border:1px solid #64b5f6;
    border-radius:10px;
    padding:10px 12px;
    font-size:.78rem;
    line-height:1.45;
    margin-top:12px;
}
.sidebar-heading { color:#ffffff !important; }
.waiting-table { width:100%; border-collapse:separate; border-spacing:0; overflow:hidden; border-radius:13px; background:#fff7d6; border:1px solid #e3c65a; margin-bottom:1rem; }
.waiting-table th { background:#c62828; color:#ffffff; padding:10px 12px; text-align:center; font-weight:750; }
.waiting-table td { color:#172b4d; padding:9px 12px; border-top:1px solid #eadf9d; text-align:center; font-weight:600; }
.waiting-table td:first-child { font-weight:750; }
.waiting-table tr:nth-child(even) td { background:#fffbea; }
.treatment-table { width:100%; border-collapse:separate; border-spacing:0; overflow:hidden; border-radius:13px; background:#d4e7ec; border:1px solid #8fb7c2; margin-bottom:1rem; }
.treatment-table th { background:#176b87; color:#ffffff; padding:10px 12px; text-align:center; font-weight:750; }
.treatment-table td { color:#102a43; padding:9px 12px; border-top:1px solid #b4ced6; text-align:center; font-weight:600; }
.treatment-table td:first-child { font-weight:750; }
.treatment-table tr:nth-child(even) td { background:#c7dfe6; }
.completed-table { width:100%; border-collapse:separate; border-spacing:0; border-radius:13px; overflow:hidden; background:#dbe8df; border:1px solid #9bb8a5; }
.completed-table th { background:#397a5a; color:#ffffff; padding:10px 12px; text-align:center; }
.completed-table td { color:#173b29; padding:9px 12px; border-top:1px solid #b8cfbf; text-align:center; font-weight:600; }
.discharged-table { width:100%; border-collapse:separate; border-spacing:0; border-radius:13px; overflow:hidden; background:#e0eef5; border:1px solid #8fb7c2; }
.discharged-table th { background:#176b87; color:#ffffff; padding:10px 12px; text-align:center; }
.discharged-table td { color:#102a43; padding:9px 12px; border-top:1px solid #b4ced6; text-align:center; font-weight:600; }
.surge-table { width:100%; border-collapse:separate; border-spacing:0; border-radius:13px; overflow:hidden; background:#ffe6e6; border:1px solid #ef9a9a; }
.surge-table th { background:#b71c1c; color:#ffffff; padding:10px 12px; text-align:center; }
.surge-table td { color:#4a1616; padding:9px 12px; border-top:1px solid #efc2c2; text-align:center; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🏥 MEDFLOW</h1><p><b>Hospital Resource Management Simulator</b></p><p class="small">Emergency stabilization → specialist department → resource allocation → treatment → resource release</p></div>', unsafe_allow_html=True)
st.caption("Synthetic patient cases + configurable demo hospital capacity. No real patient records are used.")

if "state" not in st.session_state:
    st.session_state.state = new_state()
state = st.session_state.state
m = metrics(state)
r = state["resources"].status()

with st.sidebar:
    st.markdown('<div class="sidebar-title">🧮 MEDFLOW Formulas</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="formula-card red">
      <div class="formula-title">🔴 Priority score</div>
      <div class="formula">Priority = Urgency × 100 + Waiting Time</div>
      <div class="formula-note">Red = High = 3 &nbsp;|&nbsp; Yellow = Medium = 2 &nbsp;|&nbsp; Green = Low = 1</div>
    </div>
    <div class="formula-card yellow">
      <div class="formula-title">🟡 Resource checks</div>
      <div class="formula">Every patient → Doctor + Nurse</div>
      <div class="formula">ICU → ICU bed + General bed</div>
      <div class="formula">General bed → General bed</div>
      <div class="formula">Surgery → Operating room + General bed</div>
    </div>
    <div class="formula-card blue">
      <div class="formula-title">🔵 Routing</div>
      <div class="formula">Specialist available → Direct department</div>
      <div class="formula">Specialist full → Emergency → Department</div>
    </div>
    <div class="formula-card blue">
      <div class="formula-title">🔵 Simulation clock</div>
      <div class="formula">New patients arrive every 5 simulated minutes</div>
      <div class="formula">Remaining treatment = Treatment time − elapsed time</div>
    </div>
    <div class="formula-card red">
      <div class="formula-title">🔴 Serious patient pathway</div>
      <div class="formula">Serious patient → ICU → short recovery → General Bed</div>
      <div class="formula-note">After ICU treatment, the patient shifts to a General Bed for a short recovery period.</div>
    </div>
    <div class="sidebar-note">Simplified prototype scheduling rules — not clinical decision formulas.</div>
    """, unsafe_allow_html=True)

    if st.button("🚨 Trigger Emergency Surge", use_container_width=True):
        trigger_emergency_surge(state)
        st.rerun()
    if state.get("surge_active"):
        st.markdown("<div class='sidebar-note'><b>Emergency surge active:</b> overflow patients may be marked for transfer to another hospital.</div>", unsafe_allow_html=True)

st.info("Design basis: the hackathon asks MEDFLOW to represent patient urgency, maintain a queue, track resources, assign doctors/resources, prioritize urgent cases, prevent capacity conflicts, calculate utilization, and show an operations dashboard. Department routing and temporary Emergency stabilization are prototype design assumptions added to demonstrate a more realistic workflow.")

cols = st.columns(7)
cols[0].metric("Patients", m["total"])
cols[1].metric("Waiting", m["waiting"])
cols[2].metric("Emergency", m["emergency"])
cols[3].metric("Being Treated", m["treating"])
cols[4].metric("Completed", m["completed"])
cols[5].metric("Surge Transfers", m["surge_transfers"])
cols[6].metric("Sim. Time", f"{state['clock']} min")

st.markdown("## 👨‍⚕️ Doctor & Department Capacity")
st.caption("Staffing numbers below are synthetic demo values, chosen to create specialist bottlenecks without using real hospital staffing data.")
doctor_rows = state["resources"].doctor_status()
rows_html = "".join(
    f"<tr><td>{row['Department']}</td><td>{row['Total']}</td><td>{row['Available']}</td><td>{row['Busy']}</td></tr>"
    for row in doctor_rows
)
st.markdown(
    f"""<table class='doctor-table'><thead><tr><th>Department</th><th>Total Doctors</th><th>Available</th><th>Busy</th></tr></thead><tbody>{rows_html}</tbody></table>""",
    unsafe_allow_html=True
)

st.markdown("## 🏥 Hospital Resources")
a,b,c,d,e = st.columns(5)
a.metric("General Beds", f"{r['Beds']}/{state['resources'].total_beds}")
b.metric("ICU Beds", f"{r['ICU Beds']}/{state['resources'].total_icu}")
c.metric("Doctors Available", r["Doctors"])
d.metric("Nurses Available", r["Nurses"])
e.metric("Operating Rooms", f"{r['Operating Rooms']}/{state['resources'].total_or}")

# Live waiting queue with each patient's current simulated waiting time.
st.markdown("## ⏳ Waiting Patients")
st.caption("A patient waits only when the required doctor, nurse, ICU/bed, or operating room is unavailable. The table shows the exact reason, so available general beds do not hide another bottleneck.")
waiting_patients = [p for p in state["patients"] if p["status"] == "Waiting"]
if waiting_patients:
    waiting_rows = []
    for p in sorted(waiting_patients, key=lambda x: (-x.get("priority", 0), x.get("arrival_time", 0))):
        waiting_rows.append({
            "Patient": p["id"],
            "Condition": p["condition"],
            "Triage": p["triage"],
            "Department": p["department"],
            "Waiting Time (min)": p.get("waiting_minutes", 0),
            "Reason": p.get("waiting_reason", "Resource / specialist unavailable"),
            "Priority": p.get("priority", 0),
        })
    st.markdown(pd.DataFrame(waiting_rows).to_html(index=False, classes="waiting-table", border=0), unsafe_allow_html=True)
else:
    st.markdown("<div class='card'><span class='small'>No patients are currently waiting. Press Start / Allocate or advance the simulation to update the queue.</span></div>", unsafe_allow_html=True)

if state.get("surge_active"):
    st.markdown("## 🚨 Emergency Surge — External Hospital Transfers")
    st.warning("Emergency surge mode is active. The simulator has added a sudden wave of emergency patients. Patients who cannot be accepted because emergency capacity is exhausted are listed for transfer to another hospital.")
    transfer_patients = [p for p in state["patients"] if p.get("status") == "External Transfer Recommended"]
    if transfer_patients:
        transfer_rows = []
        for p in transfer_patients:
            transfer_rows.append({
                "Patient": p["id"],
                "Urgency": p["triage"],
                "Required Care": p.get("resource", ""),
                "Waiting / Capacity Issue": p.get("transfer_reason", "Emergency capacity exceeded"),
                "Transfer Status": "Shift to other hospital",
            })
        st.markdown(pd.DataFrame(transfer_rows).to_html(index=False, classes="surge-table", border=0), unsafe_allow_html=True)
    else:
        st.markdown("<div class='card'><span class='small'>No surge patient currently requires external transfer.</span></div>", unsafe_allow_html=True)

st.markdown("## 🚑 Patient Flow")
st.caption("Completed patients leave this live inflow view. New arrivals enter every 5 simulated minutes.")
active = [p for p in state["patients"] if p["status"] not in ("Not Arrived", "Completed")]
if active:
    for p in sorted(active, key=lambda x: (x.get("arrival_time", 0), -x.get("priority", 0))):
        status = p["status"]
        if status == "Emergency Stabilization":
            flow = f"🚨 {p.get('routing_message', 'Specialist unavailable')}"
        elif status == "Ready for Resource Allocation":
            flow = f"👨‍⚕️ {p['department']} → waiting for {p.get('resource','resource')}"
        elif status == "In Treatment":
            flow = f"🏥 {p['department']} → <b>IN TREATMENT</b> → {p.get('location','')}"
        elif status == "Post-ICU Recovery":
            flow = "🛏️ ICU treatment complete → <b>GENERAL BED</b> → recovery"
        else:
            flow = f"⏳ {status}"
        arrival = p.get("arrival_time", 0)
        st.markdown(f"<div class='card'><b>{p['id']}</b> &nbsp; <span class='badge'>{p['triage']}</span> &nbsp; <span class='badge'>{status}</span><br><b>{p['condition']}</b> → {p['department']}<br><span class='small'>Arrived at {arrival} min | {flow} | Priority: {p.get('priority',0)}</span></div>", unsafe_allow_html=True)
else:
    st.write("No active patients. Advance the simulation to bring in the next arrivals.")

st.markdown("## 👥 Patients Currently Being Treated")
current = [p for p in state["patients"] if p["status"] in ("In Treatment", "Post-ICU Recovery")]

def treatment_table(title, patients):
    st.markdown(f"### {title}")
    if not patients:
        st.markdown("<div class='card'><span class='small'>No patient currently in treatment in this department.</span></div>", unsafe_allow_html=True)
        return
    rows=[]
    for p in patients:
        rows.append({"Patient":p["id"],"Condition":p["condition"],"Doctor":p.get("assigned_doctor",""),"Location":p.get("location",""),"Remaining (min)":max(0,p.get("remaining_minutes",0))})
    df=pd.DataFrame(rows)
    html=df.to_html(index=False, classes="treatment-table", border=0)
    st.markdown(html, unsafe_allow_html=True)

treatment_table("❤️ Cardiology", [p for p in current if p["department"] == "Cardiology"])
treatment_table("🧠 Neurology", [p for p in current if p["department"] == "Neurology"])
treatment_table("🦴 Orthopedics", [p for p in current if p["department"] == "Orthopedics"])
treatment_table("🏥 General / Other Departments", [p for p in current if p["department"] not in ("Cardiology", "Neurology", "Orthopedics")])
post_icu = [p for p in current if p["status"] == "Post-ICU Recovery"]
if post_icu:
    treatment_table("🛏️ Post-ICU Recovery — General Bed", post_icu)

st.markdown("## 🏆 Completed Operations")
completed_ops = [p for p in state["patients"] if p["status"] == "Completed" and p.get("resource") == "Surgery"]
if completed_ops:
    rows=[]
    for p in completed_ops:
        rows.append({"Patient":p["id"],"Department":p["department"],"Operation":p["condition"],"Doctor":p.get("assigned_doctor","") ,"Completed at (min)":p.get("end_time","")})
    st.markdown(pd.DataFrame(rows).to_html(index=False, classes="completed-table", border=0), unsafe_allow_html=True)
else:
    st.markdown("<div class='card'><span class='small'>No operations completed yet.</span></div>", unsafe_allow_html=True)

st.markdown("## 🏠 Discharged After Treatment — No Operation")
discharged = [p for p in state["patients"] if p["status"] == "Completed" and p.get("resource") != "Surgery"]
if discharged:
    rows=[]
    for p in discharged:
        rows.append({"Patient":p["id"],"Department":p["department"],"Treatment":p["condition"],"Care Type": "ICU + recovery" if p.get("resource") == "ICU" else "General treatment", "Discharged at (min)":p.get("end_time","")})
    st.markdown(pd.DataFrame(rows).to_html(index=False, classes="discharged-table", border=0), unsafe_allow_html=True)
else:
    st.markdown("<div class='card'><span class='small'>No non-operative patients have been discharged yet.</span></div>", unsafe_allow_html=True)

st.markdown("## ⚙️ Simulation Controls")
a,b,c = st.columns(3)
if a.button("▶ Start / Allocate", use_container_width=True):
    allocate_waiting(state); st.rerun()
if b.button("⏱️ Advance 5 Minutes", use_container_width=True):
    tick(state,5); st.rerun()
if c.button("🔄 Reset", use_container_width=True):
    st.session_state.state = new_state(); st.rerun()

with st.expander("📌 Why does MEDFLOW work this way?", expanded=False):
    st.markdown("""
**1. Triage / priority:** Red, Yellow and Green map to High, Medium and Low urgency. MEDFLOW uses the integrated priority model: `Priority = (Urgency × 100) + Waiting Time`.

**2. Specialist-first routing:** If the required specialist is available when the patient arrives, MEDFLOW sends the patient directly to that department. This avoids an unnecessary Emergency step.

**3. Emergency fallback:** If the required specialist is currently unavailable, the patient is assigned to Emergency for temporary stabilization. When the specialist becomes available, MEDFLOW transfers the patient to the correct department. This is a prototype workflow assumption, not a clinical protocol.

**4. Resource allocation:** After specialist assignment, MEDFLOW checks beds/ICU/OT and nurses. A patient cannot consume a resource that is already at capacity.

**5. Release:** When treatment ends, the specialist, nurse and facility resources are released so another patient can use them.

**6. Staffing numbers:** The department doctor counts are intentionally synthetic demo capacities. They are not presented as actual staffing levels of any hospital.

**7. Department mapping:** Conditions such as heart-related cases → Cardiology and fractures → Orthopedics are simplified prototype mappings. In a real hospital, clinical staff determine the appropriate specialty and treatment pathway.
""")

st.markdown("### 📚 Source / scope note")
st.write("The hackathon brochure supplies the core MEDFLOW requirements. Published hospital figures can be used as reference context, but the individual patient cases and the department staffing numbers in this demo are synthetic.")

# 01. Master Runbook for BhoomiSakha Live Demo

> **Target Audience:** Pitch Presenters, Demo Operators, SIH Judges  
> **System Name:** BhoomiSakha / BhommiFlow  
> **Problem Statement:** SIH 26017 – Predictive Analytics System for Early Detection of Land Acquisition Delays  
> **Verification Status:** ALL 68 APIs, D1–D5 Datasets, ML Inference, RAG, Security & UX **VERIFIED PASS**

---

## Pre-Demo Preparation & Environment Check

Before beginning the live demonstration, complete this 10-point health check:

### 1. Machine & Runtime Environment
- **Operating System:** Windows 10/11 or Linux
- **Python Version:** 3.10+ installed and active
- **Node.js Version:** 18+ / npm installed
- **Terminal Access:** 2 open terminal windows (Backend + Frontend)

### 2. Service Verification Commands

#### Backend Health Check
```powershell
# In root workspace directory:
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```
*Expected Output:* `{"status": "healthy", "service": "BhoomiSakha API"}`

#### Frontend Health Check
- Open Browser to: `http://localhost:5173` (or `http://localhost:3000`)
- Confirm login page renders cleanly without console errors.

#### D5 Model Artifact Check
- Confirm `backend/app/ml/delay-model-calibrated.joblib` exists (Size: ~104 KB).

#### Demo Document Pack Check
- Confirm files are present in `docs/SOP/demo_pack/mock_documents/`:
  - `01_land_record.pdf`
  - `02_ownership_record.pdf`
  - `03_applicant_document.pdf`
  - `04_acquisition_notice.pdf`
  - `05_compensation_record.pdf`
  - `06_conflicting_record.pdf`

---

## Step-by-Step Live Demo Execution

| Step | Time | Action | Visual Target | What to Explain / Key Pitch Point |
| :--- | :--- | :--- | :--- | :--- |
| **01** | `0:00 - 0:30` | **Opening & Problem** | Pitch Slide / Main Landing | "Land acquisition in India faces chronic 180+ day delays. BhoomiSakha transforms fragmented land evidence into predictive delay intelligence." |
| **02** | `0:30 - 1:00` | **Language Selection** | Top-Right Navbar Toggle | "We support English, Hindi (हिंदी), and Marathi (मराठी). Citizens and officers interact in their native language seamlessly." Switch to Hindi then Marathi. |
| **03** | `1:00 - 1:30` | **Citizen Case Intake** | Citizen Portal -> New Case | Submit deterministic case: Land Parcel Survey No `104/A`, Sub-division `2`, Village `Besa`, Taluka `Nagpur Rural`, District `Nagpur`. |
| **04** | `1:30 - 2:00` | **Document Upload** | Citizen Upload Workspace | Upload `01_land_record.pdf` and `02_ownership_record.pdf`. Emphasize browser-native drag-and-drop. |
| **05** | `2:00 - 2:30` | **Evidence Extraction** | Document Details Modal | "System automatically computes SHA-256 hash, extracts structured landholder attributes, and registers immutable provenance." |
| **06** | `2:30 - 3:00` | **Multilingual Guidance & TTS** | "What does this step mean?" Card | Click **Listen / सुनें / ऐका**. Sarvam AI / Browser speech synthesis plays audio explanation of land record verification. |
| **07** | `3:00 - 3:30` | **Officer Switching** | Officer Dashboard | Switch to Revenue Officer perspective. View Project Dashboard: `Nagpur Bypass Link` (ID: `PROJ-FC0ACD7D132F`). |
| **08** | `3:30 - 4:00` | **Graph & Bottlenecks** | Intelligence Graph View | View graph nodes (Parcel -> Case -> Owner -> Document). Highlight active bottleneck node at Section 15 Objection stage. |
| **09** | `4:00 - 4:30` | **D5 Delay Prediction** | Delay Risk Panel | View real ML inference probability: e.g. **68.4% Delay Risk within 180 days**. *(Note: Explain that 68.4% is calibrated probability, not binary fake accuracy)*. |
| **10** | `4:30 - 5:00` | **Explainability & SHAP** | "Why is this project at risk?" | Show top risk factors: `Objection Count = 4`, `Disputed Parcel Area = 1.45 Ha`, `Stage Duration = 120 Days`. |
| **11** | `5:00 - 5:30` | **D3 Conflict Detection** | Evidence Workspace | Upload `06_conflicting_record.pdf`. D3 engine highlights name mismatch: `Rajesh Kumar Patil` vs `Rajesh K. Patil`. |
| **12** | `5:30 - 6:00` | **D4 Procedure RAG** | Decision Support Panel | Officer queries: *"How to resolve Section 15 name spelling variation?"* D4 RAG returns exact clause from RFCTLARR SOP with citations. |
| **13** | `6:00 - 6:30` | **Intervention & Decision** | Officer Action Form | System recommends: *"Initiate Joint Tahsildar Field Verification"*. Officer selects **ACCEPT** & submits decision. |
| **14** | `6:30 - 7:00` | **Notification Simulation** | SMS / WhatsApp Terminal | View real-time simulated push sequence: SMS (`QUEUED` -> `SENT` -> `DELIVERED`), WhatsApp (`QUEUED` -> `SENT` -> `DELIVERED` -> `READ`). |
| **15** | `7:00 - 7:30` | **Audit & Closing** | Case Audit Log | Point out append-only cryptographic audit record. "Complete loop closed: Evidence -> Prediction -> Intervention -> Action -> Citizen Alert -> Audit." |

---

## Backup Plan & Emergency Recovery

- **If API drops:** Run `python -m uvicorn app.main:app --reload` from `backend/`.
- **If TTS has no audio output:** Ensure system volume is up; browser falls back to native Web Speech API automatically.
- **If offline without internet:** Model inference & local SQLite/PostgreSQL RAG work 100% offline.

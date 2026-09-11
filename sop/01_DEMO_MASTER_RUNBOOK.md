# 01. Demo Master Runbook

This document details the exact click-by-click navigation and live demonstration flow for the SIH evaluation.

## 11-Screen Navigation Map

### Screen 1: Citizen Case Intake
* **Action**: Open `/citizens/cases/new`. Enter land acquisition details and select demo parcel `100/B`.
* **Narration**: *"Instead of treating a land case as a single form, BhoomiSakha structures the case together with its evidence and timeline."*

### Screen 2: Evidence Submission & Extraction
* **Action**: Navigate to `Case Documents` tab. Upload `712_wagholi.pdf`. Click `Extract & Index`.
* **Narration**: *"D2 processes raw land records into structured OCR fields while preserving full document provenance."*

### Screen 3: Project Evidence Graph
* **Action**: Open `/projects/PRJ-TEST-INTEG-001/evidence`. View linked documents, parcel boundaries, and claimant nodes.
* **Narration**: *"BhoomiSakha connects fragmented evidence across documents, parcels, and authorities."*

### Screen 4: Officer Intelligence Dashboard
* **Action**: Log in as Officer. Navigate to `/dashboard`. View project `PRJ-TEST-INTEG-001`.
* **Display**:
  * **Predicted Risk Level**: `High` (Probability: `72.4%`)
  * **Primary Bottleneck**: `Section 15 Objections Pending`
* **Narration**: *"D5 calibrated machine learning model evaluates live project features to predict delay probability without target leakage."*

### Screen 5: Explanation - "Why Is This Project At Risk?"
* **Action**: Click `View Risk Explanation`.
* **Display**: Contributing factors:
  1. High count of unresolved landholder objections (Supporting Evidence: Case #BH-2026-00124)
  2. OCR Mismatch in 7/12 Extract vs Sale Deed (Supporting Evidence: Doc #D2-9842)
* **Narration**: *"Predictive risk is explained through evidence-backed contributing factors rather than opaque black-box claims."*

### Screen 6: Conflict Analysis
* **Action**: Open `Document Mismatches` tab. View D3 comparison record `COMP-001`.
* **Display**: Document A (`Sale Deed`: Area 50.0 Ha) vs Document B (`7/12 Extract`: Area 42.5 Ha). Severity: `HIGH`.
* **Narration**: *"BhoomiSakha distinguishes representation-only differences from legal conflicts requiring officer intervention."*

### Screen 7: Procedure RAG Guidance
* **Action**: Click `Procedure Guidance`.
* **Display**: Section 15 RFCTLARR Act 2013 procedure chunk `D4:PROC-012`. Department: `Revenue Department`. Status: `VERIFIED`.
* **Narration**: *"Procedure RAG retrieves exact government rules with source provenance to guide officer action."*

### Screen 8: Recommended Intervention
* **Action**: View `Intervention Recommendations`.
* **Display**:
  * **Action**: Issue Hearing Notice for Landholder Objections
  * **Priority**: `HIGH`
  * **Expected Effect**: Reduces projected delay by 45 days
* **Narration**: *"Intervention engine combines prediction, evidence, and procedure to recommend actionable steps."*

### Screen 9: Officer Decision (Human-in-the-loop)
* **Action**: Select action `Issue Hearing Notice`. Click `ACCEPT & INITIATE ACTION`.
* **State Transition**: `RECOMMENDED` → `REVIEWED` → `ACCEPTED` → `ACTION_INITIATED`.
* **Narration**: *"The AI system recommends options, but the officer retains full decision authority."*

### Screen 10: Realtime Notification Simulation
* **Action**: Observe realtime UI status update on action initiation.
* **Display**:
  * **SMS**: `QUEUED` → `SENT` → `DELIVERED` (`SIM-SMS-20260912-A819F`)
  * **WhatsApp**: `QUEUED` → `SENT` → `DELIVERED` → `READ` (`SIM-WA-20260912-B9201`)
* **Badge**: `[DEMO SIMULATION]`
* **Narration**: *"We use a provider-independent realtime simulation to demonstrate notification workflows without external API dependencies."*

### Screen 11: Immutable Audit Trail
* **Action**: Navigate to `Project Audit Log`. View record `AUDIT-9901`.
* **Display**: Actor `Officer (usr-officer-intv)`, Action `ACCEPTED_INTERVENTION`, Timestamp, Outcome.
* **Narration**: *"Every decision and notification event creates an immutable audit record for full accountability."*

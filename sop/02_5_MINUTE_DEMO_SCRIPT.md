# 02. 5-Minute Demo Script

## Timeline & Word-for-Word Pitch

### 0:00 - 0:30 | The Problem
"Good morning judges. Infrastructure and linear land acquisition projects across India face severe time and cost overruns. The root cause is not a single missing form — it is fragmented evidence scattered across paper land records, court cases, conflicting survey numbers, and departmental silos. By the time a delay is noticed, months have already been lost."

### 0:30 - 1:00 | Citizen Intake & Evidence Structuring
"BhoomiSakha changes this by unifying evidence at the point of intake. Here, a citizen submits Case #BH-2026-00124 for the Ahmednagar Highway expansion. As documents like 7/12 extracts and sale deeds are uploaded, our Evidence Intelligence service parses OCR text and links parcel 100/B to canonical database entities, preserving full data provenance."

### 1:00 - 1:40 | Evidence RAG & Mismatch Detection
"Our Evidence RAG indexes Dataset 1 case context, Dataset 2 document extractions, and Dataset 3 comparison records. In the Document Mismatch viewer, BhoomiSakha automatically detects a conflict: the Sale Deed claims 50 Hectares while the 7/12 Extract lists 42.5 Hectares. Representation-only typos are filtered out, highlighting true legal risks for officer review."

### 1:40 - 2:20 | D5 Machine Learning Delay Prediction
"On the Officer Dashboard, our calibrated Scikit-Learn model — trained on Dataset 5 — evaluates non-leaking point-in-time project features. It predicts a 72.4% delay probability for Project PRJ-TEST-INTEG-001, assigning a HIGH Risk Level and identifying 'Section 15 Objections' as the primary bottleneck."

### 2:20 - 3:00 | Evidence-Backed Risk Explanation
"Why is this project at risk? Clicking 'Why Risky?' reveals structured contributing factors. Rather than producing black-box claims, BhoomiSakha explicitly links each risk factor to verifiable evidence items: pending objections from 15 landholders and unresolved document mismatches."

### 3:00 - 3:40 | D4 Procedure RAG & Actionable Intervention
"Prediction alone is not enough. BhoomiSakha queries Dataset 4 Procedure RAG to retrieve exact government regulations from the RFCTLARR Act 2013. Grounded in this procedure, the system generates a prioritized intervention: 'Issue Hearing Notice for Landholder Objections'."

### 3:40 - 4:20 | Officer Decision (Human-in-the-Loop)
"Crucially, AI does not make executive decisions. The officer reviews the recommendation, supporting evidence, and expected delay reduction of 45 days, and clicks 'ACCEPT & INITIATE ACTION'. The system transitions the decision state from RECOMMENDED to ACTION_INITIATED."

### 4:20 - 4:45 | Realtime Notification Simulation
"Initiating action instantly triggers our provider-independent realtime notification simulation. As visible on screen, SMS status moves from QUEUED to SENT to DELIVERED, and WhatsApp progresses to READ status with full delivery timestamps."

### 4:45 - 5:00 | Audit & Closing Statement
"Finally, every decision, action, and notification is recorded in an immutable audit trail. BhoomiSakha turns fragmented land records into early delay predictions, grounded procedural guidance, and auditable officer decisions. Thank you."

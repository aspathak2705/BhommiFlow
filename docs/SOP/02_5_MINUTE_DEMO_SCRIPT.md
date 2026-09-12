# 02. 5-Minute Judge Demo Script

> **Target Audience:** Pitch Lead / Live Presenter  
> **Duration:** Exactly 5 Minutes (300 Seconds)  
> **Tone:** Professional, Authoritative, Evidence-Backed

---

## Script Flow & Verbal Cue Sheet

```
[0:00 - 0:30] PROBLEM STATEMENT
"Respected Judges, infrastructure projects across India face average delays of 2 to 5 years, with 70% of delays caused by land acquisition bottlenecks. The current system is purely reactive — officers find out about bottlenecks after deadlines pass. Today we present BhoomiSakha: an early delay intelligence and evidence-backed decision system."

[0:30 - 1:15] CITIZEN INTAKE & MULTILINGUAL TTS
"We begin on the Citizen Portal. A landholder in Besa village, Nagpur submits their case for Project PROJ-FC0ACD7D132F. Notice our multilingual support in English, Hindi, and Marathi. When a citizen clicks 'What does this step mean?', our system provides context-aware guidance and plays audio using Sarvam AI speech synthesis. Let's listen."
(Trigger TTS Audio -> 5 seconds playback)

[1:15 - 2:00] EVIDENCE EXTRACTION & DISCREPANCY DETECTION (D1, D2, D3)
"The citizen uploads their 7/12 Land Record and Title Deed. On ingestion, BhoomiSakha automatically extracts key survey metadata, hashes the document for SHA-256 integrity, and runs D3 cross-record comparison. Here, it flags a name spelling discrepancy between 'Rajesh Kumar Patil' and 'Rajesh K. Patil', preventing a silent title defect from stalling the project months down the road."

[2:00 - 3:00] D5 PREDICTIVE DELAY ANALYTICS & SHAP EXPLAINABILITY
"Now let's switch to the Revenue Officer's cockpit. BhoomiSakha aggregates all project parcels into an Intelligence Graph. Our D5 Machine Learning model — trained on 10,000 acquisition projects — performs real-time inference. For this project, it predicts a 68.4% probability of delay within 180 days. Crucially, this is NOT a black box. Our SHAP explainability engine reveals why: the top driver is 4 unresolved Section 15 objections and disputed parcel area."

[3:00 - 4:00] D4 PROCEDURAL RAG & DECISION RECOMMENDATION
"Instead of forcing the officer to search through hundreds of pages of legal SOPs, our D4 Procedural RAG system indexes the RFCTLARR Act 2013. The officer asks how to resolve the title discrepancy, and BhoomiSakha provides exact legal step-by-step guidance with direct citations. The system then recommends a specific targeted intervention: 'Initiate Joint Tahsildar Field Verification'."

[4:00 - 5:00] ACTION, NOTIFICATION SIMULATION & AUDIT TRAIL
"The officer accepts the intervention with one click. Immediately, our provider-independent notification engine simulates push delivery to the citizen: SMS transitions from QUEUED to SENT to DELIVERED, and WhatsApp to READ. Every single interaction — from upload to ML prediction and officer decision — is signed and stored in an append-only audit trail. BhoomiSakha closes the loop from raw evidence to early delay intelligence and verifiable officer action. Thank you!"
```

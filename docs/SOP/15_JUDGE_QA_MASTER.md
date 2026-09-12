# 15. SIH 2026 Judge Q&A Master Handbook

## Frequently Asked Questions & Expert Answers

### Q1: Why not rely purely on LLM / Generative AI for land acquisition analysis?
**Answer:** LLMs are prone to legal hallucinations, lack spatial/temporal awareness, and cannot perform mathematical risk calibration. BhoomiSakha uses a hybrid architecture: Scikit-Learn ML for quantitative delay prediction (D5), ChromaDB RAG for grounded legal procedure retrieval (D4), and deterministic cross-record rules for document conflict detection (D3). LLMs are only used for text formatting and grounded RAG synthesis.

### Q2: What is the difference between RAG and ML in your system?
**Answer:** 
- **D1, D2, D3, D4 RAG:** Information retrieval and semantic matching over legal SOPs, case histories, and uploaded document text.
- **D5 ML Model:** Quantitative regression/classification model trained on 10,000 baseline projects predicting the probability (`0.0` to `1.0`) of project completion exceeding statutory timelines by 180+ days. D5 is **NOT RAG**.

### Q3: How do you handle spelling variations in Indian names across multi-generational records?
**Answer:** Our D3 Cross-Record Comparison Engine utilizes Levenshtein distance and Phonetic matching algorithms specifically tuned for Indian naming conventions (e.g. matching "Rajesh Kumar Patil" with "Rajesh K. Patil"). When a discrepancy threshold is breached, a `ConflictSignal` is generated for officer review.

### Q4: Does your system integrate real SMS and WhatsApp APIs?
**Answer:** BhoomiSakha includes a provider-independent simulation layer that models exact provider state machines (`QUEUED` -> `SENT` -> `DELIVERED` -> `READ`). For production deployment, the backend contract implements standard Twilio / WhatsApp Business Cloud API adapters.

### Q5: How do you guarantee privacy and security between different projects?
**Answer:** We enforce strict Object-Level Authorization (RBAC) and Row-Level Security in FastAPI endpoints. Citizens can only query documents matching their authenticated user ID, and Revenue Officers can only inspect projects assigned to their designated administrative jurisdiction.

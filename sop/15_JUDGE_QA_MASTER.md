# 15. Judge Q&A Master

## 40 Master Defensible Q&A Answers

### Core System & Architecture
1. **What is BhoomiSakha?**
   * *Answer*: BhoomiSakha is a predictive land acquisition intelligence and decision support system designed to detect project overruns early, ground interventions in government procedures, and support officer workflows.
2. **Why is this not just a chatbot?**
   * *Answer*: It is an end-to-end decision intelligence platform combining relational evidence graphs, machine learning delay predictions, procedural grounding, human-in-the-loop governance, and auditable action workflows.
3. **Why RAG?**
   * *Answer*: RAG allows retrieval of multi-source document evidence (D1-D3) and legal regulations (D4) with verifiable source provenance and zero hallucination of official rules.
4. **Why not just use an LLM for prediction?**
   * *Answer*: LLMs are non-deterministic and prone to hallucination. Delay risk prediction requires structured point-in-time features evaluated by a calibrated machine learning pipeline (Dataset 5).
5. **How does D1 contribute?**
   * *Answer*: D1 provides structured land acquisition case records, parcel details, and historical dispute context.
6. **How does D2 contribute?**
   * *Answer*: D2 provides extracted document metadata, OCR text, and evidence field validation.
7. **How does D3 contribute?**
   * *Answer*: D3 provides document comparison records to identify discrepancies between 7/12 extracts, sale deeds, and survey notices.
8. **Why is D4 separate?**
   * *Answer*: D4 contains government regulations and procedural rules (Procedure RAG), kept isolated from case evidence to ensure accurate legal grounding.
9. **Why is D5 separate?**
   * *Answer*: D5 is a dedicated ML dataset and calibrated model artifact used exclusively for statistical delay probability prediction. D5 is NOT RAG.
10. **How does prediction work?**
    * *Answer*: Non-leaking project features pass through a Scikit-Learn `ColumnTransformer` and a `CalibratedClassifierCV` model to output a delay probability (0.0 to 1.0) and risk level.

### Leakage, Security & Isolation
11. **How do you prevent data leakage in prediction?**
    * *Answer*: Future outcome fields (e.g., `future_delay`, `delay_days`) are strictly excluded from input feature schemas.
12. **How do you prevent cross-project RAG leakage?**
    * *Answer*: All vector searches apply SQL-level `WHERE project_id = :project_id` metadata filters, ensuring complete case isolation.
13. **Who makes the final decision?**
    * *Answer*: The nodal officer retains 100% decision authority. AI provides recommendations; officers execute `ACCEPT`, `REJECT`, or `DEFER`.
14. **How are notifications handled?**
    * *Answer*: The prototype uses a provider-independent realtime simulation generating formatted SMS and WhatsApp status transitions marked `[DEMO SIMULATION]`.
15. **What is your model performance?**
    * *Answer*: On held-out Dataset 5 test data, the calibrated model achieves an ROC-AUC of `0.6905` and a Brier Score of `0.2223`.

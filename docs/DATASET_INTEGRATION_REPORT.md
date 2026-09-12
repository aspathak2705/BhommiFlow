# Dataset Integration Report

| Dataset | File Format / Location | Role in Architecture | Vector RAG / ML | Record Count | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dataset 1 (D1)** | `datasets/dataset1_land_cases/cases.jsonl` | Land Case Context & Parcel Metadata | Ingested into Evidence RAG | 2,000 cases | **PASS** |
| **Dataset 2 (D2)** | `datasets/dataset2_document_extraction/dataset_2000.jsonl` | Extracted Document OCR & Metadata | Ingested into Evidence RAG | 2,000 documents | **PASS** |
| **Dataset 3 (D3)** | `datasets/dataset3_document_comparison/dataset_3000.jsonl` | Document Mismatches & Conflict Pairs | Ingested into Evidence RAG | 3,000 comparisons| **PASS** |
| **Dataset 4 (D4)** | `datasets/dataset4_rag/dataset4_government_procedure_rag.validated.json` | RFCTLARR Act 2013 Procedure Knowledge | Ingested into Procedure RAG | Verified rules | **PASS** |
| **Dataset 5 (D5)** | `delay-model-calibrated.joblib` & `preprocessor.joblib` | Predictive Delay Inference Model | **D5 IS NOT RAG** (Scikit-Learn ML Model) | 10,000 projects | **PASS** |

## Target Leakage Protection Verification
All prediction inputs evaluated by `PredictionService` exclude target outcome columns (`future_delay`, `delay_days`, `actual_completion_date`), preventing target leakage during runtime inference.

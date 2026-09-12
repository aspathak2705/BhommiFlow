# 05. End-to-End Data Flow Architecture

```
[D1 Case Data] ------> Ingestion Pipeline ──┐
                                          ├──> [Evidence RAG & Knowledge Index]
[D2 Document Data] --> OCR / Metadata  ───┤                │
                                          │                ▼
[D3 Comparison Data] -> Conflict Engine ──┘      [Feature Extraction Engine]
                                                           │
                                                           ▼
                                               [D5 ML Delay Prediction]
                                               (Risk % + SHAP Drivers)
                                                           │
                                                           ▼
                                               [D4 Procedure RAG (RFCTLARR)]
                                                           │
                                                           ▼
                                               [Officer Intervention System]
                                                           │
                                                           ▼
                                               [Notification Simulation]
                                               (SMS / WhatsApp Delivery)
                                                           │
                                                           ▼
                                               [Cryptographic Audit Trail]
```

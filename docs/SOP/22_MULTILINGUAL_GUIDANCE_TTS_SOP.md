# 22. Multilingual Support, Contextual Guidance & Speech Synthesis SOP

## 1. Supported Languages

BhoomiSakha supports three native languages across both Citizen and Officer portals:
- **English (EN)** - Default administrative language.
- **Hindi (HI / हिंदी)** - Primary national localized view.
- **Marathi (MR / मराठी)** - Regional state localized view (Maharashtra jurisdiction).

Language preference is persisted via browser local storage (`i18nextLng`) and passed in request headers.

---

## 2. Contextual Workflow Guidance

At every step of the land acquisition intake and verification process, users are provided with a **"What does this step mean?"** guidance card.

| Guidance Category | Target Audience | Content Provided |
| :--- | :--- | :--- |
| **Citizen Guidance** | Citizens | Plain-language explanation of required land documents, 7/12 extract significance, and next verification steps. |
| **Evidence Guidance** | Citizens & Officers | Details on extracted survey numbers, owner name variations, and document hashing integrity. |
| **Conflict Guidance** | Officers | Explanation of flagged title discrepancies (e.g. spelling variations) and required field resolution SOPs. |
| **Prediction Guidance**| Officers | Clear interpretation of D5 calibrated delay risk percentage and SHAP risk drivers. |
| **Intervention Guidance**| Officers | Step-by-step recommendation for mitigating identified bottlenecks (e.g. Joint Tahsildar Field Verification). |

---

## 3. Text-to-Speech (TTS) Architecture

```
User Clicks "Listen" / "सुनें" / "ऐका"
                 │
                 ▼
     Is Sarvam API Key Present?
        ├── YES ──> Call Sarvam AI REST API (bulbul:v3 model) ──> Play MP3 Audio Stream
        └── NO  ──> Fallback to Web Speech API (window.speechSynthesis) ──> Browser Speech Output
```

- **Primary Engine:** Sarvam AI REST API (`https://api.sarvam.ai`, Model `bulbul:v3`).
- **Offline / Zero-Config Fallback:** Native Web Speech API (`window.speechSynthesis`), ensuring audio guidance plays even when offline or without API credits.
- **Supported Audio Languages:** English, Hindi, and Marathi.

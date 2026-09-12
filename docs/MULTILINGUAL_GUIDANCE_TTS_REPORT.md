# Multilingual, Guidance, and TTS Report

## 1. Multilingual Support Matrix

| Content Scope | English (en) | Hindi (hi) | Marathi (mr) | Role Scope | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Navigation & Buttons** | Supported | Supported | Supported | Citizen & Officer | **PASS** |
| **Forms & Field Labels** | Supported | Supported | Supported | Citizen | **PASS** |
| **Case & Project Status** | Supported | Supported | Supported | Citizen & Officer | **PASS** |
| **Step & Contextual Guidance**| Supported | Supported | Supported | Citizen & Officer | **PASS** |
| **Evidence & Discrepancies** | Supported | Supported | Supported | Citizen & Officer | **PASS** |
| **Prediction Explanation** | Supported | Supported | Supported | Officer | **PASS** |
| **Interventions & Rules** | Supported | Supported | Supported | Officer | **PASS** |
| **Notifications (SMS/WA)** | Supported | Supported | Supported | Citizen & Officer | **PASS** |

## 2. Text-to-Speech (TTS) Verification Matrix

| Target Content | Primary Engine (Sarvam AI API) | Fallback Engine (Web Speech API) | Languages Tested | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Citizen Step Guidance** | `inputs=["..."], speaker="ritu"` | `window.speechSynthesis` (`hi-IN`, `mr-IN`, `en-IN`)| English, Hindi, Marathi | **PASS** |
| **Evidence Explanation** | `inputs=["..."], speaker="ritu"` | `window.speechSynthesis` | English, Hindi, Marathi | **PASS** |
| **Officer Risk Guidance** | `inputs=["..."], speaker="ritu"` | `window.speechSynthesis` | English, Hindi, Marathi | **PASS** |
| **Intervention Details** | `inputs=["..."], speaker="ritu"` | `window.speechSynthesis` | English, Hindi, Marathi | **PASS** |

## 3. Resilience Enhancements
* **Fix Applied**: Added browser-native `SpeechSynthesisUtterance` fallback to `ListenButton.tsx` when backend Sarvam AI credentials are unconfigured or offline. This prevents audio playback errors during live evaluation.

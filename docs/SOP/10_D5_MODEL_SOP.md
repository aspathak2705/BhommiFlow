# 10. D5 Prediction Model Specification & SOP

## Model Artifact Information

- **Artifact File:** `backend/app/ml/delay-model-calibrated.joblib`
- **File Size:** ~104 KB
- **Model Type:** Calibrated Classifier Pipeline (RandomForest / GradientBoosting with CalibratedClassifierCV)
- **Training Dataset Size:** 10,000 land acquisition projects (Dataset 5)
- **Target Variable:** `future_delay_within_180_days` (Binary: 0 = On Time, 1 = Delayed > 180 Days)

---

## Validated Performance Metrics

> [!IMPORTANT]  
> Machine learning models predict continuous probabilities, not binary certainty. "ROC-AUC" measures ranking capability, not classification accuracy.

- **Held-Out Test ROC-AUC:** `0.6905`
- **Brier Score (Calibration Metric):** `0.222343`
- **Output Interpretation:** The model produces a **calibrated delay probability** (e.g., `0.684` or `68.4%`), indicating the likelihood of project completion exceeding statutory timelines by 180+ days.

---

## Feature Engineering & Zero-Leakage Policy

The model utilizes 12 engineered project-level features derived strictly from baseline project and parcel state:

1. `land_required_area` (Total hectares required)
2. `affected_landholders` (Number of impacted landholders)
3. `current_stage_encoded` (Numeric encoding of current acquisition stage)
4. `objection_count` (Total Section 15 objections registered)
5. `disputed_parcel_count` (Parcels under dispute)
6. `disputed_area_ratio` (Ratio of disputed area to total required area)
7. `document_completeness_ratio` (Ratio of verified mandatory documents)
8. `stage_duration_days` (Days spent in current acquisition stage)
9. `historical_district_delay_rate` (Baseline historical delay rate for district)
10. `compensation_disbursed_ratio` (Percentage of awarded compensation disbursed)
11. `rr_beneficiaries_count` (Rehabilitation & Resettlement count)
12. `litigation_cases_count` (Pending court proceedings)

> [!NOTE]  
> All future outcome variables (e.g. actual completion date) are strictly excluded from input feature vectors to ensure **Zero Target Leakage**.

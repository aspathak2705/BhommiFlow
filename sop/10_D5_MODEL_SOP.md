# 10. D5 Model SOP

## Dataset 5 Machine Learning Model Specifications

### Overview
Dataset 5 contains historical project characteristics and delay outcomes. **D5 is NOT RAG.** It is loaded directly into `DelayPredictionService` to provide calibrated delay probability predictions.

### Saved Artifacts Location
Path: `backend/app/models/d5_artifacts/` (or configured model directory)
* `delay-model-calibrated.joblib`: Pre-trained `CalibratedClassifierCV` wrapper over `GradientBoostingClassifier`.
* `preprocessor.joblib`: `ColumnTransformer` handles categorical one-hot encoding and numerical scaling.
* `feature_schema.json`: Strict input feature schema definitions.
* `model_metadata.json`: Model versioning and metrics metadata.

### Evaluation Metrics (Honest Benchmark)
* **Held-out Test ROC-AUC**: `0.6905`
* **Test Brier Score**: `0.222343`
* **Reference AUC**: `0.7920`

> [!IMPORTANT]
> Do NOT claim 100% accuracy or call ROC-AUC "accuracy". Present output as "Predicted Delay Probability".

### Zero Target Leakage Policy
The following outcome columns are strictly excluded from prediction inputs:
* `future_delay`
* `delay_days`
* `delay_horizon`
* `future_delayed_stage`
* `actual_completion_date`

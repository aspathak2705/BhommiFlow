# 14. Demo Day Checklist

## Preparation Timeline

### T-24 Hours
- [x] Run full backend integration test suite (`python -m pytest tests/test_final_integration.py`). Confirm 100% PASS.
- [x] Build frontend production bundle (`npm run build`). Confirm zero build errors.
- [x] Verify D5 ML model artifacts (`delay-model-calibrated.joblib`, `preprocessor.joblib`).

### T-2 Hours
- [x] Launch PostgreSQL database and verify connection.
- [x] Start FastAPI backend server (`uvicorn app.main:app --port 8000`).
- [x] Start React frontend server (`npm run dev`).
- [x] Perform dry run of 5-minute click-by-click demo script.

### T-30 Minutes
- [x] Verify primary demo project fixture (`PRJ-TEST-INTEG-001`) is present in database.
- [x] Open Chrome browser in clean incognito window.
- [x] Verify browser developer console is free of errors.

### T-10 Minutes
- [x] Confirm laptop charger and projection display settings.
- [x] Verify offline notification simulation triggers successfully (`SIM-SMS-` and `SIM-WA-`).

### During Demo
- [x] Follow `02_5_MINUTE_DEMO_SCRIPT.md` strictly.
- [x] Keep browser zoom at 100%. Highlight Evidence RAG and D5 Prediction callouts.

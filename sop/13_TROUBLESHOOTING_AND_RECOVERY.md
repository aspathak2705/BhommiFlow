# 13. Troubleshooting and Recovery

| Problem | Symptom | Diagnostic Step | Safe Recovery Fix |
| :--- | :--- | :--- | :--- |
| **Backend Startup Failure** | `IntegrityError` or missing column | Run `python -c "from app.core.database import engine; print(engine)"` | Ensure DB migrations are up to date via alembic or restart backend service. |
| **D5 Model Artifact Missing** | `FileNotFoundError: preprocessor.joblib` | Check `backend/app/models/` for joblib artifacts | Verify `pandas` and `scikit-learn` versions match model environment. |
| **RAG Query Returns 0 Results**| Empty knowledge list | Query `knowledge_chunks` table for `project_id` | Run `UnifiedIngestionService.ingest_all()` fixture loader. |
| **Notification Simulation Stood**| Status stays `QUEUED` | Check `NotificationService.send_sms()` logs | Ensure notification endpoint returns HTTP 200 simulation response. |
| **CORS Error on Frontend** | `Access-Control-Allow-Origin` error | Check `main.py` origins configuration | Add frontend host URL (`http://localhost:5173`) to `CORS_ORIGINS`. |

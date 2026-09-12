# 13. Troubleshooting & Failure Recovery Guide

## Common Symptoms, Root Causes & Fixes

### 1. Backend Fails to Start (`uvicorn` crash)
- **Symptom:** `ModuleNotFoundError: No module named 'app'`
- **Cause:** Running uvicorn from root instead of setting PYTHONPATH or executing inside `backend/`.
- **Fix:** Run `cd backend` then `python -m uvicorn app.main:app --reload --port 8000`.

### 2. Database Connection Error
- **Symptom:** `psycopg2.OperationalError: connection to server at localhost failed`
- **Cause:** Local PostgreSQL daemon stopped or incorrect password in `.env`.
- **Fix:** System automatically falls back to SQLite `backend/bhommiflow.db` or remote Render PostgreSQL connection. Verify `DATABASE_URL` in `backend/.env`.

### 3. Audio/TTS Plays No Sound
- **Symptom:** User clicks **Listen** button, but no audio is heard.
- **Cause:** Sarvam AI API key empty or browser blocked auto-play audio.
- **Fix:** BhoomiSakha automatically activates browser-native `window.speechSynthesis` (Web Speech API) fallback. Ensure OS speaker volume is unmuted.

### 4. Notification Push Returns 500 Error
- **Symptom:** Notification simulation fails during officer decision step.
- **Cause:** Unhandled exception in provider wrapper.
- **Fix:** Notification system operates in provider-independent simulation mode (`QUEUED` -> `SENT` -> `DELIVERED`). Verify status in Notification Drawer tab.

### 5. Document Upload Error in Frontend
- **Symptom:** Frontend displays "Upload Failed".
- **Cause:** File format not supported or project ID mismatched.
- **Fix:** Use pre-validated PDF files from `docs/SOP/demo_pack/mock_documents/` (`01_land_record.pdf` through `06_conflicting_record.pdf`).

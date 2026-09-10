import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.services.guidance_system import GuidanceSystem
from app.services.speech_service import SpeechService
from app.services.speech_to_text_service import SpeechToTextService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/guidance/{context}")
def get_guidance(context: str, language: str = "en", current_user: User = Depends(get_current_user)):
    """
    Retrieve translated contextual guidance text.
    """
    return GuidanceSystem.get_guidance(context, language)

@router.post("/speech/synthesize")
def synthesize_speech(payload: dict, current_user: User = Depends(get_current_user)):
    """
    Synthesize guidance text to speech.
    """
    text = payload.get("text", "")
    language = payload.get("language", "en")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text parameter for speech synthesis")
    try:
        return SpeechService.synthesize_speech(text, language)
    except ValueError as val_err:
        raise HTTPException(status_code=503, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis execution failure: {str(e)}")

@router.post("/speech/transcribe")
def transcribe_speech(
    audio: UploadFile = File(...), 
    language: str = Form("en"), 
    current_user: User = Depends(get_current_user)
):
    """
    Transcribe spoken audio files into text using Sarvam AI STT models.
    """
    # Restrict file size limit to max 10MB
    MAX_AUDIO_SIZE = 10 * 1024 * 1024
    content = audio.file.read()
    if len(content) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=400, detail="Audio file size exceeds maximum permitted limit (10MB)")

    allowed_types = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/x-wav", "application/octet-stream"]
    if audio.content_type not in allowed_types and not audio.filename.endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid audio file type. Only WAV, MP3, and M4A format are supported.")

    try:
        result = SpeechToTextService.transcribe_audio(content, audio.filename, language)
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=503, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech transcription execution failure: {str(e)}")

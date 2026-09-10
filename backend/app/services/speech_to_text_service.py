import logging
import urllib.request
import json
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class SpeechToTextService:
    @staticmethod
    def transcribe_audio(audio_bytes: bytes, filename: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribes audio data using Sarvam STT API if configured.
        Otherwise, returns controlled service-unavailable/simulation response.
        """
        api_key = settings.SARVAM_API_KEY
        
        # Sarvam saaras:v1 STT model expects audio data as multipart/form-data
        if not api_key or api_key == "":
            raise ValueError("Voice transcription service is not configured.")

        LANGUAGE_CODES = {
            "en": "en-IN",
            "hi": "hi-IN",
            "mr": "mr-IN",
        }
        lang_code = LANGUAGE_CODES.get(language.lower(), "en-IN")

        url = f"{settings.SARVAM_BASE_URL.rstrip('/')}/speech-to-text"
        
        # Build multipart payload manually using standard urllib boundary processing
        boundary = "----BhoomiFlowBoundary381749"
        headers = {
            "api-subscription-key": api_key,
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }

        # Format multipart body
        body = []
        
        # Add model parameter
        body.append(f"--{boundary}".encode("utf-8"))
        body.append(f'Content-Disposition: form-data; name="model"'.encode("utf-8"))
        body.append("".encode("utf-8"))
        body.append(settings.SARVAM_STT_MODEL.encode("utf-8"))
        
        # Add language code
        body.append(f"--{boundary}".encode("utf-8"))
        body.append(f'Content-Disposition: form-data; name="language_code"'.encode("utf-8"))
        body.append("".encode("utf-8"))
        body.append(lang_code.encode("utf-8"))

        # Add file content
        body.append(f"--{boundary}".encode("utf-8"))
        body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode("utf-8"))
        body.append(f"Content-Type: audio/wav".encode("utf-8"))
        body.append("".encode("utf-8"))
        body.append(audio_bytes)
        
        body.append(f"--{boundary}--".encode("utf-8"))
        
        # Join bytes with CRLF (\r\n)
        data = b"\r\n".join(body)

        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                transcript = res_data.get("transcript", "")
                return {
                    "status": "SUCCESS",
                    "text": transcript,
                    "language": language,
                    "message": "Transcription finished successfully."
                }
        except Exception as e:
            logger.error(f"Sarvam STT transcription call failed: {str(e)}")
            return {
                "status": "FAILED",
                "text": "",
                "message": f"Voice transcription failed: {str(e)}"
            }

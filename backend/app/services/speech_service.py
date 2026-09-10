import logging
import urllib.request
import urllib.parse
import json
import base64
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class SpeechService:
    @staticmethod
    def synthesize_speech(text: str, language: str = "en") -> Dict[str, Any]:
        """
        Synthesizes text into audio data.
        If SPEECH_PROVIDER is 'sarvam' and credentials exist, calls Sarvam API.
        Otherwise, throws an explicit configuration error.
        """
        provider = settings.SPEECH_PROVIDER.lower()
        api_key = settings.SARVAM_API_KEY
        
        if provider != "sarvam" or not api_key or api_key == "":
            raise ValueError("Speech service is not configured.")

        # Determine language code for Sarvam TTS (expects standard iso code mapping)
        LANGUAGE_CODES = {
            "en": "en-IN",
            "hi": "hi-IN",
            "mr": "mr-IN",
        }
        lang_code = LANGUAGE_CODES.get(language.lower(), "en-IN")

        try:
            # Do direct API post because SDK forces pitch/loudness parameters which Bulbul v3 rejects
            url = "https://api.sarvam.ai/text-to-speech"
            headers = {
                "api-subscription-key": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": [text],
                "target_language_code": lang_code,
                "speaker": "ritu",
                "model": "bulbul:v3"
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                resp_json = json.loads(response.read().decode("utf-8"))
                audio_b64 = resp_json["audios"][0]

            if not audio_b64:
                raise ValueError("No audio content returned from Sarvam AI TTS endpoint")

            return {
                "status": "SUCCESS",
                "audio_url": None,
                "audio_content_base64": audio_b64,
                "message": "Speech successfully synthesized."
            }
        except Exception as e:
            logger.error(f"Sarvam SDK TTS synthesis failed: {str(e)}")
            raise e

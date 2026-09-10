import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file_path = BASE_DIR / ".env"

# Force values from local .env to override global system environment variables
if env_file_path.exists():
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/bhoomiflow"
    SUPABASE_DATABASE_URL: str = ""
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    NVIDIA_API_KEY: str = "nvapi-placeholder-or-empty"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "nvidia/nemotron-3-super-120b-a12b:free"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    SMS_PROVIDER: str = "twilio"  # Default provider interface integration
    SMS_PROVIDER_KEY: str = "sms-provider-placeholder"
    SMS_API_KEY: str = ""  # For general provider API keys
    SMS_API_SECRET: str = ""  # For secret keys/auth tokens
    SMS_SENDER_ID: str = "BFMUT"  # Or phone number
    SARVAM_API_KEY: str = ""
    SARVAM_BASE_URL: str = "https://api.sarvam.ai"
    SARVAM_TTS_MODEL: str = "bulbul:v3"
    SARVAM_STT_MODEL: str = "saaras:v1"
    SPEECH_PROVIDER: str = "offline"

    model_config = SettingsConfigDict(
        env_file=str(env_file_path), 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()

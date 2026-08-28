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
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/bhoomiflow"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    NVIDIA_API_KEY: str = "nvapi-placeholder-or-empty"
    NVIDIA_MODEL: str = "meta/llama-3.1-405b-instruct"
    SMS_PROVIDER_KEY: str = "sms-provider-placeholder"
    SMS_SENDER_ID: str = "BFMUT"

    model_config = SettingsConfigDict(
        env_file=str(env_file_path), 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()

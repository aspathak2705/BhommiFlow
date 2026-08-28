import os
import shutil
from fastapi import UploadFile

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")

class DocumentStorageService:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)

    def store(self, file_id: str, file: UploadFile) -> str:
        # Prevent path traversal by sanitizing name inputs
        safe_name = os.path.basename(file_id)
        target_path = os.path.join(STORAGE_DIR, safe_name)
        
        # Reset file read cursor
        file.file.seek(0)
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return target_path

    def retrieve(self, file_reference: str) -> bytes:
        if not self.exists(file_reference):
            raise FileNotFoundError("Storage file does not exist")
        with open(file_reference, "rb") as f:
            return f.read()

    def exists(self, file_reference: str) -> bool:
        return os.path.exists(file_reference) and os.path.isfile(file_reference)

storage_service = DocumentStorageService()

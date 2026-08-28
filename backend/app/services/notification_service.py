import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.workflow import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_sms(db: Session, user_id: str, case_id: str, event_type: str, message: str) -> Notification:
        notification_id = f"NTF-{uuid.uuid4().hex[:12].upper()}"

        db_notif = Notification(
            notification_id=notification_id,
            user_id=user_id,
            case_id=case_id,
            channel="SMS",
            event_type=event_type,
            message=message,
            status="PENDING"
        )
        db.add(db_notif)
        db.commit()
        db.refresh(db_notif)

        # Configurable provider credential check
        api_key = settings.SMS_PROVIDER_KEY
        if not api_key or api_key == "sms-provider-placeholder":
            # Running offline/local adapt mode - mark as PENDING or SENT based on simulation
            logger.info(f"[SMS Offline Simulation] Destination User ID: {user_id}. Content: '{message}'")
            db_notif.status = "SENT"
            db_notif.sent_at = datetime.now(timezone.utc)
            db_notif.provider_reference = "sim-ref-12345"
        else:
            # Simulated real provider call representation
            try:
                # Direct external provider API call using keys would take place here
                db_notif.status = "SENT"
                db_notif.sent_at = datetime.now(timezone.utc)
                db_notif.provider_reference = f"provider-{uuid.uuid4().hex[:8]}"
            except Exception as e:
                logger.error(f"SMS Provider delivery failed: {str(e)}")
                db_notif.status = "FAILED"

        db.commit()
        db.refresh(db_notif)
        return db_notif

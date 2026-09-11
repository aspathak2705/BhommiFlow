import uuid
import logging
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.workflow import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_sms(db: Session, user_id: str, case_id: str, event_type: str, message: str) -> Notification:
        notification_id = f"SIM-SMS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"

        db_notif = Notification(
            notification_id=notification_id,
            user_id=user_id,
            case_id=case_id,
            channel="SMS",
            event_type=event_type,
            message=message,
            status="DELIVERED",
            provider_reference=f"sim-sms-ref-{uuid.uuid4().hex[:8]}",
            sent_at=datetime.now(timezone.utc)
        )
        db.add(db_notif)
        db.commit()
        db.refresh(db_notif)
        logger.info(f"[SMS Simulation] Sent notification {notification_id} for case {case_id}")
        return db_notif

    @staticmethod
    def send_whatsapp(db: Session, user_id: str, case_id: str, event_type: str, message: str) -> Notification:
        notification_id = f"SIM-WA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"

        db_notif = Notification(
            notification_id=notification_id,
            user_id=user_id,
            case_id=case_id,
            channel="WHATSAPP",
            event_type=event_type,
            message=message,
            status="READ",
            provider_reference=f"sim-wa-ref-{uuid.uuid4().hex[:8]}",
            sent_at=datetime.now(timezone.utc)
        )
        db.add(db_notif)
        db.commit()
        db.refresh(db_notif)
        logger.info(f"[WhatsApp Simulation] Sent notification {notification_id} for case {case_id}")
        return db_notif

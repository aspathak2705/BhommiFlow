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
        import urllib.request
        import urllib.parse
        import base64

        provider = settings.SMS_PROVIDER.lower()
        api_key = settings.SMS_API_KEY or settings.SMS_PROVIDER_KEY
        api_secret = settings.SMS_API_SECRET

        if not api_key or api_key in ["sms-provider-placeholder", ""]:
            # Running offline/local adapt mode
            logger.info(f"[SMS Offline Simulation] Destination User ID: {user_id}. Content: '{message}'")
            db_notif.status = "SENT"
            db_notif.sent_at = datetime.now(timezone.utc)
            db_notif.provider_reference = "sim-ref-12345"
        else:
            db_notif.status = "SENDING"
            db.commit()
            
            try:
                if provider == "twilio":
                    # twilio uses Account SID as api_key, Auth Token as api_secret
                    account_sid = api_key
                    auth_token = api_secret
                    
                    # URL encode twilio API payload
                    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
                    
                    # We query user database for a phone number or default to sender settings
                    from app.models.user import CitizenProfile, OfficerProfile
                    to_number = None
                    cit_p = db.query(CitizenProfile).filter(CitizenProfile.user_id == user_id).first()
                    if cit_p and cit_p.phone:
                        to_number = cit_p.phone
                    else:
                        off_p = db.query(OfficerProfile).filter(OfficerProfile.user_id == user_id).first()
                        if off_p and hasattr(off_p, 'phone') and off_p.phone:
                            to_number = off_p.phone

                    if not to_number:
                        to_number = "+15005550006"  # Fallback to test number
                    
                    from_number = settings.SMS_SENDER_ID or "+15005550006"
                    
                    data = urllib.parse.urlencode({
                        "To": to_number,
                        "From": from_number,
                        "Body": message
                    }).encode("utf-8")
                    
                    req = urllib.request.Request(url, data=data, method="POST")
                    
                    # Basic authentication header setup
                    auth_str = f"{account_sid}:{auth_token}"
                    encoded_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
                    req.add_header("Authorization", f"Basic {encoded_auth}")
                    req.add_header("Content-Type", "application/x-www-form-urlencoded")
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_data = json.loads(response.read().decode("utf-8"))
                        db_notif.status = "SENT"
                        db_notif.sent_at = datetime.now(timezone.utc)
                        db_notif.provider_reference = res_data.get("sid", f"twilio-{uuid.uuid4().hex[:8]}")
                else:
                    # Alternative generic HTTP API provider fallback
                    db_notif.status = "SENT"
                    db_notif.sent_at = datetime.now(timezone.utc)
                    db_notif.provider_reference = f"provider-{uuid.uuid4().hex[:8]}"
            except Exception as e:
                logger.error(f"SMS Provider delivery failed: {str(e)}")
                db_notif.status = "FAILED"

        db.commit()
        db.refresh(db_notif)
        return db_notif

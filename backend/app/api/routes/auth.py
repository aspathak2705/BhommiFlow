import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, CitizenProfile, OfficerProfile
from app.schemas.user import UserCreate, UserResponse, LoginRequest

router = APIRouter()

# Simple token mapping for mock authorization session (production-safe, no mocks in db)
# Maps custom tokens to user IDs
TOKEN_DB = {}

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    token = authorization.replace("Bearer ", "")
    user_id = TOKEN_DB.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token or session")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token or session")
    return user

@router.post("/auth/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_id = f"USR-{uuid.uuid4().hex[:12].upper()}"
    db_user = User(
        id=user_id,
        username=user_in.username,
        role=user_in.role,
    )
    db.add(db_user)

    if user_in.role == "citizen":
        db_profile = CitizenProfile(
            user_id=user_id,
            full_name=user_in.full_name,
            email=user_in.email,
            phone=user_in.phone,
            preferred_language=user_in.preferred_language
        )
        db.add(db_profile)
    elif user_in.role == "officer":
        db_profile = OfficerProfile(
            user_id=user_id,
            full_name=user_in.full_name,
            department=user_in.department or "Land Records",
            designation=user_in.designation or "Talathi",
            office=user_in.office or "Taluka Office",
            district=user_in.district or "District",
            taluka=user_in.taluka or "Taluka",
        )
        db.add(db_profile)
    else:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'citizen' or 'officer'")

    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # In a real app, passwords would be hashed. For Phase 1, we simple-authenticate.
    token = f"TOKEN-{uuid.uuid4().hex[:16].upper()}"
    TOKEN_DB[token] = user.id
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

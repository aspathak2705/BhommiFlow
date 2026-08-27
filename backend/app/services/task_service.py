import uuid
from sqlalchemy.orm import Session
from app.models.task import TeachingTask
from app.models.class_ import Class
from app.schemas.task import TeachingTaskCreate, TeachingTaskUpdate

def create_task(db: Session, task_in: TeachingTaskCreate) -> TeachingTask:
    # Validate that class exists
    class_exists = db.query(Class).filter(Class.id == task_in.class_id).first()
    if not class_exists:
        raise ValueError(f"Class with id '{task_in.class_id}' does not exist.")

    # Generate custom human-readable ID prefix
    short_id = str(uuid.uuid4())[:8].upper()
    task_id = f"TASK-{short_id}"

    db_task = TeachingTask(
        id=task_id,
        teacher_id=task_in.teacher_id,
        class_id=task_in.class_id,
        subject=task_in.subject,
        topic=task_in.topic,
        duration_minutes=task_in.duration_minutes,
        language=task_in.language,
        status="draft"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: str) -> TeachingTask:
    return db.query(TeachingTask).filter(TeachingTask.id == task_id).first()

def list_teacher_tasks(db: Session, teacher_id: str):
    return db.query(TeachingTask).filter(TeachingTask.teacher_id == teacher_id).order_by(TeachingTask.created_at.desc()).all()

def update_task(db: Session, task_id: str, task_update: TeachingTaskUpdate) -> TeachingTask:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

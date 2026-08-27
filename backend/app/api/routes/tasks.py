from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.schemas.teacher import TeacherResponse
from app.schemas.class_ import ClassResponse
from app.schemas.task import TeachingTaskCreate, TeachingTaskResponse, TeachingTaskUpdate
from app.services import task_service

router = APIRouter()

# Get teacher
@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

# Get classes for a teacher
@router.get("/teachers/{teacher_id}/classes", response_model=List[ClassResponse])
def get_classes(teacher_id: str, db: Session = Depends(get_db)):
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    return classes

# Get specific class
@router.get("/classes/{class_id}", response_model=ClassResponse)
def get_class(class_id: str, db: Session = Depends(get_db)):
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_obj

# Create teaching task
@router.post("/tasks", response_model=TeachingTaskResponse)
def create_task(task_in: TeachingTaskCreate, db: Session = Depends(get_db)):
    try:
        return task_service.create_task(db=db, task_in=task_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get tasks for a teacher
@router.get("/teachers/{teacher_id}/tasks", response_model=List[TeachingTaskResponse])
def get_tasks(teacher_id: str, db: Session = Depends(get_db)):
    return task_service.list_teacher_tasks(db=db, teacher_id=teacher_id)

# Get specific task
@router.get("/tasks/{task_id}", response_model=TeachingTaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = task_service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update task
@router.patch("/tasks/{task_id}", response_model=TeachingTaskResponse)
def update_task(task_id: str, task_update: TeachingTaskUpdate, db: Session = Depends(get_db)):
    task = task_service.update_task(db=db, task_id=task_id, task_update=task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

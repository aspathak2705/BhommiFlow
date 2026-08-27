import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models.teacher import Teacher
from app.models.class_ import Class

def seed():
    db = SessionLocal()
    try:
        # Check if demo teacher exists
        teacher = db.query(Teacher).filter(Teacher.id == "teacher-demo-001").first()
        if not teacher:
            teacher = Teacher(id="teacher-demo-001", name="Priya Sharma")
            db.add(teacher)
            db.commit()
            print("Demo teacher Priya Sharma created.")
        else:
            print("Demo teacher Priya Sharma already exists.")

        # Check if demo class exists
        class_obj = db.query(Class).filter(Class.id == "class-7a").first()
        if not class_obj:
            class_obj = Class(
                id="class-7a",
                teacher_id="teacher-demo-001",
                name="Class 7A",
                grade="7",
                section="A",
                primary_language="mr"
            )
            db.add(class_obj)
            db.commit()
            print("Demo class Class 7A (Marathi) created.")
        else:
            print("Demo class Class 7A (Marathi) already exists.")
    except Exception as e:
        print("Error seeding data:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()

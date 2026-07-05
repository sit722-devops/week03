import logging
import sys
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Student
from app.schemas import StudentCreate, StudentResponse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("student-service")

app = FastAPI(
    title="Student Service",
    description="Week 03 Student Service with FastAPI, PostgreSQL and Docker Compose",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    max_retries = 10
    retry_delay_seconds = 5

    for attempt in range(max_retries):
        try:
            logger.info(
                f"Connecting to PostgreSQL and creating tables "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            Base.metadata.create_all(bind=engine)

            logger.info("PostgreSQL connection successful. Tables are ready.")
            break

        except OperationalError as error:
            logger.warning(f"PostgreSQL connection failed: {error}")

            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                logger.critical("PostgreSQL connection failed after all retries.")
                sys.exit(1)

        except Exception as error:
            logger.critical(
                f"Unexpected error during database startup: {error}", exc_info=True
            )
            sys.exit(1)


@app.get("/")
def root():
    logger.info("Root endpoint accessed.")

    return {
        "message": "Welcome to Student Service",
        "service": "student-service",
        "week": "week-03",
    }


@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed.")

    return {"status": "healthy", "service": "student-service"}


@app.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    logger.info("Retrieving all students.")

    return db.query(Student).all()


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: str, db: Session = Depends(get_db)):
    logger.info(f"Retrieving student with ID: {student_id}")

    student = db.query(Student).filter(Student.student_id == student_id).first()

    if student is None:
        logger.warning(f"Student not found: {student_id}")
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating student with ID: {student.student_id}")

    existing_student = (
        db.query(Student).filter(Student.student_id == student.student_id).first()
    )

    if existing_student:
        logger.warning(f"Duplicate student ID attempted: {student.student_id}")
        raise HTTPException(status_code=400, detail="Student ID already exists")

    new_student = Student(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        program=student.program,
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    logger.info(f"Student created successfully: {student.student_id}")

    return new_student

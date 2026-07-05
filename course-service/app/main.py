import logging
import sys
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Course
from app.schemas import CourseCreate, CourseResponse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("course-service")

app = FastAPI(
    title="Course Service",
    description="Week 03 Course Service with FastAPI, PostgreSQL and Docker Compose",
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
        "message": "Welcome to Course Service",
        "service": "course-service",
        "week": "week-03",
    }


@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed.")

    return {"status": "healthy", "service": "course-service"}


@app.get("/courses", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    logger.info("Retrieving all courses.")

    return db.query(Course).all()


@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: str, db: Session = Depends(get_db)):
    logger.info(f"Retrieving course with ID: {course_id}")

    course = db.query(Course).filter(Course.course_id == course_id).first()

    if course is None:
        logger.warning(f"Course not found: {course_id}")
        raise HTTPException(status_code=404, detail="Course not found")

    return course


@app.post("/courses", response_model=CourseResponse, status_code=201)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating course with ID: {course.course_id}")

    existing_course = (
        db.query(Course).filter(Course.course_id == course.course_id).first()
    )

    if existing_course:
        logger.warning(f"Duplicate course ID attempted: {course.course_id}")
        raise HTTPException(status_code=400, detail="Course ID already exists")

    new_course = Course(
        course_id=course.course_id,
        course_name=course.course_name,
        credit_points=course.credit_points,
        faculty=course.faculty,
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    logger.info(f"Course created successfully: {course.course_id}")

    return new_course

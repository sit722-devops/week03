from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import Course

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def delete_test_course(course_id: str):
    db = SessionLocal()
    try:
        db.query(Course).filter(Course.course_id == course_id).delete()
        db.commit()
    finally:
        db.close()


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "course-service"
    assert response.json()["week"] == "week-03"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_all_courses():
    response = client.get("/courses")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_course():
    test_course_id = "TEST-SIT722"

    delete_test_course(test_course_id)

    new_course = {
        "course_id": test_course_id,
        "course_name": "DevOps",
        "credit_points": 6,
        "faculty": "School of IT",
    }

    response = client.post("/courses", json=new_course)

    assert response.status_code == 201
    assert response.json()["course_id"] == test_course_id
    assert response.json()["course_name"] == "DevOps"

    delete_test_course(test_course_id)


def test_get_course_by_id():
    test_course_id = "TEST-SIT737"

    delete_test_course(test_course_id)

    test_course = {
        "course_id": test_course_id,
        "course_name": "Cloud Native Application Development",
        "credit_points": 6,
        "faculty": "School of IT",
    }

    client.post("/courses", json=test_course)

    response = client.get(f"/courses/{test_course_id}")

    assert response.status_code == 200
    assert response.json()["course_id"] == test_course_id
    assert response.json()["course_name"] == "Cloud Native Application Development"

    delete_test_course(test_course_id)


def test_get_course_not_found():
    response = client.get("/courses/TEST-UNKNOWN")

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_create_course_duplicate_id():
    test_course_id = "TEST-SIT725"

    delete_test_course(test_course_id)

    course = {
        "course_id": test_course_id,
        "course_name": "Software Engineering",
        "credit_points": 6,
        "faculty": "School of IT",
    }

    client.post("/courses", json=course)

    duplicate_course = {
        "course_id": test_course_id,
        "course_name": "Duplicate Course",
        "credit_points": 6,
        "faculty": "School of IT",
    }

    response = client.post("/courses", json=duplicate_course)

    assert response.status_code == 400
    assert response.json()["detail"] == "Course ID already exists"

    delete_test_course(test_course_id)

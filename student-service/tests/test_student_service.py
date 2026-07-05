from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import Course

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def delete_test_student(student_id: str):
    db = SessionLocal()
    try:
        db.query(Student).filter(Student.student_id == student_id).delete()
        db.commit()
    finally:
        db.close()


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "student-service"
    assert response.json()["week"] == "week-03"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_all_students():
    response = client.get("/students")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_student():
    test_student_id = "TEST-S100001"

    delete_test_student(test_student_id)

    new_student = {
        "student_id": test_student_id,
        "name": "John Smith",
        "email": "john.smith@campus.edu.au",
        "program": "Master of Information Technology",
    }

    response = client.post("/students", json=new_student)

    assert response.status_code == 201
    assert response.json()["student_id"] == test_student_id
    assert response.json()["name"] == "John Smith"

    delete_test_student(test_student_id)


def test_get_student_by_id():
    test_student_id = "TEST-S100002"

    delete_test_student(test_student_id)

    test_student = {
        "student_id": test_student_id,
        "name": "Emma Brown",
        "email": "emma.brown@campus.edu.au",
        "program": "Master of Cyber Security",
    }

    client.post("/students", json=test_student)

    response = client.get(f"/students/{test_student_id}")

    assert response.status_code == 200
    assert response.json()["student_id"] == test_student_id
    assert response.json()["name"] == "Emma Brown"

    delete_test_student(test_student_id)


def test_get_student_not_found():
    response = client.get("/students/TEST-S999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_create_student_duplicate_id():
    test_student_id = "TEST-S100003"

    delete_test_student(test_student_id)

    student = {
        "student_id": test_student_id,
        "name": "Liam Wilson",
        "email": "liam.wilson@campus.edu.au",
        "program": "Master of Data Science",
    }

    client.post("/students", json=student)

    duplicate_student = {
        "student_id": test_student_id,
        "name": "Duplicate Student",
        "email": "duplicate@campus.edu.au",
        "program": "Master of Information Technology",
    }

    response = client.post("/students", json=duplicate_student)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student ID already exists"

    delete_test_student(test_student_id)

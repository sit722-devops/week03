from pydantic import BaseModel


class CourseCreate(BaseModel):
    course_id: str
    course_name: str
    credit_points: int
    faculty: str


class CourseResponse(BaseModel):
    course_id: str
    course_name: str
    credit_points: int
    faculty: str

    class Config:
        from_attributes = True

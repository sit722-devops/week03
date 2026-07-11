from pydantic import BaseModel, ConfigDict


class CourseCreate(BaseModel):
    course_id: str
    course_name: str
    credit_points: int
    faculty: str


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    course_id: str
    course_name: str
    credit_points: int
    faculty: str


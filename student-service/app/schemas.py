from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    student_id: str
    name: str
    email: EmailStr
    program: str


class StudentResponse(BaseModel):
    student_id: str
    name: str
    email: EmailStr
    program: str

    class Config:
        from_attributes = True

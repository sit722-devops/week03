import { useEffect, useState } from "react";

const STUDENT_API_URL = "/api/students";
const COURSE_API_URL = "/api/courses";

function App() {
    const [students, setStudents] = useState([]);
    const [courses, setCourses] = useState([]);

    const [studentForm, setStudentForm] = useState({
        student_id: "",
        name: "",
        email: "",
        program: ""
    });

    const [courseForm, setCourseForm] = useState({
        course_id: "",
        course_name: "",
        credit_points: 6,
        faculty: ""
    });

    const fetchStudents = async () => {
        const response = await fetch(STUDENT_API_URL);
        const data = await response.json();
        setStudents(data);
    };

    const fetchCourses = async () => {
        const response = await fetch(COURSE_API_URL);
        const data = await response.json();
        setCourses(data);
    };

    useEffect(() => {
        fetchStudents();
        fetchCourses();
    }, []);

    const createStudent = async (event) => {
        event.preventDefault();

        await fetch(STUDENT_API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(studentForm)
        });

        setStudentForm({
            student_id: "",
            name: "",
            email: "",
            program: ""
        });

        fetchStudents();
    };

    const createCourse = async (event) => {
        event.preventDefault();

        await fetch(COURSE_API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                ...courseForm,
                credit_points: Number(courseForm.credit_points)
            })
        });

        setCourseForm({
            course_id: "",
            course_name: "",
            credit_points: 6,
            faculty: ""
        });

        fetchCourses();
    };

    return (
        <div className="container">
            <h1>Campus Course Platform</h1>
            <p>Week 03 - Docker Compose with Multiple Microservices</p>

            <div className="grid">
                <section className="card">
                    <h2>Add Student</h2>

                    <form onSubmit={createStudent}>
                        <input
                            placeholder="Student ID"
                            value={studentForm.student_id}
                            onChange={(e) =>
                                setStudentForm({ ...studentForm, student_id: e.target.value })
                            }
                        />

                        <input
                            placeholder="Name"
                            value={studentForm.name}
                            onChange={(e) =>
                                setStudentForm({ ...studentForm, name: e.target.value })
                            }
                        />

                        <input
                            placeholder="Email"
                            value={studentForm.email}
                            onChange={(e) =>
                                setStudentForm({ ...studentForm, email: e.target.value })
                            }
                        />

                        <input
                            placeholder="Program"
                            value={studentForm.program}
                            onChange={(e) =>
                                setStudentForm({ ...studentForm, program: e.target.value })
                            }
                        />

                        <button type="submit">Add Student</button>
                    </form>

                    <h3>Students</h3>

                    {students.length === 0 ? (
                        <p className="empty-message">No student data found.</p>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>Student ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Program</th>
                                </tr>
                            </thead>
                            <tbody>
                                {students.map((student) => (
                                    <tr key={student.student_id}>
                                        <td>{student.student_id}</td>
                                        <td>{student.name}</td>
                                        <td>{student.email}</td>
                                        <td>{student.program}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </section>

                <section className="card">
                    <h2>Add Course</h2>

                    <form onSubmit={createCourse}>
                        <input
                            placeholder="Course ID"
                            value={courseForm.course_id}
                            onChange={(e) =>
                                setCourseForm({ ...courseForm, course_id: e.target.value })
                            }
                        />

                        <input
                            placeholder="Course Name"
                            value={courseForm.course_name}
                            onChange={(e) =>
                                setCourseForm({ ...courseForm, course_name: e.target.value })
                            }
                        />

                        <input
                            type="number"
                            placeholder="Credit Points"
                            value={courseForm.credit_points}
                            onChange={(e) =>
                                setCourseForm({ ...courseForm, credit_points: e.target.value })
                            }
                        />

                        <input
                            placeholder="Faculty"
                            value={courseForm.faculty}
                            onChange={(e) =>
                                setCourseForm({ ...courseForm, faculty: e.target.value })
                            }
                        />

                        <button type="submit">Add Course</button>
                    </form>

                    <h3>Courses</h3>

                    {courses.length === 0 ? (
                        <p className="empty-message">No course data found.</p>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>Course ID</th>
                                    <th>Course Name</th>
                                    <th>Credit Points</th>
                                    <th>Faculty</th>
                                </tr>
                            </thead>
                            <tbody>
                                {courses.map((course) => (
                                    <tr key={course.course_id}>
                                        <td>{course.course_id}</td>
                                        <td>{course.course_name}</td>
                                        <td>{course.credit_points}</td>
                                        <td>{course.faculty}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </section>
            </div>
        </div>
    );
}

export default App;
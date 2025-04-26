from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Student Portal API")

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# -------------------- DATA MODELS --------------------


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: Optional[date] = None

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    student_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    course_code: str
    title: str
    description: Optional[str] = None
    credits: int = Field(gt=0)

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    course_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    grade: Optional[str] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    enrollment_id: int
    enrollment_date: datetime

    class Config:
        from_attributes = True

# -------------------- DATABASE UTILITY FUNCTIONS --------------------
# TODO: Implement connection pooling
# import mysql.connector.pooling

def execute_query(query, params=None, fetch=True, fetch_one=False, commit=False):
    """
    Execute a database query with error handling and connection management
    
    Args:
        query: SQL query string
        params: Parameters for the query
        fetch: Whether to fetch results
        fetch_one: Whether to fetch a single row
        commit: Whether to commit the transaction
        
    Returns:
        Query results or None
    """
    connection = None
    cursor = None
    try:
        # TODO: Get connection from connection pool
        # connection = connection_pool.get_connection()
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Execute query with or without parameters
        cursor.execute(query, params or ())
        
        # Handle different query types
        result = None
        if fetch:
            if fetch_one:

                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        if commit:
            connection.commit()
            if cursor.lastrowid and not result:
                result = cursor.lastrowid
        
        return result
    except Error as e:
        # Roll back if error occurs during transaction
        if connection and commit:
            connection.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def check_exists(table, id_field, id_value):
    """Check if a record exists in the given table"""
    query = f"SELECT 1 FROM {table} WHERE {id_field} = %s LIMIT 1"
    result = execute_query(query, (id_value,), fetch_one=True)
    if not result:
        raise HTTPException(status_code=404, detail=f"{table.capitalize()} with ID {id_value} not found")
    return True

# -------------------- STUDENT ENDPOINTS --------------------

@app.post("/students/", response_model=Student, status_code=201)
def create_student(student: StudentCreate):
    """Create a new student record"""
    query = """
    INSERT INTO students (first_name, last_name, email, date_of_birth)
    VALUES (%s, %s, %s, %s)
    """
    # Insert student and get new ID
    student_id = execute_query(
        query, 
        (student.first_name, student.last_name, student.email, student.date_of_birth), 
        commit=True
    )
    
    # Return the created student
    return execute_query(
        "SELECT * FROM students WHERE student_id = %s", 
        (student_id,), 
        fetch_one=True
    )

@app.get("/students/", response_model=List[Student])
def read_students():
    """Get all students"""
    return execute_query("SELECT * FROM students")

@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int):
    """Get a specific student by ID"""
    student = execute_query(
        "SELECT * FROM students WHERE student_id = %s", 
        (student_id,), 
        fetch_one=True
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentCreate):
    """Update a student's information"""
    # Check if student exists
    check_exists("students", "student_id", student_id)
    
    # Update student
    query = """
    UPDATE students
    SET first_name = %s, last_name = %s, email = %s, date_of_birth = %s
    WHERE student_id = %s
    """
    execute_query(
        query, 
        (student.first_name, student.last_name, student.email, student.date_of_birth, student_id), 
        commit=True
    )
    
    # Return updated student
    return execute_query(
        "SELECT * FROM students WHERE student_id = %s", 
        (student_id,), 
        fetch_one=True
    )

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    """Delete a student"""
    # Check if student exists
    check_exists("students", "student_id", student_id)
    
    # Delete student
    try:
        execute_query(
            "DELETE FROM students WHERE student_id = %s", 
            (student_id,), 
            fetch=False, 
            commit=True
        )
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Cannot delete student. The student is enrolled in one or more courses.")
    return None

# -------------------- COURSE ENDPOINTS --------------------


@app.post("/courses/", response_model=Course, status_code=201)
def create_course(course: CourseCreate):
    """Create a new course"""
    query = """
    INSERT INTO courses (course_code, title, description, credits)
    VALUES (%s, %s, %s, %s)
    """
    # Insert course and get new ID
    course_id = execute_query(
        query, 
        (course.course_code, course.title, course.description, course.credits), 
        commit=True
    )
    
    # Return the created course
    return execute_query(
        "SELECT * FROM courses WHERE course_id = %s", 
        (course_id,), 
        fetch_one=True
    )

@app.get("/courses/", response_model=List[Course])
def read_courses():
    """Get all courses"""
    return execute_query("SELECT * FROM courses")

@app.get("/courses/{course_id}", response_model=Course)
def read_course(course_id: int):
    """Get a specific course by ID"""
    course = execute_query(
        "SELECT * FROM courses WHERE course_id = %s", 
        (course_id,), 
        fetch_one=True
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put("/courses/{course_id}", response_model=Course)
def update_course(course_id: int, course: CourseCreate):
    """Update a course's information"""
    # Check if course exists
    check_exists("courses", "course_id", course_id)
    
    # Update course
    query = """
    UPDATE courses
    SET course_code = %s, title = %s, description = %s, credits = %s
    WHERE course_id = %s
    """
    execute_query(
        query, 
        (course.course_code, course.title, course.description, course.credits, course_id), 
        commit=True
    )
    
    # Return updated course
    return execute_query(
        "SELECT * FROM courses WHERE course_id = %s", 
        (course_id,), 
        fetch_one=True
    )

@app.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int):
    """Delete a course"""
    # Check if course exists
    check_exists("courses", "course_id", course_id)
    
    # Delete course
    execute_query(
        "DELETE FROM courses WHERE course_id = %s", 
        (course_id,), 
        fetch=False, 
        commit=True
    )
    return None

# -------------------- ENROLLMENT ENDPOINTS --------------------

@app.post("/enrollments/", response_model=Enrollment, status_code=201)
def create_enrollment(enrollment: EnrollmentCreate):
    """Create a new enrollment linking a student to a course"""
    # Verify both student and course exist
    check_exists("students", "student_id", enrollment.student_id)
    check_exists("courses", "course_id", enrollment.course_id)
    
    # Create enrollment
    query = """
    INSERT INTO enrollments (student_id, course_id, grade)
    VALUES (%s, %s, %s)
    """
    enrollment_id = execute_query(
        query, 
        (enrollment.student_id, enrollment.course_id, enrollment.grade), 
        commit=True
    )
    
    # Return the created enrollment
    return execute_query(
        "SELECT * FROM enrollments WHERE enrollment_id = %s", 
        (enrollment_id,), 
        fetch_one=True
    )

@app.get("/enrollments/", response_model=List[Enrollment])
def read_enrollments():
    """Get all enrollments"""
    return execute_query("SELECT * FROM enrollments")

@app.get("/enrollments/{enrollment_id}", response_model=Enrollment)
def read_enrollment(enrollment_id: int):
    """Get a specific enrollment by ID"""
    enrollment = execute_query(
        "SELECT * FROM enrollments WHERE enrollment_id = %s", 
        (enrollment_id,), 
        fetch_one=True
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment

@app.put("/enrollments/{enrollment_id}", response_model=Enrollment)
def update_enrollment(enrollment_id: int, enrollment: EnrollmentCreate):
    """Update an enrollment record"""
    # Verify enrollment, student and course all exist
    check_exists("enrollments", "enrollment_id", enrollment_id)
    check_exists("students", "student_id", enrollment.student_id)
    check_exists("courses", "course_id", enrollment.course_id)
    
    # Update enrollment
    query = """
    UPDATE enrollments
    SET student_id = %s, course_id = %s, grade = %s
    WHERE enrollment_id = %s
    """
    execute_query(
        query, 
        (enrollment.student_id, enrollment.course_id, enrollment.grade, enrollment_id), 
        commit=True
    )
    
    # Return updated enrollment
    return execute_query(
        "SELECT * FROM enrollments WHERE enrollment_id = %s", 
        (enrollment_id,), 
        fetch_one=True
    )

@app.delete("/enrollments/{enrollment_id}", status_code=204)
def delete_enrollment(enrollment_id: int):
    """Delete an enrollment"""
    # Check if enrollment exists
    check_exists("enrollments", "enrollment_id", enrollment_id)
    
    # Delete enrollment
    execute_query(
        "DELETE FROM enrollments WHERE enrollment_id = %s", 
        (enrollment_id,), 
        fetch=False, 
        commit=True
    )
    return None

# -------------------- RELATIONSHIP ENDPOINTS --------------------

@app.get("/students/{student_id}/courses", response_model=List[Course])
def get_student_courses(student_id: int):
    """Get all courses a student is enrolled in"""
    # Check if student exists
    check_exists("students", "student_id", student_id)
    
    # Get courses for student using JOIN
    query = """
    SELECT c.*
    FROM courses c
    JOIN enrollments e ON c.course_id = e.course_id
    WHERE e.student_id = %s
    """
    return execute_query(query, (student_id,))

@app.get("/courses/{course_id}/students", response_model=List[Student])
def get_course_students(course_id: int):
    """Get all students enrolled in a course"""
    # Check if course exists
    check_exists("courses", "course_id", course_id)
    
    # Get students for course using JOIN
    query = """
    SELECT s.*
    FROM students s
    JOIN enrollments e ON s.student_id = e.student_id
    WHERE e.course_id = %s
    """
    return execute_query(query, (course_id,))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
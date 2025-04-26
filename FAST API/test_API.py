import requests
import json

# Base URL for our API
BASE_URL = "http://localhost:8000"

def test_create_student():
    """Test creating a student"""
    # Test data
    student_data = {
        "first_name": "Test",
        "last_name": "Student",
        "email": "test.student@example.com",
        "date_of_birth": "2000-01-01"
    }
    
    # Make POST request
    response = requests.post(f"{BASE_URL}/students/", json=student_data)
    
    # Check response
    print(f"Create Student Status Code: {response.status_code}")
    print(f"Created Student: {json.dumps(response.json(), indent=2)}")
    
    # Return student ID for further tests
    return response.json()["student_id"]

def test_create_course():
    """Test creating a course"""
    # Test data
    course_data = {
        "course_code": "TEST101",
        "title": "Test Course",
        "description": "A test course",
        "credits": 3
    }
    
    # Make POST request
    response = requests.post(f"{BASE_URL}/courses/", json=course_data)
    
    # Check response
    print(f"Create Course Status Code: {response.status_code}")
    print(f"Created Course: {json.dumps(response.json(), indent=2)}")
    
    # Return course ID for further tests
    return response.json()["course_id"]

def test_create_enrollment(student_id, course_id):
    """Test creating an enrollment"""
    # Test data
    enrollment_data = {
        "student_id": student_id,
        "course_id": course_id,
        "grade": None
    }
    
    # Make POST request
    response = requests.post(f"{BASE_URL}/enrollments/", json=enrollment_data)
    
    # Check response
    print(f"Create Enrollment Status Code: {response.status_code}")
    print(f"Created Enrollment: {json.dumps(response.json(), indent=2)}")
    
    return response.json()["enrollment_id"]

def test_get_student_courses(student_id):
    """Test getting courses for a student"""
    # Make GET request
    response = requests.get(f"{BASE_URL}/students/{student_id}/courses")
    
    # Check response
    print(f"Get Student Courses Status Code: {response.status_code}")
    print(f"Student Courses: {json.dumps(response.json(), indent=2)}")

def test_update_enrollment(enrollment_id, grade="A"):
    """Test updating an enrollment with a grade"""
    # Get current enrollment data
    response = requests.get(f"{BASE_URL}/enrollments/{enrollment_id}")
    enrollment_data = response.json()
    
    # Update grade
    enrollment_data["grade"] = grade
    
    # Make PUT request
    response = requests.put(f"{BASE_URL}/enrollments/{enrollment_id}", json=enrollment_data)
    
    # Check response
    print(f"Update Enrollment Status Code: {response.status_code}")
    print(f"Updated Enrollment: {json.dumps(response.json(), indent=2)}")

def run_all_tests():
    """Run all tests sequentially"""
    print("=== RUNNING API TESTS ===")
    
    # Create a student and course
    student_id = test_create_student()
    course_id = test_create_course()
    
    # Create an enrollment
    enrollment_id = test_create_enrollment(student_id, course_id)
    
    # Get courses for student
    test_get_student_courses(student_id)
    
    # Update enrollment with a grade
    test_update_enrollment(enrollment_id)
    
    print("=== ALL TESTS COMPLETED ===")

if __name__ == "__main__":
    run_all_tests()
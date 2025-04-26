
# Database Projects

This repository contains two database-related projects:
1. **Student Portal API** - A FastAPI-based CRUD application for managing students, courses, and enrollments
2. **Library Management System** - A MySQL database for tracking books, members, and borrowings

## File Structure

```
database-project/
├── FAST API/
│   ├── .env                  # Environment variables for database connection
│   ├── main.py               # Main FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── setup.sql             # SQL setup script for Student Portal database
│   ├── test_API.py           # Test script for API endpoints
│   └── README.md             # Documentation for the Student Portal API
├── Library Management DB/
│   ├── library_schema.sql    # SQL schema and sample data for Library Management
│   └── README.md             # Documentation for the Library Management System
└── README.md                 # Main project documentation (this file)
```

## 1. Student Portal API

A comprehensive CRUD API for managing a student portal system built with FastAPI and MySQL.

### Features

- **Student Management**: Create, read, update, and delete student records
- **Course Management**: Create, read, update, and delete course information
- **Enrollment System**: Track and manage student enrollments in courses
- **Grade Management**: Assign and update grades for enrolled students

### Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL
- **Testing**: Built-in test scripts

### Setup Instructions

#### Prerequisites
- Python 3.7+
- MySQL Server

#### Installation

1. **Clone the repository or extract the ZIP file**

2. **Set up a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   # Log in to MySQL
   mysql -u root -p
   
   # Run the setup script
   source setup.sql
   
   # Exit MySQL
   exit
   ```
   
   Alternatively, you can run the SQL script from the command line:
   ```bash
   mysql -u root -p < setup.sql
   ```

5. **Configure environment variables**
   - Edit the .env file and update the database credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=student_portal
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the API**
   - API is available at: http://localhost:8000
   - Interactive API documentation: http://localhost:8000/docs

### API Endpoints

#### Students
- **POST /students/** - Create a new student
- **GET /students/** - Get all students
- **GET /students/{student_id}** - Get a specific student
- **PUT /students/{student_id}** - Update a student
- **DELETE /students/{student_id}** - Delete a student
- **GET /students/{student_id}/courses** - Get courses for a student

#### Courses
- **POST /courses/** - Create a new course
- **GET /courses/** - Get all courses
- **GET /courses/{course_id}** - Get a specific course
- **PUT /courses/{course_id}** - Update a course
- **DELETE /courses/{course_id}** - Delete a course
- **GET /courses/{course_id}/students** - Get students enrolled in a course

#### Enrollments
- **POST /enrollments/** - Create a new enrollment
- **GET /enrollments/** - Get all enrollments
- **GET /enrollments/{enrollment_id}** - Get a specific enrollment
- **PUT /enrollments/{enrollment_id}** - Update an enrollment (including grades)
- **DELETE /enrollments/{enrollment_id}** - Delete an enrollment

### Testing

The project includes a test script (`test_API.py`) that validates all API endpoints with these functions:
- `test_create_student()` - Tests student creation
- `test_create_course()` - Tests course creation
- `test_create_enrollment()` - Tests enrollment creation
- `test_get_student_courses()` - Tests fetching courses for a student
- `test_update_enrollment()` - Tests updating enrollment information (e.g., grades)

Run all tests with:
```bash
python test_API.py
```

## 2. Library Management System

A MySQL database system designed to manage a library's books, members, and borrowing transactions.

### Features

- **Book Management**: Track books by title, author, ISBN, publication year, and genre
- **Member Management**: Store member information and track membership status
- **Borrowing System**: Record book checkouts, due dates, and returns
- **Data Validation**: Enforce data integrity with constraints and checks

### Database Schema

#### Books Table
```sql
CREATE TABLE Books (
    book_id INT PRIMARY KEY,             -- Unique identifier for each book
    title VARCHAR(100) NOT NULL,         -- Book title (required)
    author VARCHAR(100) NOT NULL,        -- Author name (required)
    isbn VARCHAR(20) UNIQUE,             -- ISBN number (must be unique if provided)
    publication_year INT,                -- Year the book was published
    genre VARCHAR(50),                   -- Book genre/category
    total_copies INT NOT NULL DEFAULT 1, -- Number of copies owned by library
    available_copies INT NOT NULL DEFAULT 1, -- Number of copies currently available
    
    -- Ensure available copies doesn't exceed total copies
    CONSTRAINT check_copies CHECK (available_copies <= total_copies)
);
```

#### Members Table
```sql
CREATE TABLE Members (
    member_id INT PRIMARY KEY,           -- Unique identifier for each member
    first_name VARCHAR(50) NOT NULL,     -- First name (required)
    last_name VARCHAR(50) NOT NULL,      -- Last name (required)
    email VARCHAR(100) UNIQUE NOT NULL,  -- Email address (required and unique)
    phone VARCHAR(20),                   -- Contact phone number
    join_date DATE NOT NULL DEFAULT CURRENT_DATE, -- When the member joined
    membership_status VARCHAR(20) NOT NULL DEFAULT 'Active', -- Current status
    
    -- Limit status values to predefined options
    CONSTRAINT valid_status CHECK (membership_status IN ('Active', 'Expired', 'Suspended'))
);
```

#### Borrowings Table
```sql
CREATE TABLE Borrowings (
    borrowing_id INT PRIMARY KEY,        -- Unique identifier for each borrowing transaction
    book_id INT NOT NULL,                -- Which book was borrowed
    member_id INT NOT NULL,              -- Who borrowed the book
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE, -- When it was borrowed
    due_date DATE NOT NULL,              -- When it should be returned
    return_date DATE,                    -- When it was actually returned (NULL if not yet returned)
    
    -- Create relationships to other tables
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (member_id) REFERENCES Members(member_id),
    
    -- Ensure due date is after borrow date
    CONSTRAINT valid_dates CHECK (due_date >= borrow_date),
    -- Ensure return date (if provided) is after borrow date
    CONSTRAINT valid_return CHECK (return_date IS NULL OR return_date >= borrow_date)
);
```

### Setup Instructions

1. **Log in to MySQL**
   ```bash
   mysql -u root -p
   ```

2. **Create and set up the database**
   ```bash
   # Run the library schema script
   source library_schema.sql
   ```
   
   Alternatively, run from command line:
   ```bash
   mysql -u root -p < library_schema.sql
   ```

3. **Verify the setup**
   ```sql
   USE library_management;
   SHOW TABLES;
   SELECT * FROM Books;
   SELECT * FROM Members;
   SELECT * FROM Borrowings;
   ```

### Sample Queries

Here are some useful queries for working with the library database:

#### 1. Find all currently borrowed books (not returned)
```sql
SELECT b.title, m.first_name, m.last_name, br.borrow_date, br.due_date
FROM Borrowings br
JOIN Books b ON br.book_id = b.book_id
JOIN Members m ON br.member_id = m.member_id
WHERE br.return_date IS NULL;
```

#### 2. Find overdue books
```sql
SELECT b.title, m.first_name, m.last_name, br.borrow_date, br.due_date, 
       DATEDIFF(CURRENT_DATE, br.due_date) AS days_overdue
FROM Borrowings br
JOIN Books b ON br.book_id = b.book_id
JOIN Members m ON br.member_id = m.member_id
WHERE br.return_date IS NULL AND br.due_date < CURRENT_DATE
ORDER BY days_overdue DESC;
```

#### 3. Get book availability
```sql
SELECT book_id, title, available_copies, total_copies,
       (available_copies = 0) AS out_of_stock
FROM Books
ORDER BY available_copies DESC;
```

#### 4. Find borrowing history for a member
```sql
SELECT b.title, br.borrow_date, br.due_date, br.return_date,
       CASE
           WHEN br.return_date IS NULL AND br.due_date >= CURRENT_DATE THEN 'Current'
           WHEN br.return_date IS NULL AND br.due_date < CURRENT_DATE THEN 'Overdue'
           WHEN br.return_date <= br.due_date THEN 'Returned on time'
           ELSE 'Returned late'
       END AS status
FROM Borrowings br
JOIN Books b ON br.book_id = b.book_id
WHERE br.member_id = 101  -- Replace with desired member_id
ORDER BY br.borrow_date DESC;
```

## Common Operations and Advanced Usage

### Student Portal API

#### Creating a New Student
```bash
curl -X POST "http://localhost:8000/students/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane.doe@example.com", "major": "Computer Science"}'
```

#### Enrolling a Student in a Course
```bash
curl -X POST "http://localhost:8000/enrollments/" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "course_id": 1, "enrollment_date": "2025-01-15"}'
```

#### Updating a Grade
```bash
curl -X PUT "http://localhost:8000/enrollments/1" \
  -H "Content-Type: application/json" \
  -d '{"grade": "A"}'
```

### Library Management System

#### Adding a New Book
```sql
INSERT INTO Books (book_id, title, author, isbn, publication_year, genre, total_copies, available_copies)
VALUES (6, 'Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', '9780747532699', 1997, 'Fantasy', 5, 5);
```

#### Registering a New Member
```sql
INSERT INTO Members (member_id, first_name, last_name, email, phone)
VALUES (106, 'Alice', 'Johnson', 'alice.j@example.com', '555-4567');
```

#### Recording a Book Checkout
```sql
-- First, make sure the book is available
SET @book_id = 3;

-- Check if book is available
SELECT IF(available_copies > 0, 'Available', 'Not Available') AS status
FROM Books
WHERE book_id = @book_id;

-- If available, create the borrowing record
INSERT INTO Borrowings (borrowing_id, book_id, member_id, borrow_date, due_date)
VALUES (1006, @book_id, 102, CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 14 DAY));

-- Update the available copies
UPDATE Books
SET available_copies = available_copies - 1
WHERE book_id = @book_id;
```

#### Recording a Book Return
```sql
-- First, identify the borrowing record
SET @borrowing_id = 1002;
SET @book_id = (SELECT book_id FROM Borrowings WHERE borrowing_id = @borrowing_id);

-- Update the borrowing record with the return date
UPDATE Borrowings
SET return_date = CURRENT_DATE
WHERE borrowing_id = @borrowing_id;

-- Update the available copies in the Books table
UPDATE Books
SET available_copies = available_copies + 1
WHERE book_id = @book_id;
```

## Troubleshooting

### Student Portal API

1. **Database Connection Issues**
   - Verify your `.env` file has correct credentials
   - Ensure MySQL server is running
   - Check if the database exists: `SHOW DATABASES;`

2. **API Not Starting**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check for Python version compatibility (3.7+)
   - Look for error messages in the terminal

3. **Endpoint Errors**
   - Verify your request format matches the API specifications
   - Check the API documentation at `/docs` for correct parameters

### Library Management System

1. **Constraint Violations**
   - Ensure available copies don't exceed total copies
   - Verify membership status is one of: 'Active', 'Expired', 'Suspended'
   - Ensure due dates are after borrow dates

2. **Foreign Key Violations**
   - Make sure referenced book_id exists in Books table before adding borrowing records
   - Make sure referenced member_id exists in Members table before adding borrowing records

## Contributing

Feel free to submit issues or pull requests to improve either projects.




-- First, create the library database
CREATE DATABASE library_management;

-- Connect to the library database
USE library_management;

-- Books table to store all books in the library
CREATE TABLE Books (
    book_id INT PRIMARY KEY, -- Unique identifier for each book
    title VARCHAR(100) NOT NULL, -- Book title (required)
    author VARCHAR(100) NOT NULL, -- Author name (required)
    isbn VARCHAR(20) UNIQUE, -- ISBN number (must be unique if provided)
    publication_year INT, -- Year the book was published
    genre VARCHAR(50), -- Book genre/category
    total_copies INT NOT NULL DEFAULT 1, -- Number of copies owned by library
    available_copies INT NOT NULL DEFAULT 1, -- Number of copies currently available
    
    -- Ensure available copies doesn't exceed total copies
    CONSTRAINT check_copies CHECK (available_copies <= total_copies)
);

-- Members table to store information about library members
CREATE TABLE Members (
    member_id INT PRIMARY KEY, -- Unique identifier for each member
    first_name VARCHAR(50) NOT NULL, -- First name (required)
    last_name VARCHAR(50) NOT NULL, -- Last name (required)
    email VARCHAR(100) UNIQUE NOT NULL, -- Email address (required and unique)
    phone VARCHAR(20), -- Contact phone number
    join_date DATE NOT NULL DEFAULT CURRENT_DATE, -- When the member joined
    membership_status VARCHAR(20) NOT NULL DEFAULT 'Active', -- Current status
    
    -- Limit status values to predefined options
    CONSTRAINT valid_status CHECK (membership_status IN ('Active', 'Expired', 'Suspended'))
);

-- Borrowings table to track which member borrowed which book and when
CREATE TABLE Borrowings (
    borrowing_id INT PRIMARY KEY, -- Unique identifier for each borrowing transaction
    book_id INT NOT NULL, -- Which book was borrowed
    member_id INT NOT NULL, -- Who borrowed the book
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE, -- When it was borrowed
    due_date DATE NOT NULL, -- When it should be returned
    return_date DATE, -- When it was actually returned (NULL if not yet returned)
    
    -- Create relationships to other tables
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (member_id) REFERENCES Members(member_id),
    
    -- Ensure due date is after borrow date
    CONSTRAINT valid_dates CHECK (due_date >= borrow_date),
    -- Ensure return date (if provided) is after borrow date
    CONSTRAINT valid_return CHECK (return_date IS NULL OR return_date >= borrow_date)
);

-- Insert sample data into Books table
INSERT INTO Books (book_id, title, author, isbn, publication_year, genre, total_copies, available_copies)
VALUES
    (1, 'To Kill a Mockingbird', 'Harper Lee', '9780061120084', 1960, 'Fiction', 3, 2),
    (2, '1984', 'George Orwell', '9780451524935', 1949, 'Dystopian', 2, 1),
    (3, 'The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 1925, 'Classic', 4, 4),
    (4, 'Pride and Prejudice', 'Jane Austen', '9780141439518', 1813, 'Romance', 2, 1),
    (5, 'The Hobbit', 'J.R.R. Tolkien', '9780547928227', 1937, 'Fantasy', 3, 3);

-- Insert sample data into Members table
INSERT INTO Members (member_id, first_name, last_name, email, phone, join_date, membership_status)
VALUES
    (101, 'John', 'Smith', 'john.smith@email.com', '555-1234', '2023-01-15', 'Active'),
    (102, 'Sarah', 'Johnson', 'sarah.j@email.com', '555-5678', '2023-03-22', 'Active'),
    (103, 'Michael', 'Brown', 'mbrown@email.com', '555-9012', '2022-11-05', 'Active'),
    (104, 'Emma', 'Davis', 'emma.davis@email.com', '555-3456', '2023-02-18', 'Suspended'),
    (105, 'David', 'Wilson', 'dwilson@email.com', '555-7890', '2022-08-30', 'Expired');

-- Insert sample data into Borrowings table
INSERT INTO Borrowings (borrowing_id, book_id, member_id, borrow_date, due_date, return_date)
VALUES
    (1001, 1, 101, '2024-03-10', '2024-03-24', '2024-03-22'), -- Returned on time
    (1002, 2, 102, '2024-03-15', '2024-03-29', NULL), -- Not yet returned
    (1003, 4, 103, '2024-03-18', '2024-04-01', NULL), -- Not yet returned
    (1004, 1, 105, '2024-02-25', '2024-03-10', '2024-03-12'), -- Returned late
    (1005, 5, 101, '2024-01-05', '2024-01-19', '2024-01-15'); -- Returned early
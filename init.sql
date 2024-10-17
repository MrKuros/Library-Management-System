-- Create the database
CREATE DATABASE IF NOT EXISTS library_db;

-- Use the created database
USE library_db;

-- Create the members table
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    outstanding_debt DECIMAL(10, 2) DEFAULT 0.00
);

-- Create the books table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    authors VARCHAR(255) NOT NULL,
    rating DECIMAL(3, 2),
    publisher VARCHAR(100),
    stock INT DEFAULT 0
);

-- Create the transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT ,
    book_id INT ,
    issue_date DATE NOT NULL,
    return_date DATE,
    fee DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);


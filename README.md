# Library Management Web Application

## Overview

This is a Flask-based web application for managing a local library. It tracks books, members, book issuances, returns, and overdue fees. The application also integrates with the Frappe API for importing book data, including book ratings.

## Features

- **Add Members**: Easily add new members to the library.
- **Add Books**: Add new books with details such as title, authors, and ratings.
- **Issue Books**: Issue books to members and keep track of issue dates.
- **Return Books**: Allow members to return books and calculate overdue fees if applicable.
- **View Reports**: Check lists of members, books, issued books, and overdue items.
- **Integration with Frappe API**: Import book data, including ratings, from Frappe.

## Installation

To install the Library Management Web Application, follow these steps:

1. **Clone the Repository**
   - Clone the repository:
     ```bash
     git clone https://github.com/yourusername/library-management-app.git
     ```
     
2. **Install the Dependencies**
   - Navigate into the project directory:
     ```bash
     cd library-management-app
     ```
   - Create a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows, use venv\Scripts\activate
     ```
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Set Up the Database**
   - Initialize the database:
     ```bash
     flask db init
     flask db migrate
     flask db upgrade
     ```

## Configuration

Before using the application, configure your environment variables:

1. **Create a `.env` file** in the project root:
   ```bash
   FLASK_APP=app
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   SQLALCHEMY_DATABASE_URI=sqlite:///library.db
   FRAPPE_API_URL=https://example.com/api/resource/Book
   FRAPPE_API_KEY=your_frappe_api_key
## Usage

Once installed and configured, use the application as follows:

## Run the Application

Start the Flask development server:

```bash
python3 app.py
```
## API Documentation

### Add a New Member

- **URL:** `/member/add`
- **Method:** `POST`
- **Data:**
  - `name`: string (required)
  - `email`: string (required)

### Add a New Book

- **URL:** `/book/add`
- **Method:** `POST`
- **Data:**
  - `title`: string (required)
  - `authors`: string (required)
  - `rating`: float (required)
  - `stock`: integer (required)

### Issue a Book

- **URL:** `/issue`
- **Method:** `POST`
- **Data:**
  - `member_id`: integer (required)
  - `book_id`: integer (required)
  - `issue_date`: datetime (optional, defaults to current datetime)

### Return a Book

- **URL:** `/return_book/<issue_id>`
- **Method:** `POST`


# Library Management System

A sample Library Management System with SQL schema, Python backend, and frontend UI.

## What is included

- `schema.sql`: MySQL/MariaDB-compatible database schema, stored procedures, and triggers.
- `sample_data.sql`: Initial sample rows for Member, Author, Book, Issue, and Staff.
- `app.py`: Flask backend API using SQLite for quick setup.
- `static/index.html`: Frontend UI for book browsing, issuing, returning, and reports.
- `static/main.js`: Frontend fetch and page logic.
- `static/style.css`: Simple styling.
- `requirements.txt`: Python dependency.

## Setup

1. Create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the Flask app:

```bash
python app.py
```

3. Visit `http://127.0.0.1:5000` in your browser.

## SQL Notes

- The MySQL/MariaDB-style `schema.sql` contains the database tables, triggers, and stored procedures as requested.
- The Flask backend uses `library.db` with the same tables and also includes SQLite-compatible triggers.

## API Endpoints

- `GET /api/books`
- `GET /api/authors`
- `GET /api/members`
- `GET /api/issues`
- `GET /api/fines`
- `GET /api/staff`
- `GET /api/books/author?name=Author+Name`
- `GET /api/books/never-issued`
- `GET /api/reports/categories`
- `GET /api/reports/over-average`
- `GET /api/reports/member-more-than/<member_id>`
- `GET /api/reports/books-left-join`
- `POST /api/issue`
- `POST /api/return`
- `POST /api/fine`

## Example requests

Issue a book:

```bash
curl -X POST http://127.0.0.1:5000/api/issue \
  -H 'Content-Type: application/json' \
  -d '{"member_id": 1, "book_id": 3, "issue_date": "2025-08-01"}'
```

Return a book:

```bash
curl -X POST http://127.0.0.1:5000/api/return \
  -H 'Content-Type: application/json' \
  -d '{"issue_id": 1002, "return_date": "2025-08-25"}'
```

Calculate fines:

```bash
curl -X POST http://127.0.0.1:5000/api/fine \
  -H 'Content-Type: application/json' \
  -d '{"member_id": 2}'
```

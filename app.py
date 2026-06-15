import os
import sqlite3
from datetime import date, datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, abort

app = Flask(__name__, static_folder='static', static_url_path='')
DB_PATH = 'library.db'

SQLITE_INIT = '''
CREATE TABLE IF NOT EXISTS Member (
    member_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    membership_date DATE
);

CREATE TABLE IF NOT EXISTS Author (
    author_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Book (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INTEGER,
    category TEXT,
    price REAL,
    availability TEXT DEFAULT 'Yes',
    FOREIGN KEY(author_id) REFERENCES Author(author_id)
);

CREATE TABLE IF NOT EXISTS Issue (
    issue_id INTEGER PRIMARY KEY,
    member_id INTEGER,
    book_id INTEGER,
    issue_date DATE,
    return_date DATE,
    FOREIGN KEY(member_id) REFERENCES Member(member_id),
    FOREIGN KEY(book_id) REFERENCES Book(book_id)
);

CREATE TABLE IF NOT EXISTS Fine (
    fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    amount REAL,
    paid_status TEXT,
    FOREIGN KEY(member_id) REFERENCES Member(member_id)
);

CREATE TABLE IF NOT EXISTS Staff (
    staff_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT
);

CREATE TRIGGER IF NOT EXISTS trg_issue_book
AFTER INSERT ON Issue
BEGIN
    UPDATE Book
    SET availability = 'No'
    WHERE book_id = NEW.book_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_return_book
AFTER UPDATE ON Issue
WHEN NEW.return_date IS NOT NULL
BEGIN
    UPDATE Book
    SET availability = 'Yes'
    WHERE book_id = NEW.book_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_calculate_fine
AFTER UPDATE ON Issue
WHEN NEW.return_date IS NOT NULL
    AND DATE(NEW.return_date) > DATE(NEW.issue_date, '+15 days')
BEGIN
    INSERT INTO Fine(member_id, amount, paid_status)
    VALUES(
        NEW.member_id,
        (julianday(NEW.return_date) - julianday(DATE(NEW.issue_date, '+15 days'))) * 5,
        'Unpaid'
    );
END;
'''

SAMPLE_DATA = [
    ('INSERT OR IGNORE INTO Member(member_id, name, phone, membership_date) VALUES (?, ?, ?, ?);',
        (1, 'Alice Johnson', '555-1234', '2025-01-10')),
    ('INSERT OR IGNORE INTO Member(member_id, name, phone, membership_date) VALUES (?, ?, ?, ?);',
        (2, 'Bob Smith', '555-2345', '2025-03-05')),
    ('INSERT OR IGNORE INTO Member(member_id, name, phone, membership_date) VALUES (?, ?, ?, ?);',
        (3, 'Carla Green', '555-3456', '2025-05-20')),
    ('INSERT OR IGNORE INTO Author(author_id, name) VALUES (?, ?);', (1, 'Jane Austen')),
    ('INSERT OR IGNORE INTO Author(author_id, name) VALUES (?, ?);', (2, 'Mark Twain')),
    ('INSERT OR IGNORE INTO Author(author_id, name) VALUES (?, ?);', (3, 'George Orwell')),
    ('INSERT OR IGNORE INTO Book(book_id, title, author_id, category, price, availability) VALUES (?, ?, ?, ?, ?, ?);',
        (1, 'Pride and Prejudice', 1, 'Fiction', 220.00, 'Yes')),
    ('INSERT OR IGNORE INTO Book(book_id, title, author_id, category, price, availability) VALUES (?, ?, ?, ?, ?, ?);',
        (2, 'Adventures of Huckleberry Finn', 2, 'Adventure', 180.00, 'Yes')),
    ('INSERT OR IGNORE INTO Book(book_id, title, author_id, category, price, availability) VALUES (?, ?, ?, ?, ?, ?);',
        (3, '1984', 3, 'Dystopian', 250.00, 'Yes')),
    ('INSERT OR IGNORE INTO Book(book_id, title, author_id, category, price, availability) VALUES (?, ?, ?, ?, ?, ?);',
        (4, 'Emma', 1, 'Fiction', 200.00, 'Yes')),
    ('INSERT OR IGNORE INTO Issue(issue_id, member_id, book_id, issue_date, return_date) VALUES (?, ?, ?, ?, ?);',
        (1001, 1, 1, '2025-07-01', '2025-07-12')),
    ('INSERT OR IGNORE INTO Issue(issue_id, member_id, book_id, issue_date, return_date) VALUES (?, ?, ?, ?, ?);',
        (1002, 2, 2, '2025-07-03', NULL)),
    ('INSERT OR IGNORE INTO Staff(staff_id, name, role) VALUES (?, ?, ?);', (1, 'Diana Peters', 'Librarian')),
    ('INSERT OR IGNORE INTO Staff(staff_id, name, role) VALUES (?, ?, ?);', (2, 'Eric Mills', 'Assistant'))
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if os.path.exists(DB_PATH):
        return
    with get_connection() as conn:
        conn.executescript(SQLITE_INIT)
        for statement, params in SAMPLE_DATA:
            conn.execute(statement, params)
        conn.commit()


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


def query_sql(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return [row_to_dict(row) for row in cur.fetchall()]


def execute_sql(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify(query_sql('SELECT * FROM Book;'))

@app.route('/api/authors', methods=['GET'])
def get_authors():
    return jsonify(query_sql('SELECT * FROM Author;'))

@app.route('/api/members', methods=['GET'])
def get_members():
    return jsonify(query_sql('SELECT * FROM Member;'))

@app.route('/api/issues', methods=['GET'])
def get_issues():
    return jsonify(query_sql('SELECT * FROM Issue;'))

@app.route('/api/fines', methods=['GET'])
def get_fines():
    return jsonify(query_sql('SELECT * FROM Fine;'))

@app.route('/api/staff', methods=['GET'])
def get_staff():
    return jsonify(query_sql('SELECT * FROM Staff;'))

@app.route('/api/books/author', methods=['GET'])
def books_by_author():
    name = request.args.get('name', '')
    if not name:
        return abort(400, 'Author name is required')
    sql = '''SELECT b.* FROM Book b JOIN Author a ON b.author_id = a.author_id WHERE a.name = ?;'''
    return jsonify(query_sql(sql, (name,)))

@app.route('/api/books/never-issued', methods=['GET'])
def books_never_issued():
    sql = '''SELECT * FROM Book b WHERE NOT EXISTS (SELECT 1 FROM Issue i WHERE i.book_id = b.book_id);'''
    return jsonify(query_sql(sql))

@app.route('/api/reports/categories', methods=['GET'])
def category_report():
    sql = 'SELECT category, COUNT(*) AS total_books FROM Book GROUP BY category;'
    return jsonify(query_sql(sql))

@app.route('/api/reports/over-average', methods=['GET'])
def books_over_average():
    sql = '''SELECT * FROM Book WHERE price > (SELECT AVG(price) FROM Book);'''
    return jsonify(query_sql(sql))

@app.route('/api/reports/member-more-than/<int:member_id>', methods=['GET'])
def members_borrowed_more(member_id):
    sql = '''SELECT m.member_id, m.name FROM Member m WHERE (
        SELECT COUNT(*) FROM Issue i WHERE i.member_id = m.member_id
    ) > (
        SELECT COUNT(*) FROM Issue WHERE member_id = ?
    );'''
    return jsonify(query_sql(sql, (member_id,)))

@app.route('/api/reports/books-left-join', methods=['GET'])
def books_left_join():
    sql = '''SELECT b.book_id, b.title, i.issue_id FROM Book b LEFT JOIN Issue i ON b.book_id = i.book_id;'''
    return jsonify(query_sql(sql))

@app.route('/api/issue', methods=['POST'])
def issue_book():
    data = request.get_json() or {}
    member_id = data.get('member_id')
    book_id = data.get('book_id')
    issue_date = data.get('issue_date') or date.today().isoformat()
    if not member_id or not book_id:
        return abort(400, 'member_id and book_id are required')
    available = query_sql('SELECT availability FROM Book WHERE book_id = ?;', (book_id,))
    if not available or available[0]['availability'] != 'Yes':
        return abort(400, 'Book is not available for issue')
    issue_id = execute_sql('INSERT INTO Issue(member_id, book_id, issue_date) VALUES (?, ?, ?);',
                          (member_id, book_id, issue_date))
    execute_sql('UPDATE Book SET availability = ? WHERE book_id = ?;', ('No', book_id))
    return jsonify({'status': 'success', 'issue_id': issue_id}), 201

@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.get_json() or {}
    issue_id = data.get('issue_id')
    return_date = data.get('return_date') or date.today().isoformat()
    if not issue_id:
        return abort(400, 'issue_id is required')
    issue = query_sql('SELECT * FROM Issue WHERE issue_id = ?;', (issue_id,))
    if not issue:
        return abort(404, 'Issue record not found')
    execute_sql('UPDATE Issue SET return_date = ? WHERE issue_id = ?;', (return_date, issue_id))
    issue_record = issue[0]
    execute_sql('UPDATE Book SET availability = ? WHERE book_id = ?;', ('Yes', issue_record['book_id']))
    if datetime.fromisoformat(return_date).date() > datetime.fromisoformat(issue_record['issue_date']).date() + timedelta(days=15):
        overdue_days = (datetime.fromisoformat(return_date).date() - (datetime.fromisoformat(issue_record['issue_date']).date() + timedelta(days=15))).days
        amount = overdue_days * 5
        execute_sql('INSERT INTO Fine(member_id, amount, paid_status) VALUES (?, ?, ?);',
                    (issue_record['member_id'], amount, 'Unpaid'))
    return jsonify({'status': 'returned', 'issue_id': issue_id})

@app.route('/api/fine', methods=['POST'])
def calculate_fine():
    data = request.get_json() or {}
    member_id = data.get('member_id')
    if not member_id:
        return abort(400, 'member_id is required')
    issues = query_sql('SELECT * FROM Issue WHERE member_id = ? AND return_date IS NOT NULL;', (member_id,))
    total = 0
    inserted = 0
    for issue in issues:
        issue_date = datetime.fromisoformat(issue['issue_date']).date()
        return_date = datetime.fromisoformat(issue['return_date']).date()
        due_date = issue_date + timedelta(days=15)
        if return_date > due_date:
            amount = (return_date - due_date).days * 5
            execute_sql('INSERT INTO Fine(member_id, amount, paid_status) VALUES (?, ?, ?);',
                        (member_id, amount, 'Unpaid'))
            total += amount
            inserted += 1
    return jsonify({'member_id': member_id, 'inserted_fines': inserted, 'total_amount': total})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

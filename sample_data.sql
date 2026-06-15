USE library_management;

INSERT INTO Member(member_id, name, phone, membership_date) VALUES
(1, 'Alice Johnson', '555-1234', '2025-01-10'),
(2, 'Bob Smith', '555-2345', '2025-03-05'),
(3, 'Carla Green', '555-3456', '2025-05-20');

INSERT INTO Author(author_id, name) VALUES
(1, 'Jane Austen'),
(2, 'Mark Twain'),
(3, 'George Orwell');

INSERT INTO Book(book_id, title, author_id, category, price, availability) VALUES
(1, 'Pride and Prejudice', 1, 'Fiction', 220.00, 'Yes'),
(2, 'Adventures of Huckleberry Finn', 2, 'Adventure', 180.00, 'Yes'),
(3, '1984', 3, 'Dystopian', 250.00, 'Yes'),
(4, 'Emma', 1, 'Fiction', 200.00, 'Yes');

INSERT INTO Issue(issue_id, member_id, book_id, issue_date, return_date) VALUES
(1001, 1, 1, '2025-07-01', '2025-07-12'),
(1002, 2, 2, '2025-07-03', NULL);

INSERT INTO Staff(staff_id, name, role) VALUES
(1, 'Diana Peters', 'Librarian'),
(2, 'Eric Mills', 'Assistant');

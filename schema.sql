-- Library Management System SQL Schema for MySQL/MariaDB

CREATE DATABASE IF NOT EXISTS library_management;
USE library_management;

CREATE TABLE IF NOT EXISTS Member (
    member_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    membership_date DATE
);

CREATE TABLE IF NOT EXISTS Author (
    author_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Book (
    book_id INT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    author_id INT,
    category VARCHAR(50),
    price DECIMAL(10,2),
    availability VARCHAR(10) DEFAULT 'Yes',
    FOREIGN KEY (author_id) REFERENCES Author(author_id)
);

CREATE TABLE IF NOT EXISTS Issue (
    issue_id INT PRIMARY KEY,
    member_id INT,
    book_id INT,
    issue_date DATE,
    return_date DATE,
    FOREIGN KEY (member_id) REFERENCES Member(member_id),
    FOREIGN KEY (book_id) REFERENCES Book(book_id)
);

CREATE TABLE IF NOT EXISTS Fine (
    fine_id INT PRIMARY KEY,
    member_id INT,
    amount DECIMAL(10,2),
    paid_status VARCHAR(10),
    FOREIGN KEY (member_id) REFERENCES Member(member_id)
);

CREATE TABLE IF NOT EXISTS Staff (
    staff_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(50)
);

DELIMITER //
CREATE PROCEDURE IssueBook(
    IN p_issue_id INT,
    IN p_member_id INT,
    IN p_book_id INT,
    IN p_issue_date DATE
)
BEGIN
    INSERT INTO Issue(issue_id, member_id, book_id, issue_date)
    VALUES(p_issue_id, p_member_id, p_book_id, p_issue_date);
    UPDATE Book
    SET availability = 'No'
    WHERE book_id = p_book_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CalculateFine(
    IN p_member_id INT
)
BEGIN
    DECLARE overdue_days INT;
    DECLARE fine_amount DECIMAL(10,2);
    SELECT DATEDIFF(CURDATE(), return_date)
    INTO overdue_days
    FROM Issue
    WHERE member_id = p_member_id
      AND return_date < CURDATE()
    LIMIT 1;
    SET fine_amount = GREATEST(overdue_days * 5, 0);
    INSERT INTO Fine(fine_id, member_id, amount, paid_status)
    VALUES((SELECT COALESCE(MAX(fine_id), 0) + 1 FROM Fine), p_member_id, fine_amount, 'Unpaid');
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_issue_book
AFTER INSERT ON Issue
FOR EACH ROW
BEGIN
    UPDATE Book
    SET availability = 'No'
    WHERE book_id = NEW.book_id;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_return_book
AFTER UPDATE ON Issue
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL THEN
        UPDATE Book
        SET availability = 'Yes'
        WHERE book_id = NEW.book_id;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_calculate_fine
AFTER UPDATE ON Issue
FOR EACH ROW
BEGIN
    IF NEW.return_date > DATE_ADD(NEW.issue_date, INTERVAL 15 DAY) THEN
        INSERT INTO Fine(fine_id, member_id, amount, paid_status)
        VALUES(
            (SELECT COALESCE(MAX(fine_id), 0) + 1 FROM Fine),
            NEW.member_id,
            DATEDIFF(NEW.return_date, DATE_ADD(NEW.issue_date, INTERVAL 15 DAY)) * 5,
            'Unpaid'
        );
    END IF;
END //
DELIMITER ;

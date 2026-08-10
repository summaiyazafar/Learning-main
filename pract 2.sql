CREATE TABLE employee2(
	employee_id INT PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	position VARCHAR(50),
	department VARCHAR(50),
	hire_date DATE,
	salary NUMERIC(10,2)
);
SELECT * FROM employee2;

INSERT INTO employee2(employee_id, name, position, department, hire_date, salary)
VALUES
(01, 'Ali', 'Data Analyst', 'Data Science', '2025-05-15', 55000.00),
(02, 'Yousaf', 'Software Engineer', 'IT', '2025-05-30', 60000.00),
(03, 'Subhan', 'HR Manager', 'HR', '2025-08-15', 59000.00),
(04, 'Irtaza', 'Marketing Specialist', 'Marketing', '2025-06-25', 75000.00),
(05, 'Hasan', 'Sales Executive', 'Sales', '2024-06-14', 90000.00);

DELETE FROM employee2
WHERE employee_id= 04;

ALTER TABLE employee2
DROP COLUMN salary;

DROP TABLE IF EXISTS employee2;

DROP TABLE IF EXISTS Company2;










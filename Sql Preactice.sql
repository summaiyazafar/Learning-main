CREATE TABLE employee(
	employee_id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	position VARCHAR(50),
	department VARCHAR(50),
	hire_date DATE,
	salary NUMERIC(10,2)
);
SELECT * FROM employee;

INSERT INTO employee(name, position, department, hire_date, salary)
VALUES
('Ali', 'Data Analyst', 'Data Science', '2025-05-15', 55000.00),
('Yousaf', 'Software Engineer', 'IT', '2025-05-30', 60000.00),
('Subhan', 'HR Manager', 'HR', '2025-08-15', 59000.00),
('Irtaza', 'Marketing Specialist', 'Marketing', '2025-06-25', 75000.00),
('Hasan', 'Sales Executive', 'Sales', '2024-06-14', 90000.00);

ALTER TABLE employee
RENAME COLUMN salary TO Salary;

TRUNCATE TABLE employee;

TRUNCATE TABLE employee RESTART IDENTITY;
		
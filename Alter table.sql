--Drop the table if it already exists
Drop TABLE IF EXISTS users2;

--Create the users table
CREATE TABLE IF NOT EXISTS users2(
		user_id SERIAL PRIMARY KEY,
		username VARCHAR(50) NOT NULL,
		email VARCHAR(100) NOT NULL,
		age INT,
		city VARCHAR(50)
);

SELECT * FROM users2;

--Insert 5 sample users into the users table
INSERT INTO users2 (username, email,age, city) VALUES
('Ali', 'ali@gmail.com', 22, 'Taxila'),
('Hasan', 'hasan@gmail.com', 24, 'Rawalpindi'),
('Ahsan', 'ahsan@gmail.com', 30, 'Lahore'),
('Ziya', 'ziya@gmail.com', 26, 'Karachi');

SELECT *
FROM users2
ORDER BY user_id ASC;

UPDATE users2
SET age= age+1
WHERE email LIKE '%gmail.com';

DELETE FROM users2 WHERE user_id=4;

-- To Rename the username to fullname
ALTER TABLE users2
RENAME COLUMN username TO fullname;

select * from users2 order by user_id asc;

-- To change the age column's data type from INT to SMALLINT
ALTER TABLE users2
ALTER COLUMN age TYPE SMALLINT;













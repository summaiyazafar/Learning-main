CREATE TABLE users(
		user_id INT PRIMARY KEY,
		name VARCHAR(50) NOT NULL,
		email VARCHAR(100) UNIQUE,
		age INTEGER CHECK (age >= 18),
		reg_date TIMESTAM
)
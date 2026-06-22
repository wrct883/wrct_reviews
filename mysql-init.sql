-- Create the user if it doesn't exist, and give them the password
CREATE USER IF NOT EXISTS 'wrct'@'%' IDENTIFIED BY 'freeform';

-- Give the user full permissions on your specific database
GRANT ALL PRIVILEGES ON *.* TO 'wrct'@'%';

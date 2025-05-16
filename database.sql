CREATE DATABASE student_auth;
USE student_auth;

-- Create Users Table
CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department VARCHAR(255) DEFAULT 'Unknown',
    cgpa FLOAT DEFAULT 0.0,
    password_hash VARCHAR(255) NOT NULL,
    otp_secret VARCHAR(32) DEFAULT NULL,
    PRIMARY KEY (user_id)
);

-- Create OTP Table (Stores OTPs for verification)
CREATE TABLE otps (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


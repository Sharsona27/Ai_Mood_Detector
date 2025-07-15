-- 1. Create the database
CREATE DATABASE IF NOT EXISTS mood_detector_db;

-- 2. Use the database
USE mood_detector_db;

-- 3. Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create moods table
CREATE TABLE IF NOT EXISTS moods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    mood VARCHAR(50),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

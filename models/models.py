# models/models.py

from backend.db import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # User Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)

    # Mood Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            mood VARCHAR(50),
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

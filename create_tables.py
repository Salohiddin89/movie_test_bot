import sqlite3


def create_tables():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        first_name TEXT,
        last_name TEXT,
        username TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        year INTEGER,
        duration INTEGER,
        genre TEXT,
        rating REAL,
        language TEXT,
        file_id TEXT
    );
    """)

    conn.commit()
    conn.close()

import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

def create_tables(db_path):
    """Create the database tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS passengers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        second_name TEXT,
                        last_name TEXT,
                        phone_number TEXT,
                        email_address TEXT,
                        address TEXT)''')
    conn.commit()
    conn.close()


def add_passenger(db_path, first_name, second_name, last_name, phone_number, email_address, address):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            second_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email_address TEXT NOT NULL,
            address TEXT NOT NULL
        )''')
        cursor.execute('''INSERT INTO passengers (first_name, second_name, last_name, phone_number, email_address, address)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (first_name, second_name, last_name, phone_number, email_address, address))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")


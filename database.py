import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

class Customer:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def save_to_db(self, db_path):
        """Save the customer object to the database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customer (username, email, password)
                VALUES (?, ?, ?)
            ''', (self.username, self.email, self.password))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError as e:
            print(f"Error saving customer to the database: {e}")
            raise ValueError("Username or email already exists.")


def create_tables(db_path):
    """Create the database tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS customer (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        password TEXT,
                        email TEXT)''')
    conn.commit()
    conn.close()

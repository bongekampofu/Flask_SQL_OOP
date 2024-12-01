import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

# Define the Customer class
class Customer:
    def __init__(self, first_name, second_name, last_name, phone_number, email_address, address):
        self.first_name = first_name
        self.second_name = second_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email_address = email_address
        self.address = address

    def save_to_db(self, db_path):
        """Save the customer object to the database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Ensure the passengers table exists
            cursor.execute('''CREATE TABLE IF NOT EXISTS passengers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                second_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email_address TEXT NOT NULL,
                address TEXT NOT NULL
            )''')
            # Insert customer data# Customer class data is insert in the passengers table
            cursor.execute('''INSERT INTO passengers (first_name, second_name, last_name, phone_number, email_address, address)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (self.first_name, self.second_name, self.last_name, self.phone_number, self.email_address, self.address))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Database Error: {e}")
            raise

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


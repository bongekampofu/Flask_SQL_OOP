from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
import json
import os
import sqlite3


# Define the database path
DATABASE_PATH = 'C:\\Users\\Bongeka.Mpofu\\DB Browser for SQLite\\flight.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

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
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Create the passengers table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS passengers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                second_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email_address TEXT NOT NULL,
                address TEXT NOT NULL
            )''')
            # Insert customer data into the passengers table
            cursor.execute('''INSERT INTO passengers (first_name, second_name, last_name, phone_number, email_address, address)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (self.first_name, self.second_name, self.last_name, self.phone_number, self.email_address, self.address))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Error: {e}")

@app.route('/')
def index():
    return render_template("index.html")

def init_db():
    if not os.path.exists(DATABASE_PATH):
        with app.app_context():
            # Assuming you have a function in `database` module that creates tables
            database.create_tables(DATABASE_PATH)
            print("Database created successfully.")
    else:
        print("Database already exists.")

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        second_name = request.form.get('second_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        email_address = request.form.get('email_address')
        address = request.form.get('address')

        print(f"Received Data: {first_name}, {second_name}, {last_name}, {phone_number}, {email_address}, {address}")

        try:
            database.add_passenger(DATABASE_PATH, first_name, second_name, last_name, phone_number, email_address, address)
            print("Database insertion attempted.")
        except Exception as e:
            print(f"Error in database insertion: {e}")

        return redirect(url_for('index'))
    return render_template('Customer_details.html')


@app.route('/save_customer_data', methods=['POST'])
def save_customer_data():
    try:
        # Get JSON data from the request
        data = request.get_json()
        print("Request received:", data)

        # Validate JSON data
        if not all([data.get('first_name'), data.get('second_name'), data.get('last_name'),
                    data.get('phone_number'), data.get('email_address'), data.get('address')]):
            return jsonify({"error": "All fields are required!"}), 400

        # Create a Customer object
        customer = Customer(
            first_name=data.get('first_name'),
            second_name=data.get('second_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            email_address=data.get('email_address'),
            address=data.get('address')
        )

        # Save the customer object to the database
        customer.save_to_db(DATABASE_PATH)

        return jsonify({"message": "Customer data successfully saved to the database!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

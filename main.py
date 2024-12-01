from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from database import Customer, create_tables

# Define the database path
DATABASE_PATH = 'C:\\Users\\Bongeka.Mpofu\\DB Browser for SQLite\\flight.db'

# Ensure the database tables are created
create_tables(DATABASE_PATH)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/customer', methods=['GET', 'POST'])
def customer():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        second_name = request.form.get('second_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        email_address = request.form.get('email_address')
        address = request.form.get('address')

        # Create a Customer object and save it to the database
        customer = Customer(first_name, second_name, last_name, phone_number, email_address, address)
        customer.save_to_db(DATABASE_PATH)

        flash("Customer data saved successfully!", "success")
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

        # Create a Customer object and save it to the database
        customer = Customer(
            first_name=data.get('first_name'),
            second_name=data.get('second_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            email_address=data.get('email_address'),
            address=data.get('address')
        )
        customer.save_to_db(DATABASE_PATH)

        return jsonify({"message": "Customer data successfully saved to the database!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, flash, session, render_template, redirect
import cgi, os
from flask import Flask, render_template, url_for, redirect, request
from flask import session as login_session
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
import sqlite3
from decimal import Decimal
from flask_admin import Admin, form
from flask import Flask, flash, request, redirect, url_for
import requests
import json
from typing import Union, Type
import os

#from cs50 import SQL
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
#from helpers import apology, passwordValid
#from flask_login import login_required, passwordValid
from flask_login import login_required
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
#import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

from database import Customer, create_tables
import database


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.config['SECRET_KEY'] = 'this is a secret key'

bcrypt = Bcrypt(app)
DATABASE_PATH = 'C:\\Users\\Bongeka.Mpofu\\DB Browser for SQLite\\site.db'


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# TABLE CREATION
def create_tables():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

        db.execute('''CREATE TABLE IF NOT EXISTS food (
                        food_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        food_name TEXT,
                        food_price DECIMAL(10,2),
                        food_type TEXT,
                        file_image TEXT)''')

        db.execute('''CREATE TABLE IF NOT EXISTS cartitem (
                        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cart_name TEXT,
                        quantity INTEGER,
                        food_id INTEGER,
                        FOREIGN KEY(food_id) REFERENCES food(food_id))''')

        db.execute('''CREATE TABLE IF NOT EXISTS "order" (
                        order_no INTEGER PRIMARY KEY AUTOINCREMENT,
                        food_id INTEGER,
                        quantity INTEGER)''')

        db.execute('''CREATE TABLE IF NOT EXISTS pay (
                        pay_no INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_no INTEGER UNIQUE,
                        total_price DECIMAL(10,2),
                        cust_name TEXT,
                        cust_address TEXT,
                        cust_postcode TEXT,
                        cust_email TEXT,
                        cust_cardno TEXT,
                        card_expirydate TEXT,
                        card_cvv TEXT,
                        trans_option TEXT,
                        pay_datetime TEXT,
                        FOREIGN KEY(order_no) REFERENCES "order"(order_no) ON DELETE CASCADE)''')

        db.execute('''CREATE TABLE IF NOT EXISTS rest (
                        rest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rest_name TEXT,
                        address TEXT,
                        stars INTEGER,
                        image TEXT)''')

        db.execute('''CREATE TABLE IF NOT EXISTS table_book (
                        table_id TEXT PRIMARY KEY,
                        rest_id INTEGER,
                        table_type TEXT,
                        reserve_fee DECIMAL(10,2),
                        max_occupants INTEGER,
                        available BOOLEAN,
                        FOREIGN KEY(rest_id) REFERENCES rest(rest_id))''')

        db.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        book_no INTEGER PRIMARY KEY AUTOINCREMENT,
                        table_id TEXT,
                        user_id INTEGER,
                        book_date_time TEXT,
                        total_price DECIMAL(10,2),
                        FOREIGN KEY(table_id) REFERENCES table_book(table_id),
                        FOREIGN KEY(user_id) REFERENCES user(id))''')
    print("Tables created successfully!")

# Initialize database
database.create_tables(DATABASE_PATH)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        if not username or not email or not password:
            flash("All fields are required!")
            return redirect(url_for('register'))

        # Create and save Customer
        customer = Customer(username, email, hashed_password)
        try:
            customer.save_to_db(DATABASE_PATH)
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error saving customer: {str(e)}")
            print("Error saving customer:", e)
            return redirect(url_for('register'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db() as db:
            customer = db.execute('SELECT * FROM customer WHERE username = ?', (username,)).fetchone()
            if customer and bcrypt.check_password_hash(customer['password'], password):
                session['username'] = username
                return redirect(url_for('welcome'))
            else:
                flash("Invalid credentials. Please try again.")
    return render_template('login.html')


@app.route('/welcome')
def welcome():
    if "username" in session:
        with get_db() as db:
            food_items = db.execute('SELECT * FROM food').fetchall()
        return render_template('welcome.html', food=food_items)
    else:
        return redirect(url_for('login'))

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # Use a cursor to fetch all food items
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM food")
    food = cursor.fetchall()  # Convert query result to a list of rows

    # Fetch selected menu item type
    selected_menu = request.args.get('type')
    if selected_menu:
        cursor.execute("SELECT * FROM food WHERE food_name = ?", (selected_menu,))
        food_data = cursor.fetchone()
        if food_data:
            price = food_data['food_price']
            fid = food_data['food_id']
        else:
            price = None
            fid = None
    else:
        price = None
        fid = None

    return render_template("menu.html", title='Menu Details', food_name=selected_menu, food_price=price, food_id=fid)


# Route to render the table booking form
@app.route('/table_booking', methods=['GET'])
def table_booking():
    return render_template('table_booking.html')

@app.route('/book_table', methods=['POST'])
def book_table():
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get form data for the booking
    table_id = "n12"
    user_id = 1  # Replace with dynamic user_id if available (e.g., from session)
    people = request.form.get('people')
    date = request.form.get('date')
    time = request.form.get('time')
    datetime_str = f"{date} {time}"

    # Retrieve the reserve fee for the selected table
    cursor.execute("SELECT reserve_fee FROM table_book WHERE table_id = ?", (table_id,))
    result = cursor.fetchone()
    if not result:
        flash("Selected table does not exist.")
        return redirect(url_for('table_booking'))

    reserve_fee = result[0]
    total_price = reserve_fee * int(people)

    # Insert new booking record into Bookings table
    try:
        cursor.execute("INSERT INTO bookings(table_id, user_id, book_date_time, total_price) VALUES (?, ?, ?, ?)",
                       (table_id, user_id, datetime_str, total_price))
        conn.commit()
    except sqlite3.Error as e:
        print("An error occurred:", e)
        flash("Error adding booking, please try again.")
        return redirect(url_for('table_booking'))

    # Retrieve the latest order_no from the Pay table
    cursor.execute("SELECT order_no FROM Pay ORDER BY order_no DESC LIMIT 1")
    last_pay = cursor.fetchone()
    new_order_no = last_pay[0] + 1 if last_pay else 1

    # Close the database connection
    conn.close()

    # Redirect to payment route, passing both total_price and order_no
    return redirect(url_for('payment_table', total_price=total_price, order_no=new_order_no))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Assuming the user is logged in
        usern = login_session.get('username')

        # Connect to the database
        conn = get_db()
        cursor = conn.cursor()

        # Retrieve the latest order_no from the Pay table
        cursor.execute('SELECT order_no FROM "order" ORDER BY order_no DESC LIMIT 1')
        last_order = cursor.fetchone()
        new_order_no = last_order[0] + 1 if last_order else 1

        total_price = Decimal('0.0')

        # Retrieve cart items and calculate the total price
        cursor.execute("SELECT cartitem.food_id, food.food_name, food.food_price, cartitem.quantity "
                       "FROM cartitem JOIN food ON cartitem.food_id = food.food_id")
        cartitems = cursor.fetchall()

        for item in cartitems:
            food_id = item['food_id']
            quantity = item['quantity']
            food_price = Decimal(item['food_price'])
            total_price += food_price * quantity

            # Insert each item in the Order table with the new order number
            cursor.execute("INSERT INTO 'order' (food_id, quantity) VALUES (?, ?)",
                           (food_id, quantity))
            conn.commit()

        # Get customer details from the form
        cust_name = request.form.get('cardname')
        cust_address = request.form.get('address')
        cust_postcode = request.form.get('postcode')
        cust_email = request.form.get('email')
        cust_cardno = request.form.get('cardnumber')
        card_expirydate = request.form.get('expdate')
        card_cvv = request.form.get('cvv')
        trans_option = request.form.get('trans_option')

        # Insert payment details into the Pay table
        #pay_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        total_price = float(total_price)

        #pay_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pay_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''INSERT INTO pay (order_no, total_price, cust_name, cust_address, cust_postcode, 
                          cust_email, cust_cardno, card_expirydate, card_cvv, trans_option, pay_datetime) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (new_order_no, total_price, cust_name, cust_address, cust_postcode, cust_email,
                        cust_cardno, card_expirydate, card_cvv, trans_option, pay_datetime))
        conn.commit()

        # Clear the cart after payment
        cursor.execute("DELETE FROM cartitem")
        conn.commit()

        # Fetch the most recent payment entry for receipt display
        cursor.execute("SELECT * FROM pay ORDER BY pay_no DESC LIMIT 1")
        recentp = cursor.fetchone()

        return render_template("receipt.html", recentp=recentp)

    else:
        # Calculate total price to display on payment page
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity * food_price) as total FROM cartitem JOIN food ON cartitem.food_id = food.food_id")
        total_price_data = cursor.fetchone()
        total_price = total_price_data['total'] if total_price_data['total'] else 0.00

        return render_template('checkout_table.html', total_price=total_price)


@app.route('/payment_table/<float:total_price>/<int:order_no>', methods=['GET', 'POST'])
def payment_table(total_price, order_no):
    if request.method == 'POST':
        # Collect payment details from the form
        cust_name = request.form.get('cardname')
        cust_address = request.form.get('address')
        cust_postcode = request.form.get('postcode')
        cust_email = request.form.get('email')
        cust_cardno = request.form.get('cardnumber')
        card_expirydate = request.form.get('expdate')
        card_cvv = int(request.form.get('cvv'))
        trans_option = request.form.get("trans_option")

        # Insert the new payment into the 'pay' table
        with get_db() as db:
            db.execute('''INSERT INTO pay (
                            order_no, total_price, cust_name, cust_address, 
                            cust_postcode, cust_email, cust_cardno, 
                            card_expirydate, card_cvv, trans_option
                          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (order_no, total_price, cust_name, cust_address,
                        cust_postcode, cust_email, cust_cardno,
                        card_expirydate, card_cvv, trans_option))

            # Commit the transaction
            db.commit()

            # Retrieve the most recent payment entry for the receipt
            recentp = db.execute('SELECT * FROM pay ORDER BY pay_no DESC LIMIT 1').fetchone()

        return render_template("receipt.html", recentp=recentp)

    # If GET request, render checkout page with total price and order number
    return render_template("checkout_table.html", total_price=total_price, order_no=order_no)


@app.route('/addfood', methods=['GET', 'POST'])
def addfood():
    if request.method == 'POST':
        food_name = request.form['food_name']
        food_price = request.form['food_price']
        food_type = request.form['food_type']
        file_image = request.files['file1']

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_image.filename)
        file_image.save(file_path)

        with get_db() as db:
            db.execute('''INSERT INTO food (food_name, food_price, food_type, file_image) 
                          VALUES (?, ?, ?, ?)''', (food_name, food_price, food_type, file_path))
        return redirect(url_for('welcome'))
    return render_template('createfood.html')


@app.route('/delete_food/<int:food_id>', methods=['POST'])
def delete_food(food_id):
    with get_db() as db:
        db.execute('DELETE FROM cartitem WHERE food_id = ?', (food_id,))
        db.execute('DELETE FROM food WHERE food_id = ?', (food_id,))
    return redirect(url_for('welcome'))


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Update using raw SQL
        sql = """
            UPDATE Customer
            SET email = :email, 
                password = :hashed_password
            WHERE username = :username;
        """
        db.session.execute(sql, {'email': email, 'hashed_password': hashed_password, 'username': username})
        db.session.commit()

        return redirect(url_for('welcome'))

    return render_template('update.html')


@app.route('/addtocart', methods=['POST'])
def addtocart():
    if "username" in session:
        food_id = request.form.get("food_id")
        food_name = request.form.get("food_name")
        food_price = request.form.get("food_price")
        quantity = int(request.form.get("name_of_slider"))

        cart_name = f"cart{food_id}"
        with get_db() as db:
            db.execute('''INSERT INTO cartitem (cart_name, quantity, food_id) VALUES (?, ?, ?)''',
                       (cart_name, quantity, food_id))
        return redirect(url_for('welcome'))


@app.route('/checkout')
def checkout():
    # Query to join CartItem with Food and retrieve necessary fields
    cartitems = db.session.query(
        CartItem.quantity,
        Food.food_name,
        Food.food_price
    ).join(Food, CartItem.food_id == Food.food_id).all()

    return render_template('checkout.html', cartitems=cartitems)


@app.route('/view_cart')
def view_cart():
    # Fetch cart items from the database
    sql = """
        SELECT MenuItems.name, MenuItems.price, Cart.quantity, 
               (MenuItems.price * Cart.quantity) AS total_price
        FROM Cart
        JOIN MenuItems ON Cart.item_id = MenuItems.id;
    """
    result = db.session.execute(sql)
    cart_items = result.fetchall()

    return render_template('view_cart.html', cart_items=cart_items)

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)


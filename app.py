from flask import Flask, render_template, request, redirect, session, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'jothi_secret_key'

DB_FILE = 'data.json'

# Initialize admin credentials
ADMIN_USERNAME = 'jothilingam'
ADMIN_PASSWORD = 'jothi3845'

# Load data from JSON
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({'customers': {}}, f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

# Save data to JSON
def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        print(f"Login Attempt: Username: {uname}, Password: {pwd}")  # Debugging line

        # Check for admin login
        if uname == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['admin'] = True
            print(f"Admin logged in: {session}")  # Debugging line
            return redirect('/admin')

        data = load_data()
        customers = data['customers']
        
        # Check for customer login
        if uname in customers and customers[uname]['password'] == pwd:
            session['customer'] = uname
            print(f"Customer logged in: {session}")  # Debugging line
            return redirect('/customer')

        flash('Invalid username or password')

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/')

    data = load_data()
    customers = data['customers']

    if request.method == 'POST':
        if request.form.get('create_customer') == 'true':
            new_user = request.form['new_username']
            new_pass = request.form['new_password']
            if new_user not in customers:
                customers[new_user] = {
                    'password': new_pass,
                    'pending_amount': 0,
                    'payments': []
                }
                save_data(data)
        else:
            username = request.form.get('username')
            amount = request.form.get('amount')
            date = request.form.get('date')
            action = request.form.get('action')

            # Check if all fields are provided
            if not all([username, amount, date, action]):
                flash("Please fill in all fields.")
                return redirect('/admin')

            try:
                amount = float(amount)
            except ValueError:
                flash("Amount must be a number.")
                return redirect('/admin')

            if username in customers:
                if action == 'add':
                    customers[username]['pending_amount'] += amount
                elif action == 'subtract':
                    customers[username]['pending_amount'] -= amount
                    amount = -amount
                customers[username]['payments'].append({
                    'amount': amount,
                    'date': date
                })
                save_data(data)

    return render_template('admin_dashboard.html', customers=customers)

@app.route('/customer')
def customer_dashboard():
    uname = session.get('customer')
    if not uname:
        return redirect('/')

    data = load_data()
    customer = data['customers'].get(uname)
    if not customer:
        return redirect('/')

    return render_template(
        'customer_dashboard.html',
        username=uname,
        pending=customer['pending_amount'],
        payments=customer['payments']
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# For Render deployment: bind to 0.0.0.0 and use PORT env variable
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
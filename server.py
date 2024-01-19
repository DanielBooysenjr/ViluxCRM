from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, send_from_directory, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

import logging as lg

from mysql.connector import pooling
import json
from datetime import datetime

from loginForm import LoginForm
from newLead import NewLead
from editLead import EditLead
from newEmployee import NewEmployee


db_config = {
        "host": "127.0.0.1",
        "port": "3306",
        "user": "root",
        "password": "Baphomet6969!",
        "database":"Vilux",
            }

connection_pool = pooling.MySQLConnectionPool(pool_name="pool", pool_size=5, **db_config)


app = Flask(__name__, static_folder='static')
app.secret_key = 'JHkfjsfa183n5rkjjkNKDG093N'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_NAME'] = 'remember_token'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Login Manager #

login_manager = LoginManager()
login_manager.init_app(app)

# Login Manager #

class User(UserMixin):
    def __init__(self, id, firstname, lastname, contactnumber, email, address, area, machine, password, role, position):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.contactnumber = contactnumber
        self.email = email
        self.address = address
        self.area = area
        self.machine = machine
        self.role = role
        self.position = position

    def is_active(self):
        return True
    

@login_manager.user_loader
def load_user(user_id):


    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT id, fname, lname, password, contactNumber, email, address, area, machine, role, position FROM Users WHERE id = %s', (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5], user_data[6], user_data[7], user_data[8], user_data[9], user_data[10])
        
        lg.info(f'User not found with ID: {user_id}')

    except ConnectionError as e:
        lg.error(f"Couldn't connect to DB to get user data: {e}")
    except Exception as e:
        lg.error(f"Error loading user: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return None

def configure_logging():
    lg.basicConfig(filename='./viluxcrm.log', level=lg.INFO)

# Call the configure_logging function to set up logging
configure_logging()

@app.route("/register", methods=['POST', 'GET'])
def register():
    connection = None
    if request.method == 'POST':
        firstname = request.form['Firstname']
        lastname = request.form['Lastname']
        cellphone = request.form['Cellphone']
        email = request.form['Email']
        password = request.form['Password']
        rpassword = request.form['rPassword']

        try:
            connection = connection_pool.get_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM Users WHERE email = %s', (email, ))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("User with that email already exists")
            else:
                if password == rpassword:
                        user_password = generate_password_hash(password, 'pbkdf2', 8)

                        
                        cursor.execute('INSERT INTO Users (fName, lName, password, contactNumber, email, role) VALUES (%s, %s, %s, %s, %s, %s)',
                                    (firstname, lastname, user_password, cellphone, email, 'employee'))
                        connection.commit()
                        return redirect(url_for('login'))
                else:
                    flash("Passwords do no match")
        except ConnectionError as e:
            lg.error(f"Can not register user and connect to DB: {e}")
        finally:
            if connection is not None:
                connection.close()
    return render_template('sign-up.html')

@app.route("/", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    connection = None
    try:
        email = request.form['email']
        password = request.form['password']
        try:
            connection = connection_pool.get_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM Users WHERE email = %s', (email, ))
            user = cursor.fetchone()
            user_password = user[3]
            if user:
                try:
                    if check_password_hash(user_password, password):
                        try:
                            user_to_login = User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8], user[9], user[10])
                            login_user(user_to_login)
                        except Exception as e:
                            lg.error(f"Error logging in user: {e}")
                        return redirect(url_for('appointments'))
                    else:
                        lg.error("incorrect password")
                except Exception as e:
                    lg.error(f"Error with password {e}")
            else:
                lg.error("User not found")
        except ConnectionError as e:
            lg.error(f"Problem connecting to login in user: {e}")
        finally:
            if connection is not None:
                connection.close()
            
    except Exception as e:
        lg.error(f"Error getting information: {e}")

    return render_template('sign-in.html', form=form)


@app.route("/logged-out")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('index.html')

@app.route("/appointments")
@login_required
def appointments():
    connection = None
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()


        if current_user.role == 'admin':
            cursor.execute("SELECT * FROM Appointments")
            appointments = cursor.fetchall()

            cursor.execute("SELECT * FROM Leadappointments")
            lead_appointments = cursor.fetchall()
        elif current_user.role == 'employee':
            employee_name = current_user.firstname + ' ' + current_user.lastname
            cursor.execute("SELECT * FROM Appointments WHERE assigned =  %s", (employee_name, ))
            appointments = cursor.fetchall()

            cursor.execute("SELECT * FROM Leadappointments WHERE assigned =  %s", (employee_name, ))
            lead_appointments = cursor.fetchall()


    except Exception as e:
        lg.error(f"Connection failed to get appointments: {e}")
        connection.rollback()
    finally:
        if connection is not None:
            connection.close()

    return render_template('appointments.html', appointments=appointments, lead_appointments=lead_appointments)

@app.route("/billing")
@login_required
def billing():
    return render_template('billing.html')

@app.route("/profile")
@login_required
def profile():

    return render_template('profile.html')

### LEADS ###

@app.route("/leads")
@login_required
def leads():
    connection = None
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        if current_user.role == 'admin':
            cursor.execute("SELECT * FROM Leads")
            leads = cursor.fetchall()
        elif current_user.role == 'employee':
            employee_name = current_user.firstname + ' ' + current_user.lastname
            cursor.execute("SELECT * FROM Leads WHERE assigned = %s", (employee_name, ))
            leads = cursor.fetchall() 
    except ConnectionError as e:
        lg.error(f"Couldn't connect to get leads: {e}")
        connection.rollback()
    finally:
        if connection is not None:
            connection.close()
    return render_template('leads.html', leads=leads)

@app.route("/new-lead", methods=['POST', 'GET'])
@login_required
def new_lead():
    form = NewLead
    employees = []
    connection = None
    try:

        connection = connection_pool.get_connection()
        cursor = connection.cursor()


        if current_user.role == 'admin':
            cursor.execute('SELECT * FROM Users WHERE role = %s', ('employee', ))
            employees = cursor.fetchall()

        if request.method == 'POST':
            try:
                name = request.form['name']
                number = request.form['number']
                email = request.form['email']
                area = request.form['area']
                status = request.form['status']
                services = request.form['services']
                comments = request.form['comments']

                if current_user.role == 'employee':
                    assigned_to = current_user.firstname + ' ' + current_user.lastname
                elif current_user.role == 'admin':
                    assigned_to = request.form['assigned']

                try:
                    cursor.execute('INSERT INTO LEADS (name, number, email, area, status, services, comments, assigned) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (
                        name, number, email, area, status, services, comments, assigned_to
                    ))
                    connection.commit()
                except Exception as e:
                    lg.info(f"Can't insert lead into database: {e}")
            except Exception as e:
                lg.error(f"Error in submitting and getting form data: {e}")
    except ConnectionError as e:
        lg.error(f"Couldn't connect to insert lead: {e}")
    finally:
        if connection is not None:
            connection.close()
    return render_template('add-lead.html', form=form, employees=employees)

@app.route("/edit-lead/<pk>", methods=['POST', 'GET'])
@login_required
def edit_lead(pk):
    form = NewLead()
    connection = None

    try:

        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Leads WHERE id = %s", (pk, ))
        lead = cursor.fetchone()

        cursor.execute("SELECT * FROM Users WHERE role = %s", ('employee', ))
        employees = cursor.fetchall()


        cursor.execute('SELECT * FROM LeadAppointments WHERE number = %s', (lead[2], ))
        appointments = cursor.fetchall()

        action = request.form.get('action')
        if request.method == 'POST':
            try:
                if action == 'update':
                    try:
                        name = request.form['name']
                        number = request.form['number']
                        email = request.form['email']
                        area = request.form['area']
                        status = request.form['status']
                        services = request.form['services']
                        comments = request.form['comments']
                    except Exception as e:
                        lg.error(f"Error is here: {e}")

                    try:
                        cursor.execute(
                            'UPDATE Leads SET name = %s, number = %s, email = %s, area = %s, status = %s, services = %s, comments = %s WHERE id = %s',
                            (name, number, email, area, status, services, comments, lead[0])
                            )
                        connection.commit()
                    except Exception as e:
                        lg.error(f"Error occured when updating lead: {e}")
                    return redirect(url_for('leads'))
            except Exception as e:
                lg.error(f"Error updating lead: {e}")

            try:

                if action == 'delete':
                    cursor.execute('DELETE FROM Leads WHERE id = %s', (pk, ))
                    connection.commit()
                    return redirect(url_for('leads'))
                
                elif action == 'convert':
                    cursor.execute('DELETE FROM Leads WHERE id =%s', (pk, ))
                    connection.commit()
                    try:
                        cursor.execute('INSERT INTO Customers (name, number, email, area, amount, services, comments, subject, message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                                (lead[1], lead[2], lead[3], lead[4], lead[5], lead[7], lead[8], lead[9], lead[10]))
                        connection.commit()
                        return redirect(url_for('leads'))
                    except Exception as e:
                        lg.error(f"Error occured when inserting into customers: {e}")

                elif action == 'add-appointment':
                    try:
                        cursor = connection.cursor()
                        date = request.form['date']
                        date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M')
                        today_date = datetime.now().strftime('%Y-%m-%d')

                        date = date_obj.date()
                        time = date_obj.strftime('%H:%M')

                        appointment_services = request.form.getlist('items[]') 

                        services_json = json.dumps(appointment_services)

                        status = request.form['status']
                        comments = request.form['comments']

                        if current_user.role == 'admin':
                            assigned = request.form['assigned']
                        elif current_user.role == 'employee':
                            assigned = current_user.firstname + ' ' + current_user.lastname
                        
                        cursor.execute('INSERT INTO LeadAppointments (date, time, services, number, customer, address, assigned, status, comments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                                    (date, time, services_json, lead[2], lead[1], lead[4], assigned, status, comments))
                        connection.commit()

                        cursor.execute('UPDATE Leads SET nextappointment = %s, lastcontacted = %s WHERE id = %s', (date, today_date, lead[0]))
                        connection.commit()

                        return redirect(url_for('edit_lead  ', pk=pk))
                    except Exception as e:
                        lg.error(f"Error creating appointment") 

            except Exception as e:
                lg.error(f"Problem with editing or updating lead: {e}")


    except ConnectionError as e:
        lg.error(f"Couldn't get connection for edit lead: {e}")
    finally:
        if connection is not None:
            connection.close()


    return render_template('edit-lead.html', lead=lead, form=form, employees=employees, appointments=appointments)


@app.route('/edit-lead-appointment/<pk>', methods=['POST', 'GET'])
def edit_lead_appointment(pk):

    connection = None

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM LeadAppointments WHERE id = %s', (pk, ))
        lead_appointment = cursor.fetchone()

        action = request.form.get('action')
        if request.method == 'POST':

            if action == 'update':
                customer = request.form['customer']
                date = request.form['date']
                address = request.form['address']
                number = request.form['number']
                status = request.form['status']
                services = request.form['services']
                comments = request.form['comments']

                try:
                    cursor.execute('SELECT * FROM Leads WHERE number = %s', (number,))
                    lead = cursor.fetchone()
                    lead_id = lead[0]
                except Exception as e:
                    lg.error(f"Can't get lead pk: {e}")

                try:

                    cursor.execute('UPDATE LeadAppointments SET customer = %s, date = %s, address = %s, number = %s, status = %s, services = %s, comments = %s WHERE id = %s', (
                        customer, date, address, number, status, services, comments, pk,
                    ))

                    connection.commit()
                    return redirect(url_for('edit_lead', pk=lead_id))
                except Exception as e:
                    lg.error(f"Problem updating lead appointment: {e}")
                    connection.rollback()

            elif action == 'delete':

                try:
                    cursor.execute('DELETE FROM LeadAppointments WHERE id = %s', (pk, ))
                    connection.commit()
                    return redirect(url_for('edit_lead', pk=lead_id))
                except Exception as e:
                    lg.error(f"Problem deleting lead appointment: {e}")
                    connection.rollback()


    except Exception as e:
        lg.error(f"Error getting lead appointment: {e}")
    finally:
        if connection is not None:
            connection.close()

    return render_template('edit-lead-appointment.html', lead_appointment=lead_appointment)

### END OF LEADS ###

### Customers ###

@app.route("/customers")
@login_required
def customers():
    connection = None
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        if current_user.role == 'admin':
            cursor.execute('SELECT * FROM Customers')
            customers = cursor.fetchall()
        elif current_user.role == 'employee':
            employee_name = current_user.firstname + ' ' + current_user.lastname
            cursor.execute('SELECT * FROM Customers WHERE assigned = %s', (employee_name, ))
            customers = cursor.fetchall()
    except ConnectionError as e:
        lg.error(f"Couldn't get connection for customers: {e}")
    finally:
        if connection is not None:
            connection.close()

    return render_template('customers.html', customers=customers)


@app.route("/add-customer", methods=['POST', 'GET'])
@login_required
def add_customer():
    form = NewLead
    employees = []
    connection = None
    if request.method == 'POST':
        try:
            connection = connection_pool.get_connection()
            cursor = connection.cursor()
            name = request.form['name']
            number = request.form['number']
            email = request.form['email']
            area = request.form['area']
            amount = request.form['amount']
            status = request.form['status']
            services = request.form['services']
            comments = request.form['comments']

            if current_user.role == 'employee':
                assigned = current_user.firstname + ' ' + current_user.lastname
            elif current_user.role == 'admin':
                cursor.execute("SELECT * FROM Users WHERE role = %s", ('employee', ))
                employees = cursor.fetchall()
                assigned = request.form['assigned']


            cursor.execute('INSERT INTO Customers (name, number, email, area, amount, status, services, comments, assigned) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (
                name, number, email, area, amount, status, services, comments, assigned
            ))
            connection.commit()
        except ConnectionError as e:
            lg.error(f"Couldn't get connection for add customer: {e}")
            connection.rollback()
        finally:
            if connection is not None:
                connection.close()
    return render_template('add-customer.html', form=form, employees=employees)


@app.route("/view-customer/<pk>", methods=['POST', 'GET'])
@login_required
def view_customer(pk):
    form = NewLead()
    employees = []
    connection = None

        
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        if current_user.role == 'admin':
            cursor.execute("SELECT * FROM Users WHERE role = %s", ('employee', ))
            employees = cursor.fetchall()
        cursor.execute("SELECT * FROM Customers WHERE id = %s", (pk, ))
        customer = cursor.fetchone()

        cursor.execute('SELECT * FROM Appointments WHERE Number = %s', (customer[2], ))
        appointments = cursor.fetchall()

        # Extract the items from the database result as a list of strings
        item_list = [appointment[2] for appointment in appointments]

        # Convert the list to a comma-separated string
        items_as_string = ', '.join(item_list).replace('[', '').replace(']', '').replace('"', '')



        if request.method == 'POST':
            action = request.form.get('action')  # Assuming you add a hidden field named 'action' in your form

            if action == 'update':
                cursor = connection.cursor()
                name = request.form['name']
                number = request.form['number']
                email = request.form['email']
                area = request.form['area']
                amount = request.form['amount']
                services = request.form['services']
                comments = request.form['comments']

                cursor.execute(
                    'UPDATE Customers SET name = %s, number = %s, email = %s, address = %s, amount = %s, services = %s, comments = %s WHERE id = %s',
                    (name, number, email, area, amount, services, comments, customer[0])
                    )
                connection.commit()
                return redirect(url_for('customers'))

            elif action == 'delete':
                cursor = connection.cursor()
                cursor.execute('DELETE FROM Customers WHERE id = %s', (pk, ))
                connection.commit()
                return redirect(url_for('customers'))
            
            elif action == 'convert':
                cursor = connection.cursor()
                cursor.execute('DELETE FROM Customers WHERE id =%s', (pk, ))
                cursor.execute('INSERT INTO Customers (name, number, email, area, amount, services, comments, subject, message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (customer[1], customer[2], customer[3], customer[4], customer[5], customer[7], customer[8], customer[9], customer[10]))

                connection.commit()
                return redirect(url_for('customers'))
            
            elif action == 'add-appointment':
                cursor = connection.cursor()
                date = request.form['date']
                date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M')

                date = date_obj.date()
                time = date_obj.strftime('%H:%M')

                appointment_services = request.form.getlist('items[]') 
                appointment_amounts = request.form.getlist('amounts[]')

                all_amounts = [int(amount) for amount in appointment_amounts]
                total_amount = sum(all_amounts)

                services_json = json.dumps(appointment_services)
                amounts_json = json.dumps(appointment_amounts)

                if current_user.role == 'admin':
                    assigned = request.form['assigned']
                elif current_user.role == 'employee':
                    assigned = current_user.firstname + ' ' + current_user.lastname
                
                cursor.execute('INSERT INTO Appointments (date, time, services, amount, total, number, customer, address, assigned) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                               (date, time, services_json, amounts_json, total_amount, customer[2], customer[1], customer[4], assigned ))
                connection.commit()

                cursor.execute('UPDATE Customers SET amount = %s, lastbooked = %s WHERE id = %s', (total_amount, date, customer[0]))
                connection.commit()

            return redirect(url_for('view_customer', pk=pk))
    except ConnectionError as e:
        lg.error(f"Can't establish connection viewing customers: {e}")
    finally:
        if connection is not None:
            connection.close()

    return render_template('view-customer.html', customer=customer, form=form, appointments=appointments,  items_as_string=items_as_string, employees=employees)

### End Customers ###

### Employees ###

@app.route('/employees')
@login_required
def employees():
    connection = None
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE role = %s", ('employee', ))
        employees = cursor.fetchall()
    except ConnectionError as e:
        lg.error(f"Can't get connection for employees: {e}")
    finally:
        if connection is not None:
            connection.close()
    return render_template('employees.html', employees=employees)


@app.route("/add-employee", methods=['POST', 'GET'])
@login_required
def add_employee():
    form = NewEmployee()
    connection = None
    if request.method == 'POST':
        try:
            connection = connection_pool.get_connection()
            cursor = connection.cursor()
            name = request.form['name']
            address = request.form['address']
            contact = request.form['contact']
            idnumber = request.form['idnumber']
            machine = request.form['machine']
            startdate = request.form['startdate']
            enddate = request.form['enddate']
            vehcilereg = request.form['vehcilereg']

            # cursor.execute('INSERT INTO Customers (name, number, email, area, amount, status, services, comments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (
            #     name, number, email, area, amount, status, services, comments
            # ))
            connection.commit()
        except ConnectionError as e:
            lg.error(f"Can't connect to add employee: {e}")
        finally:
            if connection is not None:
                connection.close()
    return render_template('new-employee.html', form=form)


@app.route("/manage-employee/<pk>", methods=['POST', 'GET'])
def manage_employee(pk):
    connection = None
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE id = %s', (pk, ))
        employee = cursor.fetchone()
    except ConnectionError as e:
        lg.error('Can not get employees in manage employee endpoint: {e}')
    finally:
        if connection is not None:
            connection.close()

    return render_template('manage-employee.html', employee=employee)


### End Employees


@app.route("/machines")
@login_required
def machines():
    return render_template('machines.html')


if __name__ == '__main__':
    app.run(debug=True)

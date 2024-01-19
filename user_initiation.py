# Login Manager #
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user



login_manager = LoginManager()
login_manager.init_app(app)

# Login Manager #

class User(UserMixin):
    def __init__(self, id, firstname, lastname, contactnumber, email, address, area, machine, password, role):
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

    def is_active(self):
        return True

@login_manager.user_loader
def load_user(user_id):
    try:
        DB.connect()
        cursor = DB.cursor()
    except Exception as e:
        print(e)
    cursor.execute('SELECT id, firstname, lastname, ContactNumber, email, password, StudentSchool, UserRole, Approved, auth, StudentId FROM Users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5], user_data[6], user_data[7], user_data[8], user_data[9], user_data[10])
    cursor.close()
    lg.info(f'User Loaded with user data: {user_data}')
    return None
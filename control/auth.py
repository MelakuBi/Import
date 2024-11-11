from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from control.models import User, LoginAction
from control.extensions import db
from flask_login import login_user, logout_user, login_required, current_user, LoginManager

# Create a blueprint for authentication
auth_bp = Blueprint('auth', __name__)


# User registration route

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

login_manager = LoginManager()



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name')  # Optional
        last_name = request.form['last_name']
        role = request.form['role']

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
        else:
            new_user = User(
                username=username,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                role=role
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! User created.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

# User login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session['username'] = user.username
            if user.is_admin:
                return redirect(url_for('admin.dashboard', msg=username))  # Change this line
            else:
                return redirect(url_for('users.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return redirect(url_for('main.index'))

@auth_bp.route('/loginform', methods=['GET'])
def loginform():
    return render_template('login_form.html')

# User logout route
@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('auth.login'))


#dashboard for Admin and users
users_bp = Blueprint('users', __name__)
@users_bp.route('/dashboard')
@login_required
def dashboard():
    # Logic for standard user dashboard
    return render_template("user_dashboard.html")

# In admin.py (for admin users)
admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/dashboard')
def dashboard():
    # Logic for admin dashboard
    return render_template('admin_dashboard.html')
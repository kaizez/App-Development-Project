from flask import Flask, render_template, request, redirect, url_for, flash, session
import shelve
import time
import os
from user import User
from forms import RegisterForm
from forms import LoginForm
from forms import EditUsernameForm

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_EMAIL = 'bryceang2007@gmail.com'
ADMIN_PASSWORD = 'ecobike'

#create data dictionary
if not os.path.exists('data'):
    os.makedirs('data')

#for database
db_path = os.path.join('data', 'users_db')


def datenow():
    return str(int(time.time()))



def init_admin():
    try:
        with shelve.open(db_path, flag='c') as db:
            if ADMIN_EMAIL not in db:
                admin_password_hash = User.hash_password(ADMIN_PASSWORD)
                # Set is_admin=True when creating admin user
                admin_user = User(ADMIN_EMAIL, 'admin', admin_password_hash, is_admin=True)
                db[ADMIN_EMAIL] = admin_user.to_dict()
    except Exception as e:
        print(f"Error initializing admin: {str(e)}")


@app.route('/')
def home():
    init_admin()
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    with shelve.open(db_path) as db:
        if email not in db:
            flash('Email not found.')
            return redirect(url_for('home'))

        user_data = db[email]
        user = User.from_dict(user_data)

        if not user.check_password(password):
            flash('Incorrect password.')
            return redirect(url_for('home'))

        user.update_last_login()
        db[email] = user.to_dict()

        session['user_id'] = email
        session['is_admin'] = user.is_admin()  # Make sure this is set

        if user.is_admin():  # Check the user object directly
            return redirect(url_for('admin'))
        return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))

        with shelve.open(db_path) as db:
            if email in db:
                flash('Email already registered.')
                return redirect(url_for('register'))


            if any(User.from_dict(user_data).get_username() == username
                   for user_data in db.values()):
                flash('Username already taken.')
                return redirect(url_for('register'))

            user = User(
                email=email,
                username=username,
                password=User.hash_password(password),
                user_id=datenow()
            )
            db[email] = user.to_dict()
            flash('Registration successful! Please log in.')
            return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    with shelve.open(db_path) as db:
        current_time = time.time()
        users = []
        regular_users_count = 0
        active_users_count = 0

        # Get data from 30 days ago for comparison
        thirty_days_ago = current_time - (30 * 24 * 3600)
        past_regular_count = 0
        past_active_count = 0

        for email, user_data in db.items():
            user = User.from_dict(user_data)
            is_active = (current_time - user.get_last_login()) <= (30 * 24 * 3600)
            status = 'active' if is_active else 'inactive'

            users.append((
                user.get_username(),
                user.get_user_id(),
                email,
                status,
                user.is_admin()
            ))

            # Only count non-admin users for statistics
            if not user.is_admin():
                regular_users_count += 1
                if is_active:
                    active_users_count += 1

                # Check if user was registered before 30 days ago
                if user.get_last_login() < thirty_days_ago:
                    past_regular_count += 1
                    if current_time - user.get_last_login() <= (60 * 24 * 3600):  # Was active 30 days ago
                        past_active_count += 1

        # Calculate growth percentages
        total_growth = int(((regular_users_count - past_regular_count) / max(past_regular_count, 1)) * 100)
        active_growth = int(((active_users_count - past_active_count) / max(past_active_count, 1)) * 100)

        # Monthly rides calculation (you'll need to implement a proper ride tracking system)
        # This is placeholder logic - replace with actual ride tracking
        current_month_rides = 680  # Replace with actual ride count
        last_month_rides = 354  # Replace with actual previous month count
        rides_growth = int(((current_month_rides - last_month_rides) / max(last_month_rides, 1)) * 100)

        stats = {
            'totalUsers': regular_users_count,
            'activeUsers': active_users_count,
            'monthlyRides': current_month_rides,
            'activePercentage': int((active_users_count / regular_users_count * 100) if regular_users_count > 0 else 0),
            'totalGrowth': total_growth,
            'activeGrowth': active_growth,
            'ridesGrowth': rides_growth
        }

    return render_template('admin.html', users=users, stats=stats)


@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('home'))
    return render_template('dashboard.html')


@app.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    with shelve.open(db_path) as db:

        target_email = None
        for email, user_data in db.items():
            user = User.from_dict(user_data)
            if user.get_user_id() == user_id:
                target_email = email
                break
        else:
            flash('User not found.')
            return redirect(url_for('admin'))

        if request.method == 'POST':
            new_username = request.form['username']

            #
            if any(User.from_dict(u_data).get_username() == new_username
                   and User.from_dict(u_data).get_user_id() != user_id
                   for u_data in db.values()):
                flash('Username already taken.')
                return redirect(url_for('edit', user_id=user_id))

            user.set_username(new_username)
            db[target_email] = user.to_dict()
            flash('Username updated successfully.')
            return redirect(url_for('admin'))

        return render_template('edit.html', user_id=user_id, username=user.get_username())


@app.route('/delete/<user_id>', methods=['POST'])
def delete(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    with shelve.open(db_path) as db:
        for email, user_data in list(db.items()):
            if User.from_dict(user_data).get_user_id() == user_id:
                del db[email]
                flash('User deleted successfully.')
                break

    return redirect(url_for('admin'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/add_admin', methods=['POST'])
def add_admin():
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('admin'))

    with shelve.open(db_path) as db:
        if email in db:
            flash('Email already registered.')
            return redirect(url_for('admin'))

        if any(User.from_dict(user_data).get_username() == username
               for user_data in db.values()):
            flash('Username already taken.')
            return redirect(url_for('admin'))

        user = User(
            email=email,
            username=username,
            password=User.hash_password(password),
            user_id=datenow(),
            is_admin=True
        )
        db[email] = user.to_dict()
        flash('Admin user created successfully.')
        return redirect(url_for('admin'))


@app.route('/toggle_admin/<user_id>', methods=['POST'])
def toggle_admin(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    with shelve.open(db_path) as db:
        for email, user_data in db.items():
            user = User.from_dict(user_data)
            if user.get_user_id() == user_id:
                # Prevent self-demotion
                if email == session['user_id']:
                    flash('You cannot change your own admin status.')
                    return redirect(url_for('admin'))

                user.set_admin(not user.is_admin())
                db[email] = user.to_dict()
                flash(f"User {'promoted to' if user.is_admin() else 'demoted from'} admin.")
                break

    return redirect(url_for('admin'))



if __name__ == '__main__':
    app.run(debug=True)
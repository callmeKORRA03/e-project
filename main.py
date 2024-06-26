from flask import Flask, flash, render_template, request, redirect, session
import random
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = '46d6dd16ec6beaf459693870'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ums.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Session(app)

# User Class


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    edu = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f'User("{self.id}","{self.fname}","{self.lname}","{self.email}","{self.edu}","{self.username}","{self.status}")'

# Create admin Class


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}","{self.id}")'

# Create table


def create_tables():
    with app.app_context():
        db.create_all()


create_tables()

# Insert admin data one time only one time insert this data
# latter will check the condition
with app.app_context():
    admin = Admin(username='hilal123',
                  password=bcrypt.generate_password_hash('hilal123', 10))
    db.session.add(admin)
    db.session.commit()

# Main index


@app.route('/')
def index():
    return render_template('index.html', title="")

# Admin login


@app.route('/admin/', methods=["POST", "GET"])
def adminIndex():
    # Check the request method
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "" and password == "":
            flash('Please fill all the fields', 'danger')
            return redirect('/admin/')
        else:
            admins = Admin.query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password, password):
                session['admin_id'] = admins.id
                session['admin_name'] = admins.username
                flash('Login Successfully', 'success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Email and Password', 'danger')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html', title="Admin Login")

# Admin Dashboard


@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    totalUser = User.query.count()
    totalApprove = User.query.filter_by(status=1).count()
    NotTotalApprove = User.query.filter_by(status=0).count()
    return render_template('admin/dashboard.html', title="Admin Dashboard", totalUser=totalUser, totalApprove=totalApprove, NotTotalApprove=NotTotalApprove)

# Admin get all user


@app.route('/admin/get-all-user', methods=["POST", "GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method == "POST":
        search = request.form.get('search')
        users = User.query.filter(User.username.like('%'+search+'%')).all()
        return render_template('admin/all-user.html', title='Approve User', users=users)
    else:
        users = User.query.all()
        return render_template('admin/all-user.html', title='Approve User', users=users)


@app.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    User.query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('Approve Successfully', 'success')
    return redirect('/admin/get-all-user')

# Change admin password


@app.route('/admin/change-admin-password', methods=["POST", "GET"])
def adminChangePassword():
    admin = Admin.query.get(1)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "" or password == "":
            flash('Please fill the fields', 'danger')
            return redirect('/admin/change-admin-password')
        else:
            Admin.query.filter_by(username=username).update(
                dict(password=bcrypt.generate_password_hash(password, 10)))
            db.session.commit()
            flash('Admin Password updated successfully', 'success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html', title='Admin Change Password', admin=admin)

# Admin logout


@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id'] = None
        session['admin_name'] = None
        return redirect('/')

# User login


@app.route('/user/', methods=["POST", "GET"])
def userIndex():
    if session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        users = User.query.filter_by(email=email).first()
        if users and bcrypt.check_password_hash(users.password, password):
            is_approve = User.query.filter_by(id=users.id).first()
            if is_approve.status == 0:
                flash('Your Account is not approved by Admin', 'danger')
                return redirect('/user/')
            else:
                session['user_id'] = users.id
                session['username'] = users.username
                flash('Login Successfully', 'success')
                return redirect('/user/dashboard')
        else:
            flash('Invalid Email and Password', 'danger')
            return redirect('/user/')
    else:
        return render_template('user/index.html', title="User Login")

# User Register


@app.route('/user/signup', methods=['POST', 'GET'])
def userSignup():
    if session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        username = request.form.get('username')
        edu = request.form.get('edu')
        password = request.form.get('password')
        if fname == "" or lname == "" or email == "" or password == "" or username == "" or edu == "":
            flash('Please fill all the fields', 'danger')
            return redirect('/user/signup')
        else:
            is_email = User.query.filter_by(email=email).first()
            if is_email:
                flash('Email already Exist', 'danger')
                return redirect('/user/signup')
            else:
                hash_password = bcrypt.generate_password_hash(password, 10)
                user = User(fname=fname, lname=lname, email=email,
                            password=hash_password, edu=edu, username=username)
                db.session.add(user)
                db.session.commit()
                flash('Account Created Successfully', 'success')
                return redirect('/user/')
    else:
        return render_template('user/signup.html', title="User Signup")

# Leaderboard route


@app.route('/leaderboard')
def leaderboard():
    winners = User.query.filter(User.status == 1).all()
    return render_template('/user/leaderboard.html', title='Leaderboard', winners=winners)

# User dashboard


# @app.route('/user/dashboard', methods=['GET', 'POST'])
# def userDashboard():
#     if not session.get('user_id'):
#         return redirect('/user/')

#     if 'max_attempts' not in session:
#         session['max_attempts'] = 10  # Default max attempts
#     if 'count' not in session:
#         session['count'] = 0  # Initialize count to 0

#     if request.method == 'POST':
#         guess = request.form.get('guess')
#         difficulty = request.form.get('difficulty')
#         if 'guess_num' not in session:
#             if difficulty == 'low':
#                 session['guess_num'] = random.randint(1, 99)
#             elif difficulty == 'moderate':
#                 session['guess_num'] = random.randint(1, 999)
#             else:
#                 session['guess_num'] = random.randint(1, 9999)

#         if guess.isdigit():
#             guess = int(guess)
#             session['guess'] = guess
#             session['count'] += 1
#         else:
#             flash('Please enter a valid number', 'danger')

#     users = User.query.filter_by(id=session.get('user_id')).first()
#     return render_template('user/dashboard.html', title="User Dashboard", users=users)


@app.route('/user/dashboard', methods=['GET', 'POST'])
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')

    if request.method == 'POST':
        guess = request.form.get('guess')
        difficulty = request.form.get('difficulty')

        if 'guess_num' not in session or 'max_attempts' not in session or 'count' not in session:
            if difficulty == 'low':
                session['guess_num'] = random.randint(1, 99)
                session['max_attempts'] = 10
            elif difficulty == 'moderate':
                session['guess_num'] = random.randint(1, 999)
                session['max_attempts'] = 15
            else:
                session['guess_num'] = random.randint(1, 9999)
                session['max_attempts'] = 20
            session['count'] = 0

        if guess.isdigit():
            guess = int(guess)
            session['guess'] = guess
            session['count'] += 1

            if guess == session['guess_num']:
                flash('Congratulations! You guessed the number.', 'success')
                return redirect('/insert_name')
            elif session['count'] >= session['max_attempts']:
                flash(
                    f'You have exhausted all your attempts. The number was {session["guess_num"]}.', 'danger')
                return redirect('/reset')
            elif guess > session['guess_num']:
                flash('Too High!', 'warning')
            else:
                flash('Too Low!', 'warning')
        else:
            flash('Please enter a valid number', 'danger')

    users = User.query.filter_by(id=session.get('user_id')).first()
    return render_template('user/dashboard.html', title="User Dashboard", users=users)

# Reset game route


@app.route('/reset')
def resetGame():
    if 'guess_num' in session:
        session.pop('guess_num', None)
        session.pop('guess', None)
        session.pop('count', None)
        session.pop('max_attempts', None)
    return redirect('/user/dashboard')

# Insert winner name route


@app.route('/insert_name', methods=['POST'])
def insertName():
    if request.method == 'POST':
        name = request.form.get('name')
        user = User.query.filter_by(username=name).first()
        if user:
            user.status = 1
            db.session.commit()
            flash(f'Congratulations {name}! You won the game.', 'success')
        else:
            flash('Invalid username', 'danger')
    return redirect('/user/dashboard.html')

# User logout


@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/user/')


@app.route('/user/change-password', methods=["POST", "GET"])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/user/')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == "" or password == "":
            flash('Please fill the fields', 'danger')
            return redirect('/user/change-password')
        else:
            users = User.query.filter_by(email=email).first()
            if users:
                hash_password = bcrypt.generate_password_hash(password, 10)
                User.query.filter_by(email=email).update(
                    dict(password=hash_password))
                db.session.commit()
                flash('Password Changed Successfully', 'success')
                return redirect('/user/change-password')
            else:
                flash('Invalid Email', 'danger')
                return redirect('/user/change-password')

    else:
        return render_template('user/change-password.html', title="Change Password")

# User update profile


@app.route('/user/update-profile', methods=["POST", "GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user/')
    users = User.query.get(session.get('user_id'))
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        username = request.form.get('username')
        edu = request.form.get('edu')
        if fname == "" or lname == "" or email == "" or username == "" or edu == "":
            flash('Please fill all the fields', 'danger')
            return redirect('/user/update-profile')
        else:
            session['username'] = None
            User.query.filter_by(id=session.get('user_id')).update(
                dict(fname=fname, lname=lname, email=email, edu=edu, username=username))
            db.session.commit()
            session['username'] = username
            flash('Profile updated Successfully', 'success')
            return redirect('/user/dashboard')
    else:
        return render_template('user/update-profile.html', title="Update Profile", users=users)


if __name__ == "__main__":
    app.run(debug=True)

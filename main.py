# A todo list website with user login

from datetime import date
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'gHYowMzVMDhaVTyUxCyO6A71PVF5ac98'

# Connect to the users database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tasks.db"
db = SQLAlchemy(app)

# User secure login
login_manager = LoginManager()
login_manager.init_app(app)


# TABLE CONFIGURATION
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True)
    email = db.Column(db.VARCHAR(100), unique=True, nullable=False)
    password = db.Column(db.VARCHAR(100), nullable=False)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.INTEGER, primary_key=True)
    # Create Foreign Key to link to ID of user
    author_id = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    task = db.Column(db.VARCHAR(200), nullable=False)
    start = db.Column(db.DATE(), nullable=False)
    status = db.Column(db.BOOLEAN(), nullable=False)


# Create initial database
# db.create_all()


# Store user ID for secure session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/new', methods=['GET', 'POST'])
def new():
    if current_user.is_authenticated:
        return redirect(url_for('list_page'))
    else:
        return redirect(url_for('login'))


@app.route('/list', methods=['GET', 'POST'])
def list_page():
    if request.method == 'POST':
        task = request.form.get('task')
        add_task = Task(author_id=current_user.id,
                        task=task,
                        start=date.today(),
                        status=True)
        db.session.add(add_task)
        db.session.commit()
        return redirect(url_for('list_page'))
    tasks = Task.query.all()
    return render_template('list.html', all_tasks=tasks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('list_page'))
            else:
                error = 'Password incorrect, please try again.'
        else:
            error = 'That email does not exist, please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if User.query.filter_by(email=request.form.get('email')).first():
            error = "That email is already register, log in instead."
        else:
            # Hash the user password before adding to the database
            hash_password = generate_password_hash(request.form.get('password'),
                                                   method='pbkdf2:sha256',
                                                   salt_length=8)
            new_user = User(email=request.form.get('email'),
                            password=hash_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('list_page'))
    return render_template('register.html', error=error)


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task_to_delete = Task.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('list_page'))


@app.route('/check_task/<int:task_id>')
def check_task(task_id):
    task_to_check = Task.query.get(task_id)
    task_to_check.status = 0
    db.session.commit()
    return redirect(url_for('list_page'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()

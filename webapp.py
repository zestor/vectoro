from flask import Flask, render_template, jsonify, redirect, url_for, request, redirect, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SD&F&D&Sd7HHAS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

"""
# Set up the Google OAuth blueprint
google_blueprint = make_google_blueprint(
    # Replace with your Google OAuth client ID
    client_id="989334775830-2i9bbj8ff07t272kh9ev8vnu65882vo0.apps.googleusercontent.com",  
    # Replace with your Google OAuth client secret
    client_secret="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",  
    scope=["profile", "email"],
    offline=True,
)
app.register_blueprint(google_blueprint, url_prefix="/login")

# Signal handler to retrieve user information after OAuth
@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        return False

    # Get user information from Google
    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return False

    # Store user information in the session (e.g., user ID, email)
    user_info = resp.json()
    # You can store user_info in a database and manage user sessions
"""

# Routes
@app.route('/')
def index():
    #if not google.authorized:
    #    return redirect(url_for("google.login"))
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

@app.route('/register')
def register_page():
    #if not google.authorized:
    #    return redirect(url_for("google.login"))
    return render_template('register.html')

@app.route('/login')
def login_page():
    #if not google.authorized:
    #    return redirect(url_for("google.login"))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)
    user = User(email=email, password=hashed_password, firstname=firstname, lastname=lastname)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return 'Invalid credentials', 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/get_indexes')
def get_indexes():
    #if not google.authorized:
    #    return redirect(url_for("google.login"))

    # Get the user's unique identifier (e.g., email) from the session
    #user_id = session.get('user_id')
    #if not user_id:
    #    return jsonify(error='User not authenticated'), 401

    try:
        with open('indexes.txt', 'r') as file:
            indexes = [line.strip() for line in file]
        return jsonify(indexes=indexes)
    except FileNotFoundError:
        return jsonify(error='File not found'), 404

if __name__ == '__main__':
    app.run(debug=True)

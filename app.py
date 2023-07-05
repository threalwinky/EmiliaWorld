#Including libraries and modules
from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from os import path

#Initing app and database connection
db = SQLAlchemy()
app = Flask(__name__)
app.config["SECRET_KEY"] = "thanhdz"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=1)
db.init_app(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=True)
    password = db.Column(db.String)
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=["POST", "GET"])
def log_in():
    if (request.method == "POST"):
        username = request.form["username"]
        password = request.form["password"]
        if (username == "" or password == "") :
            return redirect(url_for("log_in", empty = True))
        # print(password)
        found_user = User.query.filter_by(username=username).first()
        print(found_user)
        session["user"] = username
        user = User(username, password)
        if (found_user == None):
            db.session.add(user)
            db.session.commit()
        # flash("created")
        return redirect(url_for("dash_board"))
    if "user" in session:
        return redirect(url_for("dash_board"))
    return render_template('home.html')

@app.route('/signup')
def sign_up():
    return render_template('signup.html')

@app.route('/logout')
def log_out():
    session.pop("user", None)
    return redirect(url_for('log_in'))

@app.route('/dashboard')
def dash_board():
    if "user" in session:
        name = session["user"]
        return render_template('dashboard.html', user=name)
    else :
        return redirect(url_for("log_in"))

# @app.route('/app')
# def ad():
#     return "ai chat"

# @app.route('/profile')
# def profile():
#     return render_template('profile.html')

#Running website
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
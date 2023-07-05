#Including libraries and modules
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
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
app.permanent_session_lifetime = timedelta(minutes=10)
db.init_app(app)

#Class of database 
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=True)
    password = db.Column(db.String)
    def __init__(self, username, password):
        self.username = username
        self.password = password

#Home Page
@app.route('/', methods=["POST", "GET"])
def log_in():
    if (request.method == "POST"):
        username = request.form["username"]
        password = request.form["password"]
        if (username == "" or password == "") :
            flash("Please enter both username and password", "info")
            return redirect(url_for("log_in"))
        # print(password)
        found_user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar()
        # print(found_user.password)
        
        if (found_user == None):
            flash("Username not found", "info")
            return redirect(url_for("log_in"))
        tpassword = found_user.password
        if (tpassword != password) :
            flash("Wrong password", "info")
            return redirect(url_for("log_in"))
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

#Sign up page
@app.route('/signup', methods=["POST", "GET"])
def sign_up():
    if (request.method == "POST"):
        print(123)
        username = request.form["username"]
        password = request.form["password"]
        rpassword = request.form["rpassword"]
        if (username == "" or password == "" or rpassword == "") :
            flash("Please enter full of area", "info")
            return redirect(url_for("sign_up"))
        elif (password != rpassword):
            flash("Password doesn't match", "info")
            return redirect(url_for("sign_up"))
        found_user = User.query.filter_by(username=username).first()
        user = User(username, password)
        if (found_user == None):
            db.session.add(user)
            db.session.commit()
        else :
            flash("The username have been taken", "info")
            return redirect(url_for("sign_up"))
        flash("Account created! Please log in again")
        return redirect(url_for("log_in"))
    return render_template('signup.html')

#Users Observing
@app.route("/users")
def user_list():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template("list.html", users=users)

#Logging out in dashboard page
@app.route('/logout')
def log_out():
    session.pop("user", None)
    return redirect(url_for('log_in'))

#Dashboard page
@app.route('/dashboard')
def dash_board():
    if "user" in session:
        name = session["user"]
        return render_template('dashboard.html', user=name)
    else :
        return redirect(url_for("log_in"))

#AI chatbot Page
@app.route('/app')
def aichat():
    return render_template('chat.html')



#Profile Page
# @app.route('/profile')
# def profile():
#     return render_template('profile.html')

#Running website
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
#Including libraries and modules
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from datetime import timedelta
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
from os import path
import requests
import json

#Initing app and database connection
db = SQLAlchemy()
app = Flask(__name__)
app.config["SECRET_KEY"] = "2b3ifbf302f9nc1j2po1jewkajsd"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=10)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origin="*")

#Class of database 
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=True)
    password = db.Column(db.String)
    def __init__(self, username, password):
        self.username = username
        self.password = password

def get_message(message):
    headers = {
        'Content-Type':'application/x-www-form-urlencoded',
    }
    API_ENDPOINT = 'https://api.simsimi.vn/v1/simtalk'
    data = {
        'text' : message,
        'lc' : 'vn',
        'key' : ''
    }
    res = requests.post(url = API_ENDPOINT, headers=headers, data=data)
    json_text = json.loads(res.text)
    return json_text['message']

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
        notification = ["Account created! Please log in again", 1]
        flash(notification)
        return redirect(url_for("log_in"))
    return render_template('signup.html')

#Users Observing
@app.route("/users")
def user_list():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template("list.html", users=users)

@app.route("/about")
def about_us():
    return render_template('about.html')

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
@socketio.on('message')
def handle_message(message):
    print('Receive message : ' + message)
    # print(get_message(message))
    send(message, broadcast=True)
    send(get_message(message), broadcast=True)
@app.route('/general_chat')
def general_chat():
    return render_template('general_chat.html')

@app.route('/app')
def emilia_chat():
    return render_template('emilia_chat.html')

@app.route('/rem_chat')
def rem_chat():
    return render_template('rem_chat.html')

#Running website
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
#Including libraries and modules
from module.lib import *
from module.emilia import *
from module.ram import *
from module.code_runner import *
# from module.code_runner import *
#Initing app
app = Flask(__name__)
app.config['SECRET_KEY'] = "2b3ifbf302f9nc1j2po1jewkajsd"
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 1024*1024*10
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=10)
#Database connection
db = SQLAlchemy()
db.init_app(app)
#SocketIO connection
socketio = SocketIO(app, cors_allowed_origin="*")

#Class of database 
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    avatar = db.Column(db.String)
    chat = db.Column(db.String, nullable=True)
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.avatar = 'admin.jpg'
        self.chat = ''

#Home Page
@app.route('/', methods=["POST", "GET"])
def log_in():
    found_user = User.query.filter_by(username="admin").first()
    if (found_user == None):
        user = User("admin", "123")
        db.session.add(user)
        db.session.commit()
    if (request.method == "POST"):
        username = request.form["username"]
        password = request.form["password"]
        found_user = User.query.filter_by(username=username).first()
        if (found_user == None):
            flash("Username not found", "info")
            return redirect(url_for("log_in"))
        if (password != found_user.password) :
            flash("Wrong password", "info")
            return redirect(url_for("log_in"))
        session["user"] = username
        user = User(username, password)
        if (found_user == None):
            db.session.add(user)
            db.session.commit()
        return redirect(url_for("dash_board"))
    if "user" in session:
        return redirect(url_for("dash_board"))
    return render_template('home.html')

#Sign up page
@app.route('/signup', methods=["POST", "GET"])
def sign_up():
    if (request.method == "POST"):
        username = request.form["username"]
        password = request.form["password"]
        rpassword = request.form["rpassword"]
        if (password != rpassword):
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

# @app.route('/test', methods=["POST", "GET"])
# def test():
#     return render_template('test.html')

#Users Observing
@app.route("/users")
def users():
    user_list = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template("list.html", users=user_list)

#About us
@app.route("/about")
def about_us():
    return render_template('about.html')

#Logging out
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

#General chat
@socketio.on('message')
def handle_message(message):
    found_user = User.query.filter_by(username="admin").first()
    found_user.chat = found_user.chat + "####" + message
    print(found_user.chat.split("####"))
    db.session.commit()
    print('Receive message : ' + message)
    elem = message.split("$$$$")
    found_user2 = User.query.filter_by(username=elem[0]).first()
    elem.append(found_user2.avatar)
    send(elem, broadcast=True)
@app.route('/general_chat')
def general_chat():
    found_user = User.query.filter_by(username="admin").first()
    all_chat = found_user.chat.split("####")
    all_chat2 = []
    for i in range(1, len(all_chat)):
        elem = all_chat[i].split("$$$$")
        found_user2 = User.query.filter_by(username=elem[0]).first()
        elem.append(found_user2.avatar)
        print(elem)
        all_chat2.append(elem)
    if "user" in session:
        name = session["user"]
        return render_template('general_chat.html', user=name, all_chat=all_chat2)
    else :
        return redirect(url_for("log_in"))

#Chat with emilia
@app.route('/app', methods=["POST", "GET"])
def emilia_chat():
    if "user" in session:
        name = session["user"]
        return render_template('emilia_chat.html', user=name)
    else :
        return redirect(url_for("log_in"))
@app.route('/get_emilia_message', methods=["POST", "GET"])
def get_emilia_message():
    name = request.form.get('name')
    message = request.form.get('msg')
    found_user = User.query.filter_by(username=name).first()
    print(name)
    return [get_emilia_response(unidecode.unidecode(message)), name, found_user.avatar]

#Chat with Ram
@app.route('/ram_chat', methods=["POST", "GET"])
def ram_chat():
    if "user" in session:
        name = session["user"]
        return render_template('ram_chat.html', user=name)
    else :
        return redirect(url_for("log_in"))
@app.route('/get_ram_message', methods=["POST", "GET"])
def get_ram_message():
    name = request.form.get('name')
    message = request.form.get('msg')
    found_user = User.query.filter_by(username=name).first()
    print(name)
    return [get_ram_response(message), name, found_user.avatar]

#Code Runner
@app.route('/code_runner', methods=["POST", "GET"])
def run():
    return render_template('code_runner.html')
@app.route('/runcode', methods=["POST", "GET"])
def print_result():
    language = request.form.get('language')
    code = request.form.get('code')
    input = request.form.get('input')
    res = run_code(language, code, input)
    return res 

#Storing media
@app.route('/store_media', methods=["POST","GET"])
def store_media():
    name = session["user"]
    found_user = User.query.filter_by(username=name).first()
    media_url = found_user.chat
    if request.method == "POST":
        media = request.files["new-media"]
        filename = media.filename
        arr = ["png", "jpg", "jpeg", "gif", "svg"]
        if (filename == ''):
            flash("Không có ảnh nào được gửi lên")
            return redirect(url_for("store_media"))
        if (filename.split('.')[1] not in arr):
            flash("File phải là hình ảnh có đuôi png, jpg, jpeg, gif, svg")
            return redirect(url_for("store_media"))
        else :
            filename = secure_filename(media.filename)
            storeFolder = 'static/store'
            if not os.path.exists(os.path.join(storeFolder, name)):
                os.makedirs(os.path.join(storeFolder, name))
            media.save(os.path.join(storeFolder+ '/' +name, filename))
            found_user.chat = found_user.chat + '$$$$' + filename
            db.session.commit()
        return redirect(url_for("store_media"))
    media_url = media_url.split('$$$$')
    real_media_url = []
    for i in range(1, len(media_url)):
        real_media_url.append(media_url[i])
    return render_template('store_media.html', media_url = real_media_url, user = name)

#Setting up
@app.route('/settingup', methods=["POST","GET"])
def setting_up():
    name = session["user"]
    found_user = User.query.filter_by(username=name).first()
    if request.method == "POST":
        avatar = request.files["new-avatar"]
        filename = avatar.filename
        arr = ["png", "jpg", "jpeg", "gif", "svg"]
        if (filename == ''):
            flash("Không có ảnh nào được gửi lên")
            return redirect(url_for("setting_up"))
        if (filename.split('.')[1] not in arr):
            flash("File phải là hình ảnh có đuôi png, jpg, jpeg, gif, svg")
            return redirect(url_for("setting_up"))
        else :
            filename = secure_filename(avatar.filename)
            filename = name + '.' + avatar.filename.rsplit('.')[1]
            avatar.save(os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename))
            found_user.avatar = filename
            db.session.commit()
    return render_template('setting_up.html', user = found_user.avatar)

@app.route('/clear_db', methods=["POST", "GET"])
def clear_db():
    user_list = db.session.execute(db.select(User.username).order_by(User.username)).scalars()
    if request.method == "POST":
        clear_user = request.form['clear_obj']
        found_user = User.query.filter_by(username=clear_user).first()
        found_user.chat = ''
        db.session.commit()
        storeFolder = 'static/store'
        if os.path.exists(os.path.join(storeFolder, clear_user)):
            shutil.rmtree(os.path.join(storeFolder, clear_user))
    return render_template('clear_db.html', user_list=user_list)

#Running website
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host="localhost", debug=True)
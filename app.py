import os
from flask import Flask, redirect, url_for, render_template, request, send_from_directory
app = Flask("__name__")

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'emilia.png')


@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def info():
    return render_template('index.html')

@app.route('/app')
def ad():
    return "ai chat"

@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == "__main__":
    app.run(debug=True)

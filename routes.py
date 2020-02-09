from flask import (
    flash, request, redirect, render_template, Flask
    )

DEBUG = True

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/play')
def play_quiz():
    return render_template("select_quiz.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    print(request.path)
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=DEBUG)
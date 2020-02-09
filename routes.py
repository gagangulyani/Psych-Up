from flask import (
    flash, request, redirect, render_template, Flask, url_for
)
from Forms.SignUp import SignupForm

DEBUG = True

app = Flask(__name__)
app.secret_key = 'a random string'


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


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        return redirect(url_for('/'))
    return render_template("signup.html", form=form)


if __name__ == "__main__":
    app.run(debug=DEBUG)

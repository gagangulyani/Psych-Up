from flask import (
    flash, request, redirect, render_template, Flask, url_for, make_response
)
from Forms.SignUp import SignupForm

DEBUG = True

app = Flask(__name__)
app.secret_key = 'a random string'


@app.route('/')
@app.route('/home')
def index():
    resp = make_response(render_template('index.html'))
    resp.set_cookie('SameSite', 'None', samesite="Lax", secure=True)
    resp.set_cookie('cross-site-cookie', 'None', samesite='Lax', secure=True)
    return resp


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
        flash(f"Welcome {form.name.data.split()[0]}!")
        return redirect(url_for('index'))
    return render_template("signup.html", form=form)


if __name__ == "__main__":
    app.run(debug=DEBUG)

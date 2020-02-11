from flask import (
    flash, request, redirect,
    render_template, Flask, url_for,
    make_response
)
from flask_login import (
    login_user, current_user,
    logout_user, LoginManager,
    login_required)
from flask_paranoid import Paranoid
from models.users import User
from Forms.SignUp import SignupForm
from Forms.Login import LoginForm
from uuid import uuid4
from bson import ObjectId

DEBUG = True

app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid4())

login_manager = LoginManager()


@login_manager.user_loader
def load_user(_id):
    if type(_id) is str:
        return User.get_user_info(
            _id=ObjectId(_id)
        )
    return User.get_user_info(
        _id=_id
    )


# Login Manager Config
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message_category = "info"

# For Preventing Multiple requests using same cookie from
# Multiple IPs
paranoid = Paranoid(app)
paranoid.redirect_view = '/'

User.load_user = classmethod(load_user)


@app.route('/')
@app.route('/home')
def index():
    template = 'index.html'
    if current_user.is_authenticated:
        if current_user.is_admin:
            template = "Admin Panel"
    resp = make_response(render_template(template))
    # for Chrome
    resp.set_cookie('SameSite', 'None', samesite="Lax", secure=True)
    resp.set_cookie('cross-site-cookie', 'None', samesite='Lax', secure=True)
    return resp

# @login_required


@app.route('/play')
def play_quiz():
    return render_template("select_quiz.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect('/', 302)

    form = LoginForm()

    if request.method == 'POST':
        if result := form.validate():
            # print("result:", result)
            login_user(
                User(
                    _id=str(result.get('_id')),
                    username=result.get('username'),
                    name=result.get('name')
                )
            )
            flash(f"Welcome {current_user.name.split()[0]}!")
            return redirect(f'/player/{current_user.username}', 302)

    return render_template('login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
@app.route('/signup/admin', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect('/', 302)

    is_admin = False

    form = SignupForm()

    if request.path == '/signup/admin':
        is_admin = True

    if request.method == "POST" and form.validate():
        User(
            username=str(uuid4()),
            email=form.email.data.lower(),
            password=form.password.data,
            name=form.name.data.title(),
            is_admin=is_admin
        ).save_user(signup=True)
        flash("Registration Completed! Please Login to Continue..")
        return redirect(url_for('index'))

    if is_admin:
        return render_template("signup_admin.html", form=form)
    return render_template("signup.html", form=form)


@app.route('/player/<string:username>')
def player(username):
    if len(username) != 36:
        flash('User Does Not Exist!')
        redirect('/', 302)

    user = User.get_user_info(username=username)
    return render_template("player.html", user=user)


@app.route('/logout')
def logout():
    fname = current_user.name.split()[0].capitalize()
    logout_user()
    flash(f'See You Next Time {fname}!')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=DEBUG)

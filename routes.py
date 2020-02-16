from flask import Flask, render_template
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
from models.quiz import Quiz
from Forms.SignUp import SignupForm
from Forms.Login import LoginForm
from Forms.Quiz import (AddQuestion,
                        EditQuestion)
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
            return redirect('/admin/dashboard', 302)
        else:
            if request.path in ['/admin', '/admin/dashboard']:
                return render_template("404.html")

    resp = make_response(render_template(template))
    # for Chrome
    resp.set_cookie('SameSite',
                    'None',
                    samesite="Lax",
                    secure=True)
    resp.set_cookie('cross-site-cookie',
                    'None',
                    samesite='Lax',
                    secure=True)
    return resp


@app.route('/admin/dashboard')
def admin_dashboard():
    if current_user.is_authenticated and current_user.is_admin:
        return render_template('admin_dashboard.html')
    return render_template("404.html")


@login_required
@app.route('/admin/dashboard/Quiz/add', methods=['GET', 'POST'])
@app.route('/admin/dashboard/Quiz/edit')
@app.route('/admin/dashboard/Quiz/edit/<string:qid>',
           methods=["GET", "POST"])
@app.route('/admin/dashboard/Quiz/delete')
@app.route('/admin/dashboard/Quiz/delete/<string:qid>',
           methods=["GET", "POST"])
def quiz_dashboard(qid=None):
    if not current_user.is_authenticated:
        flash('Login is Required for this action!')
        return redirect('/', 302)
    if not current_user.is_admin:
        flash('You need to be an Admin for Performing this action!')
        return redirect('/', 302)

    template = "_question.html"
    req_path = request.path.split('/')[-1]

    if qid and len(qid) > 24:
        return render_template('404.html')
    if req_path == qid:
        req_path = request.path.split('/')[-2]

    if req_path == 'add':
        form = AddQuestion()
        if request.method == "POST":
            if form.validate():
                sol = {
                    1: form.option1.data,
                    2: form.option2.data,
                    3: form.option3.data,
                    4: form.option4.data,
                }
                Quiz(
                    question=form.question.data,
                    options=[
                        form.option1.data,
                        form.option2.data,
                        form.option3.data,
                        form.option4.data,
                    ],
                    answer=sol.get(form.solution.data)
                ).save_quiz()
                flash('Question Saved Successfully!')
                return redirect('/admin/dashboard/Quiz/edit')
        return render_template('add' + template, form=form)

    elif req_path == 'edit':
        if not qid:
            questions = Quiz.get_questions(userID=None,
                                           show_history=True,
                                           is_admin=True)
            for question in questions:
                question._id = str(question._id)

            return render_template('display_questions.html', questions=questions)

        form = EditQuestion()
        question = Quiz.get_question(qid)
        if request.method == "POST":
            if form.validate_on_submit():
                if question:
                    question.question = form.question.data
                    question.options = [
                        form.option1.data,
                        form.option2.data,
                        form.option3.data,
                        form.option4.data
                    ]
                    sol = {
                        1: form.option1.data,
                        2: form.option2.data,
                        3: form.option3.data,
                        4: form.option4.data,
                    }
                    question.answer = sol.get(form.solution.data)
                    question.update_quiz_info()
                    # print('Quiz updated!')
                    flash('Question Edited Successfully!')
                    return redirect('/admin/dashboard/Quiz/edit')
                else:
                    flash('Unable to find Question in DB')
                    return redirect('/')
            else:
                flash("Couldn't Validate form..")
                # print(form.validate_on_submit())
                return render_template('edit' + template, form=form)

        if question:
            form.solution.default = question.options.index(
                question.answer
            ) + 1
            form.process()
            form.question.data = question.question
            form.option1.data = question.options[0]
            form.option2.data = question.options[1]
            form.option3.data = question.options[2]
            form.option4.data = question.options[3]
            # form.process()

        return render_template('edit' + template, form=form)

    elif req_path == 'delete' or qid:
        if request.method == "POST" and qid:
            # print(help(Quiz.DB.CURSOR.delete_one))
            Quiz.DB.CURSOR.Quiz.delete_one({'_id': ObjectId(qid)})
            flash('Question Deleted!')
            return redirect('/admin/dashboard/Quiz/delete')

        if not qid:
            questions = Quiz.get_questions(userID=None,
                                           show_history=True,
                                           is_admin=True)
            for question in questions:
                question._id = str(question._id)

            return render_template('display_questions.html', questions=questions)
        return render_template('delete_question.html')
    else:
        return render_template('404.html')


@login_required
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
            if result.get('is_admin'):
                return redirect('/admin/dashboard')
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
        flash("Registration Completed! Please Login..")
        return redirect(url_for('index'))

    if is_admin:
        return render_template("signup_admin.html", form=form)
    return render_template("signup.html", form=form)


@app.route('/player/<string:username>')
def player(username):
    if len(username) != 36:
        flash('User Does Not Exist!')
        return redirect('/', 302)

    user = User.get_user_info(username=username)
    return render_template("player.html", user=user)


@app.route('/followers/<string:username>')
def followers(username):
    if not username and len(username) != 36:
        flash("User Not Found!")
        return redirect('/', 302)
    user = User.get_user_info(username=username)
    if user:
        return render_template('followers.html', user=user, enumerate=enumerate)
    flash("User Not Found!")
    return redirect('/', 302)


@app.route('/following/<string:username>')
def following(username):
    if not username and len(username) != 36:
        flash("User Not Found!")
        return redirect('/', 302)
    user = User.get_user_info(username=username)
    if user:
        return render_template('following.html', user=user, enumerate=enumerate)
    flash("User Not Found!")
    return redirect('/', 302)


@app.route('/follow/<string:username>')
def follow(username):
    if not username and len(username) != 36:
        flash("User Not Found!")
        return redirect('/', 302)

    if current_user.is_authenticated:
        user = User.get_user_info(username=username)
        if user and current_user.follow_user(user):
            return redirect(f'/player/{username}')
        flash("User Not Found!")
        return redirect('/', 302)
    flash('Please Login before this action!')
    return redirect('/', 302)


@app.route('/unfollow/<string:username>')
def unfollow(username):
    if not username and len(username) != 36:
        flash("User Not Found!")
        return redirect('/', 302)

    if current_user.is_authenticated:
        user = User.get_user_info(username=username)
        if user and current_user.unfollow_user(user):
            return redirect(f'/player/{username}')
        flash("User Not Found!")
        return redirect('/', 302)
    flash('Please Login before this action!')
    return redirect('/', 302)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        fname = current_user.name.split()[0].capitalize()
        logout_user()
        flash(f'See You Next Time {fname}!')
    return redirect('/')


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=DEBUG)

from bson import ObjectId
from uuid import uuid4
from flask import Flask, render_template
from flask import (flash, request, redirect, render_template,
                   Flask, url_for, make_response, session)
from flask_login import (login_user, current_user, logout_user,
                         LoginManager, login_required)
from flask_paranoid import Paranoid
from models.users import User
from models.quiz import Quiz
from models.history import History
from models.contact import Contact
from Forms.SignUp import SignupForm
from Forms.Login import LoginForm
from Forms.Quiz import AddQuestion, EditQuestion, Play
from Forms.Settings import SettingsForm
from Forms.Contact import ContactForm
from random import randint

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

# print(History.show_history())


@app.context_processor
def inject_stage_and_region():
    return dict(
        enumerate=enumerate,
        leaderboard=History.show_history()
    )


# Login Manager Config
login_manager.init_app(app)
login_manager.session_protection = None  # for flask paranoid
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
        messages = Contact.get_messages()
        return render_template(
            'admin_dashboard.html',
            messages=messages,
            zip=zip,
            range=range, len=len,
            str=str
        )
    return render_template("404.html")


@app.route('/leaderboard')
def leaderboard():
    if not History.show_history():
        flash('No Player Data is available at the moment')
        return redirect('/')
    return render_template('leaderboard.html')


@login_required
@app.route('/admin/dashboard/Players/view')
@app.route('/admin/dashboard/Players/remove')
@app.route('/admin/dashboard/Players/remove/<string:pid>', methods=['GET', 'POST'])
def player_dashboard(pid=None):
    if current_user.is_authenticated and current_user.is_admin:
        players = User.get_all_users()
        if request.path == '/admin/dashboard/Players/view':
            return render_template('view_players.html', players=players)

        elif pid and len(pid) < 100 and (pid.replace('-', '').isalnum() or pid.replace('_', '').isalnum()):
            if not User.get_user_info(username=pid):
                flash('Can\'t find player')
                return redirect('/admin/dashboard/Players/view')

            if request.method == "POST":
                Quiz.remove_player(pid)
                flash('Player Removed!')
                return redirect('/admin/dashboard/Players/view')
            return render_template('remove_player.html', players=players)

        return render_template('view_players.html', players=players)
    return render_template('404.html')


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
                                           is_admin=True, limit=1000)
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
                                           is_admin=True, limit=1000)
            for question in questions:
                question._id = str(question._id)

            return render_template('display_questions.html', questions=questions)
        return render_template('delete_question.html')
    else:
        return render_template('404.html')


@login_required
@app.route('/final_score')
def display_score():
    if session.get('score') != None:
        current_user.total_score += session.get('score')
        current_user.update_user_info()
        score = session.pop('score')
        History.find_and_update(userID=current_user._id, score=score)
        return render_template('final_score.html', score=score)
    else:
        flash('You haven\'t played the Quiz yet!')
        return redirect('/')


@login_required
@app.route('/play', methods=['GET', 'POST'])
@app.route('/play/<string:qid>', methods=["POST"])
def play_quiz(qid=None):
    form = Play()
    if not current_user.is_authenticated:
        flash('Please Login for playing Quiz..')
        return redirect('/login')
    if request.method == "POST":
        if form.validate():
            if question := Quiz.get_question(form.qid.data):
                if Quiz.attempt_question(current_user, form.ans.data, question):
                    session['score'] += 10
                    return redirect('/play')
                else:
                    return redirect('/final_score')
            return render_template('404.html')
        else:
            errors = []
            errors.append(form.qid.errors)
            errors.append(form.ans.errors)
            errors.append(form.current_score.errors)
            errors.append(form.correct_ans.errors)
            if qid:
                return redirect('/play/')
            return str(errors)

    if not qid:
        if question := Quiz.get_questions(current_user._id, sample=1):
            # question is a list with one element
            question = question[0]  # accessing that element

            form.qid.data = str(question._id)
            if not form.current_score.data:
                form.current_score.data = 0
            form.correct_ans.data = question.answer
        else:
            flash('Well Done! You have reached the end of the Quiz!')
            if session.get('score') != None and session.get('score') > 0:
                current_user.total_wins += 1
                current_user.update_user_info()
                return redirect('/final_score')
            return redirect('/')

    score = form.current_score.data

    if session.get('score'):
        score += session.get('score')
        form.current_score.data += session.get('score')
    else:
        session['score'] = score = 0

    return render_template(
        "main_quiz.html",
        form=form,
        quiz=question,
        score=score
    )


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
    if len(username) > 36:
        flash('User Does Not Exist!')
        return redirect('/', 302)

    user = User.get_user_info(username=username)
    return render_template("player.html", user=user)


@app.route('/followers/<string:username>')
def followers(username):
    if not username and len(username) > 36:
        flash("User Not Found!")
        return redirect('/', 302)
    user = User.get_user_info(username=username)
    if user:
        return render_template('followers.html', user=user)
    flash("User Not Found!")
    return redirect('/', 302)


@app.route('/following/<string:username>')
def following(username):
    if not username and len(username) > 36:
        flash("User Not Found!")
        return redirect('/', 302)
    user = User.get_user_info(username=username)
    if user:
        return render_template('following.html', user=user)
    flash("User Not Found!")
    return redirect('/', 302)


@app.route('/follow/<string:username>')
def follow(username):
    if not username and len(username) > 36:
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
    if not username and len(username) > 36:
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


@app.route('/settings', methods=['GET', 'POST'])
@app.route('/settings/delete', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_authenticated:
        flash('Please Login to continue..')
        return redirect('/login')

    user = current_user

    form = SettingsForm()

    form.name.render_kw = {'placeholder': user.name}
    form.username.render_kw = {'placeholder': user.username}
    form.email.render_kw = {'placeholder': user.email}

    if request.method == 'GET':
        if request.path == '/settings/delete':
            return render_template('confirm_remove.html')
        return render_template('settings.html', user=user, form=form)

    elif request.method == 'POST':
        if request.path == '/settings/delete':
            Quiz.remove_player(user.username)
            flash('Sorry to see you go :(')
            flash('You will be missed..')
            return redirect('/')

        if form.validate():
            if form.name.data.strip() and user.name != form.name.data.strip():
                user.name = form.name.data.strip()
                form.name.render_kw = {'placeholder': form.name.data}
                user.update_user_info()
                flash('Name Updated Successfully!')
            if form.username.data.strip() and user.username != form.username.data.strip():
                user.username = form.username.data.strip().lower()
                form.username.render_kw = {
                    'placeholder': form.username.data.strip().lower()}
                user.update_user_info()
                flash('Username Updated Successfully!')
            if form.email.data.strip() and user.email != form.email.data.strip():
                user.email = form.email.data.strip().lower()
                form.email.render_kw = {
                    'placeholder': form.email.data.strip().lower()}
                user.update_user_info()
                flash('Email Address Updated Successfully!')
            if form.password.data and len(form.password.data) in [i for i in range(8, 17)]:
                user.password = form.password.data
                user.update_user_info(settings=True)
                flash('Password Updated Successfully!')

            form.email.data = form.name.data = form.username.data = ""
        return render_template('settings.html', user=user, form=form)

    return render_template('404.html')


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


@app.route('/about/how')
@app.route('/about/why')
@app.route('/about/who')
def about():
    path = request.path.split('/')[-1]
    return render_template(f'about_{path}.html')


@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contact/delete/<string:mid>', methods=['GET', 'POST'])
def contact(mid=None):
    if request.path == '/contact':
        form = ContactForm()
        if current_user.is_authenticated:
            form.email.data = current_user.email
            form.name.data = current_user.name

        if request.method == 'POST':
            if form.validate():
                Contact(
                    email=form.email.data,
                    title=form.title.data,
                    name=form.name.data,
                    message=form.message.data
                ).save_message()
                flash('Message Sent to Admin!')
                return redirect('/')
        return render_template('contact.html', form=form)

    if current_user.is_authenticated:
        if current_user.is_admin and mid and len(mid) == 24 and mid.isalnum():
            if Contact.get_message(mid):
                if request.method == 'POST':
                    Contact.delete_message(mid)
                    flash('Message Deleted!')
                    return redirect('/')
                return render_template(
                    'confirm_message_delete.html',
                    mid=mid
                )
            return redirect('/')
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=DEBUG)

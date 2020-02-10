from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField,
                     PasswordField,)
from models.users import User
from models.database import Database
from wtforms.validators import (InputRequired,
                                Length)
from customValidators import (checkForJunk,
                              StrongPassword, isUser, isUser2)


class LoginForm(FlaskForm):

    email = StringField("Email Address or Username", validators=[
        InputRequired(
            'Please Enter your Username Or Email Address'),
        Length(min=4, max=100,
               message='Invalid Username'), isUser2],
        render_kw={"placeholder": "Enter Email Address or Username"})

    password = PasswordField(validators=[
        InputRequired('Please Enter your Password'),
        Length(8, 16, "Invalid Password!")],
        render_kw={"placeholder": "Password"})

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if len(self.password.data) > 16:
            return None
        else:
            result = User.login(self.email.data, self.password.data)

        if result is None:
            self.email.errors = ['Account Not Found!']
            return False

        elif result is False:
            self.password.errors.append('Incorrect Password!')
            return False

        else:
            return result

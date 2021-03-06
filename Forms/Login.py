from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import InputRequired, Length

from Forms.customValidators import (StrongPassword, checkForJunk, isUser,
                                    isUser2)
from models.database import Database
from models.users import User


class LoginForm(FlaskForm):

    email = StringField("Email Address or Username", validators=[
        InputRequired(
            'Please Enter your Username Or Email Address'), isUser2],
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
            result = User.login(self.email.data.lower(), self.password.data)
            print("FORM DATA:\nemail, password")
            print(*[self.email.data, self.password.data])
            print("\nForm Result :", result)
            
        if result is None:
            self.email.errors = ['Account Not Found!!']
            return False

        elif result is False:
            self.password.errors.append('Incorrect Password!')
            return False

        else:
            return result

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email


class SignupForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired("Name is Required for Signing Up")])
    email = StringField("Email", validators=[InputRequired("Email is Required for Signing Up"), Email("Invalid Email Address")])
    password = PasswordField("Password", validators=[InputRequired("Password is required for Signing Up")])
    cpassword = PasswordField("Confirm Password", validators=[InputRequired("Password needs to be confirmed for Signing Up")])
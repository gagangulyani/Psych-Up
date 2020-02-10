from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo, Length
from Forms.customValidators import StrongPassword, isUser, checkForJunk


class SignupForm(FlaskForm):

    name = StringField('Name', validators=[
                       InputRequired("Name is Required for Signing Up"), checkForJunk])

    email = StringField("Email",
                        validators=[
                            InputRequired(
                                "Email is Required for Signing Up"),
                            Email("Invalid Email Address"),
                            Length(5,
                                   100,
                                   message="Please Enter a valid email address"),
                            isUser
                        ]
                        )

    password = PasswordField("Password",
                             validators=[
                                 InputRequired(
                                     "Password is required for Signing Up"),
                                 Length(
                                     min=8,
                                     max=16,
                                     message="Password Must be between 8 to 16 Characters long"
                                 )
                             ]
                             )

    cpassword = PasswordField("Confirm Password",
                              validators=[
                                  InputRequired(
                                      "Password needs to be confirmed for Signing Up"),
                                  EqualTo("password", "Passwords does not match")
                              ]
                              )

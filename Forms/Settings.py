from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Email

from Forms.customValidators import (StrongPassword, checkForJunk, isUser,
                                    Length_custom, isEmailAddress,
                                    Length_Email)
from models.database import Database
from models.users import User


class SettingsForm(FlaskForm):
    name = StringField(
        'Change Name', validators=[
            Length_custom, checkForJunk
        ])

    email = StringField("Change Email Address", validators=[
        Length_Email, isEmailAddress, isUser])

    username = StringField("Change Username", validators=[
        Length_custom, isUser, checkForJunk])

    password = PasswordField("Change Password", validators=[
        Length_custom, StrongPassword],
        render_kw={'placeholder': 'Must have atleast 8 characters'}
    )

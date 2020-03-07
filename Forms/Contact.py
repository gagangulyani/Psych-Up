from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length, Email

from Forms.customValidators import checkForJunkContact, checkEmpty


class ContactForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            InputRequired(),
            Length(8,50),
            checkEmpty
        ],
        render_kw={'placeholder': 'Enter Name here..'}
    )
    email = StringField(
        "Email Address",
        validators=[
            InputRequired(),
            Length(10,60),
            Email()
        ],
        render_kw={'placeholder': 'Enter Email Address here..'}
    )
    title = StringField(
        "Title",
        validators=[
            InputRequired(),
            Length(8,30),
            checkForJunkContact,
            checkEmpty
        ],
        render_kw={'placeholder': 'Enter Title Here...'}
    )
    message = StringField(
        "Message",
        validators=[
            InputRequired(),
            Length(8,200),
            checkForJunkContact,
        ],
        render_kw={'placeholder':"Enter Message Here..."}
    )

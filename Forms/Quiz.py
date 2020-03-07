from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField,
                     HiddenField, IntegerField)
from wtforms.validators import InputRequired, Length, NumberRange
from wtforms.widgets import HiddenInput


class AddQuestion(FlaskForm):

    question = TextAreaField(
        validators=[
            Length(20, 150,)
        ], render_kw={
            "placeholder": "Write your Question",
            "rows": "3",
        }

    )

    option1 = StringField(
        validators=[
            Length(5, 30)
        ], render_kw={"placeholder": "Option #1"},)

    option2 = StringField(
        validators=[
            Length(5, 30, )
        ], render_kw={"placeholder": "Option #2"},)

    option3 = StringField(
        validators=[
            Length(5, 30, )
        ], render_kw={"placeholder": "Option #3"},)

    option4 = StringField(
        validators=[
            Length(5, 30, )
        ], render_kw={"placeholder": "Option #4"},)

    solution = SelectField('Choose Option as Solution',
                           choices=[
                               (1, "Option #1"),
                               (2, "Option #2"),
                               (3, "Option #3"),
                               (4, "Option #4")
                           ],
                           default=1,
                           coerce=int
                           )


class EditQuestion(AddQuestion):
    pass


class Play(FlaskForm):

    qid = HiddenField(validators=[
        InputRequired()])

    ans = HiddenField(validators=[
        InputRequired()])

    current_score = IntegerField(validators=[
        InputRequired(),
        NumberRange(min=0)], widget=HiddenInput())

    correct_ans = HiddenField(validators=[
        InputRequired()])

from flask_wtf import FlaskForm
from wtforms import SelectField
from flask import render_template
from wtforms.fields.simple import SubmitField


class TeachingTaskForm(FlaskForm):
    teacher = SelectField('Teacher', coerce=int)  # Coerce to int for selecting teacher ID
    subject = SelectField('Subject', coerce=int)
    classroom = SelectField('Classroom', coerce=int)
    semester = SelectField('Semester', coerce=int)
    year = SelectField('Year', coerce=int)
    submit = SubmitField('Submit')

from flask_wtf import FlaskForm
from wtforms import SelectField

class ThesisFilter(FlaskForm):
    worktype = SelectField('worktype', choices=[])


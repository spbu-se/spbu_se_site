from flask_wtf import FlaskForm
from wtforms import SelectField

class ThesisFilter(FlaskForm):
    worktype = SelectField('worktype', choices=[])
    supervisor = SelectField('supervisor', choices=[])
    startdate = SelectField('worktype', choices=[])
    enddate = SelectField('worktype', choices=[])

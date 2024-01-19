from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, DateField
from wtforms.validators import DataRequired, URL


class NewEmployee(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('addrss', validators=[DataRequired()])
    contact = StringField('contact', validators=[DataRequired()])
    idnumber = StringField('idnumber', validators=[DataRequired()])
    machine = StringField('machine', validators=[DataRequired()])
    startdate = DateField('startdate', validators=[DataRequired()])
    enddate = DateField('enddate', validators=[DataRequired()])
    vehiclereg = StringField('vehiclereg', validators=[DataRequired()])
    submit = SubmitField('submit')
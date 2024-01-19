from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, EmailField, StringField
from wtforms.validators import DataRequired, URL


class EditLead(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    number = StringField('number', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    area = StringField('area', validators=[DataRequired()])
    amount = StringField('amount', validators=[DataRequired()])
    status = StringField('status', validators=[DataRequired()])
    services = StringField('services', validators=[DataRequired()])
    comments = StringField('comments', validators=[DataRequired()])
    submit = SubmitField('submit')
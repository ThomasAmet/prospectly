from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo, Optional
from app.models import distinct_activity_values

class LeadsQueryForm(FlaskForm):
	activity_field = SelectField('Business Activity', choices=distinct_activity_values(), validators=[DataRequired()])
	postal_code = StringField('Postal Code', validators=[Optional(), Regexp('^[0-9]{2,5}$', 0, 'Vous devez entrez au moins 2 chiffres. Ex: 75 or 75001')])
	# postal_code = StringField('Postal Code')

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo, Optional
from app.models import companies_activity_values

class CompaniesQueryForm(FlaskForm):
	company_activity_field = SelectField('Business Activity', choices=companies_activity_values(), validators=[DataRequired()])
	company_postal_code = StringField('Postal Code', validators=[Optional(), Regexp('^[0-9]{2,5}$', 0, 'Vous devez entrez au moins 2 chiffres. Ex: 75 or 75001')])
	# postal_code = StringField('Postal Code')

class ContactsQueryForm(FlaskForm):
	some_field = StringField()
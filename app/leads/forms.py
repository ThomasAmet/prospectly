from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo, Optional
from app.models import distinct_companies_activity_values, distinct_status_values

class CompaniesQueryForm(FlaskForm):
	company_activity_field = SelectField('Business Activity')
	company_postal_code = StringField('Postal Code', validators=[Optional(), Regexp('^[0-9]{2,5}$', 0, 'Vous devez entrez au moins 2 chiffres. Ex: 75 or 75001')])
	# postal_code = StringField('Postal Code')

	def __init__(self, *args, **kwargs):
		super(CompaniesQueryForm, self).__init__(*args, **kwargs)
		self.company_activity_field.choices = distinct_companies_activity_values()

class ContactsQueryForm(FlaskForm):
	some_field = StringField()


class LeadsQueryForm(FlaskForm):
	company_activity_field = SelectField('Business Activity', choices=[])
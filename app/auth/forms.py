from ..models import *
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo

import logging
logging.basicConfig(level=logging.INFO)

csrf = CSRFProtect()



class LoginForm(FlaskForm):
	email = StringField('Email:',
						validators=[DataRequired(message='You must provide an email'),
									Email(message='Oups... Cet email est invalide.')])
	password = PasswordField('Mot de passe:', validators=[DataRequired()])
	remember_me = BooleanField('Se souvenir de moi')
	submit = SubmitField('Se connecter')



class RegistrationForm(FlaskForm):
	first_name = StringField('Prenom', validators=[DataRequired(), Regexp('^[A-Za-z][A-Za-z]*$', 0,
		'Usernames must have only letters')])
	last_name = StringField('Nom', validators=[DataRequired(), Regexp('^[A-Za-z][A-Za-z]*$', 0,
    	'Usernames must have only letters')])
	email = StringField('Email', validators=[DataRequired(), Email(message='This is not an email format')])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
	submit = SubmitField('Register')

	# When a form has a method with prefix 'validate', the method is invoked along with regular validators of the field the validate function is applied on 
	def validate_first_name(self, first_name):
		'''
			Concatenate the first name and last name provided to check.
			Raise an error if an existing user has the same names
		'''
		username = str(first_name.data).capitalize() + '_' + str(self.last_name.data).capitalize()
		user = User.query.filter_by(username=username).first()
		if user is not None:
			raise ValidationError('Please use a different name.')

	def validate_last_name(self, last_name):
		'''
			Same as above but the validation is operated on the last_name field rather than first_name
		'''
		username = str(self.first_name.data).capitalize() + '_' + str(last_name.data).capitalize()
		user = User.query.filter_by(username=username).first()
		if user is not None:
			raise ValidationError('Please use a different name.')

	def validate_email(self, email):
		'''
			Check wheter a user already register with that email
		'''
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')

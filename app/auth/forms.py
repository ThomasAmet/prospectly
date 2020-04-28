from ..models import *
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo

import logging
logging.basicConfig(level=logging.INFO)

csrf = CSRFProtect()

class RequestNewPasswordForm(FlaskForm):
	email = StringField('Email:',
						validators=[DataRequired(message="Il faut un email pour se connecter."),
									Email(message="Oups... Ce n'est pas un format valide.")])
	submit = SubmitField('Se connecter')



class SetPasswordForm(FlaskForm):
	password = PasswordField('Mot de passe:', validators=[DataRequired()])
	password_confirmation = PasswordField('Confirmez le mot de passe', validators=[DataRequired(), EqualTo('password', message='Les mots de passse ne correspondent pas.')])
	
	
class LoginForm(FlaskForm):
	email = StringField('Email:',
						validators=[DataRequired(message="Il faut un email pour se connecter."),
									Email(message='Oups... Cet email est invalide.')])
	password = PasswordField('Mot de passe:', validators=[DataRequired()])
	remember_me = BooleanField('Se souvenir de moi')
	submit = SubmitField('Se connecter')

	def prepopulate_values(self, email):
		self.email = email



class RegistrationForm(FlaskForm):
	# first_name = StringField('Prenom', validators=[DataRequired(message="Merci de remplir votre prenom"), Regexp('^[A-Za-z][A-Za-z]*$', 0,
	# 	'Les prenoms peuvent seulement contenir des lettres')])
	# last_name = StringField('Nom', validators=[DataRequired(message="Merci de remplir votre nom"), Regexp('^[A-Za-z][A-Za-z]*$', 0,
 #    	'Les noms peuvent seulement contenir des lettres')])
	first_name = StringField('Prenom', validators=[DataRequired(message="Merci de remplir votre prenom")])
	last_name = StringField('Nom', validators=[DataRequired(message="Merci de remplir votre nom")])
	
	email = StringField('Email', validators=[DataRequired("Il faut un email pour s'inscrire."), Email(message='Oups... Cet email est invalide.')])
	# password = PasswordField('Password', validators=[DataRequired("Aucun mot de passe detecte.")])
	# password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Les mots de passse ne correspondent pas.')])
	# mobile = StringField('Telephone Mobile (06 ou 07)', validators=[DataRequired(message='Merci de remplir votre numero mobile.'), Regexp('^((06)|(07))[0-9]{8}$', 0, message='Oups ce numero est invalide')])
	submit = SubmitField("Créer un compte")
	
	# When a form has a method with prefix 'validate', the method is invoked along with regular validators of the field the validate function is applied on 
	# def validate_first_name(self, first_name):
	# 	'''
	# 		Concatenate the first name and last name provided to check.
	# 		Raise an error if an existing user has the same names
	# 	'''
	# 	username = str(first_name.data).capitalize() + '_' + str(self.last_name.data).capitalize()
	# 	user = User.query.filter_by(username=username).first()
	# 	if user is not None:
	# 		raise ValidationError("Ce nom d'utilisateur est deja pris.")

	# def validate_last_name(self, last_name):
	# 	'''
	# 		Same as above but the validation is operated on the last_name field rather than first_name
	# 	'''
	# 	username = str(self.first_name.data).capitalize() + '_' + str(last_name.data).capitalize()
	# 	user = User.query.filter_by(username=username).first()
	# 	if user is not None:
	# 		raise ValidationError("Ce nom d'utilisateur existe. Merci de changer le prénom ou le nom.")

	# def validate_email(self, email):
	# 	'''
	# 		Check wheter a user already register with that email
	# 	'''
	# 	user = User.query.filter_by(email=email.data).first()
	# 	if user is not None:
	# 		raise ValidationError()#'Please use a different email address.'

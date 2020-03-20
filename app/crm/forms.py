from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, DecimalField, RadioField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo, Optional
from ..models import Company, distinct_status_values, distinct_stages_values, distinct_priority_values
from flask_login import current_user
# é


def company_choices():
	#result = Contact.query.filter(Contact.postal_code.like('94%'))
	return Company.query.filter(Company.user_id==current_user.id)

class CompanyForm(FlaskForm):
	name = StringField("Nom de l'opportunité", validators=[DataRequired()])
	activity_field = StringField("Domaine d'activité", validators=[DataRequired()])#choice from exisitng + free
	email = StringField("Email", validators=[Email()], default=None)
	phone = StringField("Téléphone", validators=[Regexp('0[0-9]{9}', 0, 'Le format doit être de la forme 0XXXXXXXXX')], default=None)
	address = StringField("Adresse", default=None)
	postal_code = StringField("Code Postal", default=None)
	city = StringField("Ville", default=None)
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)], default=None)
	website = StringField('Site web', default=None)
	facebook = StringField('Page Facebook', default=None)
	instagram = StringField('Page Instagram web')
	linkedin = StringField('Page LinkedIn')


class AddContactForm(FlaskForm):
	first_name = StringField('Prénom', validators=[DataRequired('Champ obligatoire')])
	last_name = StringField('Nom', validators=[DataRequired('Champ obligatoire')])
	company_id = QuerySelectField("Entreprise", query_factory=company_choices, allow_blank=True)
	position = StringField('Rôle', validators=[Optional()])
	email = StringField('Email', validators=[Optional(), Email("Cet email n'est pas valide")])
	# is_email_main = RadioField("Type d'email", choices=[('True','Email principal'),('False','Email secondaire')], default='Professionnel') #whether email is main email
	phone = StringField("Téléphone", validators=[Regexp('0[0-9]{9}', 0, 'Le format doit être de la forme 0XXXXXXXXX')])
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)])
	facebook = StringField('Page Facebook')
	instagram = StringField('Page Instagram web')
	linkedin = StringField('Page LinkedIn')
	# submit = SubmitField('Créer')

class EditContactForm(FlaskForm):
	first_name = StringField('Prénom', validators=[DataRequired('Champ obligatoire')])
	last_name = StringField('Nom', validators=[DataRequired('Champ obligatoire')])
	company_id = QuerySelectField("Entreprise", query_factory=company_choices, allow_blank=True)
	position = StringField('Rôle', validators=[Optional()])
	email = StringField('Email', validators=[Optional(), Email("Cet email n'est pas valide")])
	# is_email_main = RadioField("Type d'email", choices=[('True','Email principal'),('False','Email secondaire')], default='Professionnel') #whether email is main email
	phone = StringField("Téléphone", validators=[Regexp('0[0-9]{9}', 0, 'Le format doit être de la forme 0XXXXXXXXX')])
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)])
	facebook = StringField('Page Facebook')
	instagram = StringField('Page Instagram web')
	linkedin = StringField('Page LinkedIn')
	# submit = SubmitField('Créer')


class AddOpportunityForm(FlaskForm):
	company = QuerySelectField("Entreprise", query_factory=company_choices, allow_blank=False)# when selecting a choice it return company's id. Add arg 'get_label=company_name' if we just want to return company's name instead
	name = StringField("Nom de l'opportunité", validators=[DataRequired()])
	euros_value = DecimalField("Montant (en €)", default=0, places=2)
	stage = SelectField(u'Etape Commerciale', choices=distinct_stages_values(), validators=[DataRequired()])
	status = SelectField('Status', choices=distinct_status_values(), default='En attente', validators=[DataRequired()]) #list(distinct_status_values())[2][0]
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)], default=None)
	task_title = StringField('Nom de la tâche', validators=[Optional()], default=None)
	task_content = TextAreaField('Descriptif', validators=[Optional(), Length(max=200)], default=None)
	task_priority = SelectField('Priorité', choices=distinct_priority_values(), validators=[Optional()])	
	# task_due_date = DateField('A faire pour:', format='%Y-%m-%d', validators=[Optional()], default=None)

	# Define choices within _init__ to prevent error when manually initiating choices
	def __init__(self, *args, **kwargs):
		super(AddOpportunityForm, self).__init__(*args, **kwargs)
		self.stage.choices = distinct_stages_values()
		self.status.choices = distinct_status_values()
		self.task_priority.choices = distinct_priority_values()

	def validate_task_fields(self):
		if not ((self.task_title.data and self.task_content.data) and self.task_priority.data):
			return False
		else:
			return True

			
class EditOpportunityForm(FlaskForm):
	# Fields regarding the Opportunity
	company = QuerySelectField("Entreprise", query_factory=company_choices, allow_blank=False)# when selecting a choice it return company's id. Add arg 'get_label=company_name' if we just want to return company's name instead
	name = StringField("Nom de l'opportunité", validators=[DataRequired()])
	euros_value = DecimalField("Montant (en €)", default=0, places=2)
	# Fields regarding the Stage Step
	stage = SelectField(u'Etape Commerciale', choices=distinct_stages_values(), validators=[DataRequired()])
	status = SelectField('Status', choices=distinct_status_values(), validators=[DataRequired()])
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)], default=None)
	task_title = StringField('Nom de la tâche', validators=[Optional()], default=None)
	task_content = TextAreaField('Descriptif', validators=[Optional(), Length(max=200)], default=None)
	task_priority = SelectField('Priorité', choices=distinct_priority_values(), validators=[Optional()], default=None)
	# task_due_date = DateField('A faire pour:', format='%Y-%m-%d')
	# submit = SubmitField('Valider')

	def __init__(self, *args, **kwargs):
		super(EditOpportunityForm, self).__init__(*args, **kwargs)
		# Update choices for the select fields
		self.stage.choices = distinct_stages_values()
		self.status.choices = distinct_status_values()
		self.task_priority.choices = distinct_priority_values()
	
	def prepopulate_values(self, session):
		"""	Pre-populate the form with the data of the latest step """
		self.stage.data = session.get('stage')
		self.status.data = session.get('status')
		self.note_content.data = session.get('note_content')
		self.task_title.data = session.get('task_title')
		self.task_content.data = session.get('task_content')
		self.task_priority.data = session.get('task_priority')
		# self.task_due_date.data = session.get('task_due_date')

	def validate_task_fields(self):
		if not ((self.task_title.data and self.task_content.data) and self.task_priority.data):
			return False
		else:
			return True
# class AddOpportunityForm(FlaskForm):
# 	company = QuerySelectField("Entreprise", query_factory=company_choices, allow_blank=False)# when selecting a choice it return company's id. Add arg 'get_label=company_name' if we just want to return company's name instead
# 	name = StringField("Nom de l'opportunité", validators=[DataRequired()])
# 	euros_value = DecimalField("Montant (en €)", default=0, places=2)
# 	stage = SelectField(u'Etape Commerciale', choices=distinct_stages_values(), validators=[DataRequired()])
# 	status = SelectField('Status', choices=distinct_status_values(), default='En attente', validators=[DataRequired()]) #list(distinct_status_values())[2][0]
# 	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)], default=None)
# 	task_title = StringField('Nom de la tâche', validators=[Optional()], default=None)
# 	task_content = TextAreaField('Descriptif', validators=[Optional(), Length(max=200)], default=None)
# 	task_priority = SelectField('Priorité', choices=distinct_priority_values(), validators=[Optional()])	
# 	# task_due_date = DateField('A faire pour:', format='%Y-%m-%d', validators=[Optional()], default=None)

# 	# Define choices within _init__ to prevent error when manually initiatin choices
# 	def __init__(self, *args, **kwargs):
# 		super(AddOpportunityForm, self).__init__(*args, **kwargs)
# 		self.stage.choices = distinct_stages_values()
# 		self.status.choices = distinct_status_values()
# 		self.task_priority.choices = distinct_priority_values()

# 	def validate_task_fields(self):
# 		if not ((self.task_title.data and self.task_content.data) and self.task_priority.data):
# 			return False
# 		else:
# 			return True



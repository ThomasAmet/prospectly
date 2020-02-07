from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, DecimalField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo, Optional
from ..models import Contact, distinct_status_values, distinct_stages_values, distinct_priority_values
from flask_login import current_user



def contact_choices():
	#result = Contact.query.filter(Contact.postal_code.like('94%'))
	return Contact.query.filter(Contact.user_id==current_user.id)

class EditOpportunityStageForm(FlaskForm):
	stage = SelectField(u'Etape Commerciale', choices=distinct_stages_values(), validators=[DataRequired()])
	status = SelectField('Status', choices=distinct_status_values(), validators=[DataRequired()])
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)], default=None)
	task_title = StringField('Nom de la tache', validators=[Optional()], default=None)
	task_content = TextAreaField('Descriptif', validators=[Optional(), Length(max=200)], default=None)
	task_priority = SelectField('Priorité', choices=distinct_priority_values(), validators=[Optional()], default=None)
	# task_due_date = DateField('A faire pour:', format='%Y-%m-%d')
	# submit = SubmitField('Valider')

	def initiate_choices(self):
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


class AddOpportunityForm(FlaskForm):
	contact = QuerySelectField(query_factory=contact_choices, allow_blank=False)#add arg 'get_label=company_name' if we just want to return company name
	name = StringField("Nom de l'opportunite", validators=[DataRequired()])
	euros_value = DecimalField("Montant en euros", default=0)
	stage = SelectField(u'Etape Commerciale', choices=distinct_stages_values(), validators=[DataRequired()])
	status = SelectField('Status', choices=distinct_status_values(), validators=[DataRequired()])
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)], default=None)
	task_title = StringField('Nom de la tache', validators=[Optional()], default=None)
	task_content = TextAreaField('Descriptif', validators=[Optional(), Length(max=200)], default=None)
	task_priority = SelectField('Priorité', choices=distinct_priority_values(), validators=[Optional()])
	task_due_date = DateField('A faire pour:', format='%Y-%m-%d', validators=[Optional()], default=None)

	def initiate_choices(self):
		# Update choices for the select fields
		self.stage.choices = distinct_stages_values()
		self.status.choices = distinct_status_values()
		self.task_priority.choices = distinct_priority_values()


class AddProspectForm(FlaskForm):
	company_name = StringField("Nom de l'opportunite", validators=[DataRequired()])
	company_activity_field = StringField("Domaine d'activité", validators=[DataRequired()])#choice from exisitng + free
	company_email = StringField("Email", validators=[Regexp('0[0-9]{9}', 0, 'Le format doit etre de la forme 0XXXXXXXXX')], default=None)
	company_phone = StringField("Nom de l'opportunite", validators=[Regexp('0[0-9]{9}', 0, 'Le format doit etre de la forme 0XXXXXXXXX')], default=None)
	company_address = StringField("Adresse", default=None)
	company_postal_code = StringField("Code Postal", default=None)
	company_city = StringField("Ville", default=None)
	company_email_bcc = StringField("2nd email", default=None)
	owner_firstname = StringField("Prenom du dirigeant", default=None)
	owner_lastname = StringField("Nom du dirigeant", default=None)
	website = StringField('Site web', default=None)
	facebook = StringField('Page Facebook', default=None)
	instagram = StringField('Page Instagram web', default=None)
	linkedin = StringField('Page LinkedIn', default=None)







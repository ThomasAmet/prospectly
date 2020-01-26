from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError,  Email, EqualTo, Optional
from app.models import distinct_status_values, distinct_stages_values, distinct_priority_values

class EditOpportunityStepForm(FlaskForm):
	stage = SelectField('Etape Commerciale', choices=distinct_stage_values(), validators=[DataRequired()])
	status = SelectField('Status', choices=distinct_status_values(), validators=[DataRequired()])
	note_content = TextAreaField('Note', validators=[Optional(), Length(max=200)])
	task_title = TextAreaField('Nom de la tache', validators=[DataRequired(), Length(max=200)], default='Aucune tache')
	task_content = TextAreaField('Descriptif', validators=[Optional(), Length(max=200)])
	task_priority = SelectField('Priorité', choices=distinct_priority_values(), default='basse')
	due_date = DateField('A faire pour:', format='%Y-%m-%d')
	
from flask import render_template, redirect, url_for, request, session, jsonify, flash, Response
from . import crm
from .forms import CompanyForm, AddContactForm, EditContactForm, AddOpportunityForm, EditOpportunityForm
from app import db
from ..models import User, Subscription, Company, Contact, ContactsEmail, Opportunity, OpportunityStep, CommercialStage, Status, Task, Note
from ..models import get_list_opportunities, get_list_companies, get_list_contacts
from app.auth.views import admin_login_required
from flask_login import current_user, login_required
from datetime import datetime

def clear_session():
	session.pop('note_content', None)
	session.pop('stage', None)
	session.pop('stage_closing_perc', None)
	session.pop('stage_closing_perc', None)
	session.pop('status', None)
	session.pop('task_content', None)
	session.pop('task_done', None) 
	session.pop('task_due_date', None)
	session.pop('task_due_date', None)
	session.pop('task_priority', None)
	session.pop('task_title', None)
	return True


@crm.route('/error')
@login_required
@admin_login_required
def test():
	contacts, next_page, previous_page = get_list_contacts(current_user.id, limit=25, cursor=None)
	return render_template('test.html', contacts=contacts)


@crm.route('/', methods=['GET','POST'])
@login_required
def index():
	# flash('Test')
	return render_template('app_base.html', title='Prospects')



@crm.route('/dashboard')
@login_required
def home():
	return render_template('dashboard.html', title='Dashboard')



@crm.route('/entreprises/liste')
@login_required
def view_companies_list():
	form = CompanyForm()
	token = request.args.get('page_token', None)
	if token:
		token = token.encode('utf-8')

	companies, next_page, previous_page = get_list_companies(user_id=current_user.id, limit=25, cursor=token)

	return render_template('companies-list.html', companies=companies, next_page=next_page, previous_page=previous_page, form=form)



@crm.route('/entreprises/ajout', methods=['POST'])
@login_required
def add_company():
	if not request.method=='POST':
		return redirect(url_for('crm.home'))

	# try:
	form = CompanyForm(request.form)
	data = request.form.to_dict(flat=True)
	print(data)
	data['user_id'] = current_user.id
	note_content = data['note_content']
	data.pop('note_content')
	data.pop('csrf_token')
	company = Company(**data) # This method only works if data only contains key that are attributes of Company. Otherwise use setattr(company, k, v) looped over company.items()
	db.session.add(company)
	db.session.flush()

	# if note_content!='':
	note = Note(company_id=company.id, content=note_content)
	db.session.add(note)
		
	db.session.commit()
		# flash('Entreprise ajoutée avec succès.')
	# except:
		# db.session.rollback()
		# flash("Une erreur s'est produite. Veuillez réessayer ou contactez le support.")
	return redirect(url_for('crm.view_companies_list'))



@crm.route('/entreprises/suppression', methods=['POST','GET'])
def delete_company():	
	if request.form.get('company_id'):
		companies_ids = [request.form.get('company_id')]
	else:
		companies_ids = request.get_json()['companies_ids']

	for company_id in companies_ids:
		company = Company.query.get(company_id)
		db.session.delete(company)
	try:
		db.session.commit()
		# flash('Entreprises supprimées avec succès.')
	except:
		flash("Une erreur s'est produite. Veuillez réessayer ou contactez le support.")
		db.session.rollback()

	return redirect(url_for('crm.view_companies_list'))



@crm.route('/entreprise/<id>/edition', methods=['GET','POST'])
def edit_company(id):			
	company = Company.query.get(id)
	data = request.form.to_dict(flat=True)

	# Return to list if the user attempt to edit an opportunity that doesnt belong to hin or if request is GET
	if not company.user_id == current_user.id or request.method=='GET':
		return redirect(url_for('crm.view_companies_list'))
	
	try:
		# Edit the company
		for k,v in data.items():
			print('{}:{}'.format(k,v))
			setattr(company, k, v)
		db.session.commit()	
	except:
		db.session.rollback
	return redirect(url_for('crm.view_companies_list'))




@crm.route('/contacts/liste', methods=['GET'])
def view_contacts_list():
	add_contact_form = AddContactForm()
	edit_contact_form = EditContactForm()
	token = request.args.get('page_token', None)
	if token:
		token = token.encode('utf-8')

	contacts, next_page, previous_page = get_list_contacts(current_user.id, limit=25, cursor=None)
	print([contact.firm for contact in contacts])
	return render_template('contacts-list.html', contacts=contacts, next_page=next_page,
							previous_page=previous_page, add_form=add_contact_form, edit_form=edit_contact_form)




@crm.route('/contacts/ajout', methods=['POST'])
def add_contact():

	if request.method == 'POST':
		# Get input from the form
		data = request.form.to_dict(flat=True) 	
		print(data)

		# Prepare input data to create Emails and Notes 
		email = data['email']
		is_main = True if data['is_email_main']=='True' else False
		note_content = data['note_content']	

		if data['company_id'] == '__None':
			data.pop('company_id')	
		data['user_id'] = current_user.id
		data.pop('csrf_token')
		data.pop('email')
		data.pop('is_email_main')
		data.pop('note_content')

		# Add contact to db and flush to get an id
		contact = Contact(**data)
		db.session.add(contact)
		db.session.flush()
		
		# if not note_content == '':
		note = Note(content=note_content, contact_id=contact.id)
		db.session.add(note)
		# if not email == '':
		contactsemail = ContactsEmail(contact_id=contact.id, email=email, is_main=is_main)
		db.session.add(contactsemail)

		try:
			db.session.commit()
			# flash('Contact ajouté avec succès.')
		except:
			db.session.rollback()
			flash("Une erreur s'est produite. Veuillez réessayer ou contactez le support.")

	return redirect(url_for('crm.view_contacts_list'))



@crm.route('/contacts/suppression', methods=['POST'])
def delete_contact():

	if request.form.get('contact_id'):
		contacts_ids = [request.form.get('contact_id')]
	else:
		contacts_ids = request.get_json()['contacts_ids']


	for contact_id in contacts_ids:
		contact = Contact.query.get(contact_id)
		db.session.delete(contact)

	try:
		db.session.commit()
		# flash('Contact supprimé avec succès.')
	except:
		db.session.rollback()

	return redirect(url_for('crm.view_contacts_list'))



@crm.route('/contact/<id>/edition', methods=['POST'])
def edit_contact(id):
	contact = Contact.query.get(id)
	# Return to list of contact for GET request or when trying to edit someone else contact
	if request.method=='GET' or not contact.user_id==current_user.id:
		return redirect(url_for('crm.view_contacts_list'))
	
	data = request.form.to_dict(flat=True)

	# Remove company id if none
	if data['company_id'] == '__None':
			data.pop('company_id')
	print(data)
	for k,v in data.items():
		setattr(contact, k, v)

	if data.get('note_content'):
		contact.notes.first().content = data.get('note_content')
	if data.get('email'):
		contact.emails.first().email = data.get('email')

	try:
		db.session.commit()
	except:
		db.session.rollback()

	return redirect(url_for('crm.view_contacts_list'))



@crm.route('/opportunites/liste')
@login_required
def view_opportunities_list():	
	add_opportunity_form = AddOpportunityForm()
	edit_opportunity_form = EditOpportunityForm()
	edit_opportunity_form.company.render_kw = {'disabled': 'disabled'}
	
	token = request.args.get('page_token', None)
	if token:
		token = token.encode('utf-8')
	
	opportunities, next_page, previous_page = get_list_opportunities(user_id=current_user.id, limit=20, cursor=token)
	latest_steps = [OpportunityStep.query.filter_by(opportunity_id=opportunity.id).order_by(OpportunityStep.creation_date.desc()).first() for opportunity in opportunities]
	# ids = [opp.id for opp in opportunities]
	# opportunities = dict(zip(ids,list(zip(opportunities, latest_steps)))) #dict of list: key is an integer, value is a list. Each list is compose of an opportunity and its latest stage. 
	opportunities = dict(zip(range(len(opportunities)),list(zip(opportunities, latest_steps)))) #dict of list: key is an integer, value is a list. Each list is compose of an opportunity and its latest stage. 
	# print(opportunities[0][1].tasks.first())
	return render_template('opportunities-list.html', opportunities=opportunities,
						    add_form=add_opportunity_form, edit_form= edit_opportunity_form,			
							next_page_token=next_page, previous_page_token=previous_page)


@crm.route('/opportunites/ajout', methods=['GET','POST'])
@login_required
def add_opportunity(): 
	if request.method=='GET':
		return redirect(url_for('crm.view_opportunities_list'))

	form = AddOpportunityForm(request.form)
	
	if not form.validate():
		print(form.errors)
		flash('Une erreur est survenue. Veuillez réessayer.')
		return redirect(url_for('crm.view_opportunities_list'))
	
	try:
		opportunity = Opportunity(user_id=current_user.id,
							 	  company_id=form.company.data.id,
							  	  name=form.name.data,
							  	  euros_value=form.euros_value.data)
		db.session.add(opportunity)
		db.session.flush()	
		print(request.form)
		stage = CommercialStage.query.filter_by(name=request.form.get('stage')).first_or_404()
		status = Status.query.filter_by(name=request.form.get('status')).first_or_404()
		opportunity_step = OpportunityStep(opportunity_id=opportunity.id,
										  stage_id=stage.id,
										  status_id=status.id)
		db.session.add(opportunity_step)
		db.session.flush()

		if form.status.data=='A faire':
			task_done = True if request.form.get('task_done') else False
			due_date = request.form.get('task_due_date')
			print('due_date before process: {}'.format(due_date))
			due_date = datetime(year=int(due_date[-4:]), month=int(due_date[:2].replace('0','')), day=int(due_date[3:-5].replace('0',''))) if due_date else None # Parse due from mm/dd/yyyy to dd/mm/yyyy if exists
			print('due_date after process: {}'.format(due_date))

			task = Task(user_id=current_user.id,
						opportunity_step_id=opportunity_step.id,
						title=request.form.get('task_title'),
						content=request.form.get('task_content'), 
						priority=request.form.get('task_priority'), 
						due_date=due_date,
						done=task_done)
			db.session.add(task)
			
		else:
			note = Note(content=request.form.get('note_content'),
						opportunity_step_id	=opportunity_step.id)
			db.session.add(note)
			

		db.session.commit()
	except:
		db.session.rollback()

	return redirect(url_for('crm.view_opportunities_list'))	
	


@crm.route('/oppportunites/suppression', methods=['POST','GET'])
@login_required
def delete_opportunity():
	# try:
	if request.form.get('opportunity_id'):
		opp_ids = [request.form.get('opportunity_id')] #row by row deletion
	else:
		opp_ids = request.get_json()['opp_ids'] #multiple rows deletion
	# print(opp_ids)

	try:
		for id in opp_ids:
			id = int(id)
			opportunity = Opportunity.query.get(id)
			
			db.session.delete(opportunity)
		db.session.commit()
	except:
		db.session.rollback()
	return redirect(url_for('crm.view_opportunities_list'))



@crm.route('/opportunites/<id>/edition', methods=['POST'])
def edit_opportunity(id):
	data = request.form.to_dict(flat=True)

	print(data)	
	
	# Query some object from the form's input
	opportunity = Opportunity.query.get(id)
	company = Company.query.get(data.get('company_id'))
	initial_step = OpportunityStep.query.get(int(data.get('initial_step_id')))
	new_stage_id = CommercialStage.query.filter_by(name=data.get('stage')).first().id
	new_status_id = Status.query.filter_by(name=data.get('status')).first().id

	# Parse some input
	due_date = request.form.get('task_due_date')
	due_date = datetime(year=int(due_date[-4:]), month=int(due_date[:2].replace('0','')), day=int(due_date[3:-5].replace('0',''))) if due_date else None # Parse the task's due-date from mm/dd/yyyy to dd/mm/yyyy if exists
	task_done = True if request.form.get('task_done') else False

	# Condition to verify that the user that request the page is the owner of the requested opportunity
	if not opportunity.user_id == current_user.id:
		return redirect(url_for('crm.view_opportunities_list'))

	# No change in step status nor commercial stage so we only edit Note or Task
	if data.get('initial_stage') == data.get('stage') and data.get('initial_status') == data.get('status'):
		latest_note = Note.query.filter_by(opportunity_step_id=int(data.get('initial_step_id'))).first()
		latest_task = Task.query.filter_by(opportunity_step_id=int(data.get('initial_step_id'))).first()
		# If true, update the task associated to the step
		if data.get('status') == 'A faire':

			latest_task.title = data.get('task_title')
			latest_task.priority = data.get('task_priority')
			latest_task.content = data.get('task_content')
			latest_task.due_date = due_date
			latest_task.done = task_done
		# Else update the note associated to the step 
		else:
			latest_note.content = data.get('note_content')
	# Else check if an opportunity'step with the required stage and status already exists		
	else:
		new_latest_step = OpportunityStep.query.filter_by(opportunity_id=data.get('opportunity_id'),
										  stage_id=new_stage_id,
										  status_id=new_status_id).first()
		# If not, create a new step
		if not new_latest_step:
			new_latest_step = OpportunityStep(opportunity_id=data.get('opportunity_id'),
											  stage_id=new_stage_id,
											  status_id=new_status_id)
			db.session.add(new_latest_step)
			db.session.flush() # get new_opp id
		
		# Then create a task or note
		if data.get('status') == 'A faire':
			new_task = Task(opportunity_step_id=new_latest_step.id,
							title=data.get('task_title'),
							content=data.get('task_content'),
							priority=data.get('task_priority'),
							due_date=due_date,
							done=task_done)
		else:
			new_note = Note(opportunity_step_id=new_latest_step.id,
							content=data.get('note_content'))

	# Edit the company associated to that opportunity if the customer clicked on the pencil in the form
	company.email = data.get('company-email') if data.get('company-email') else company.email
	company.phone = data.get('company-phone') if data.get('company-phone')else company.phone
	company.activity_field = data.get('company-activity') if data.get('company-activity') else company.activity_field

	try:
		db.session.commit()
	except:
		db.session.rollback()

	return redirect(url_for('crm.view_opportunities_list'))





@crm.route('/opportunites/<id>/etape/edition', methods=['POST','GET'])
@login_required
def edit_opportunity_step(id):

	if not request.method=='POST':
		return redirect(url_for('crm.view_opportunity_step', id=id))

	opportunity = Opportunity.query.get(id)
	form = EditOpportunityStageForm(request.form)

	if not opportunity.user_id == current_user.id:
		return redirect(url_for('crm.home'))

	# Condition that prevent to submit the form if the session has been cleared before  
	if not 'status' in session:	
		return redirect(url_for('crm.view_opportunity_step', id=opportunity.id))

	latest_step = OpportunityStep.query.filter_by(opportunity_id=opportunity.id).order_by(OpportunityStep.creation_date.desc()).first()
	due_date = request.form.get('due-date-value')
	due_date = datetime(year=int(due_date[-4:]), month=int(due_date[:2].replace('0','')), day=int(due_date[3:-5].replace('0',''))) if due_date else None # Parse due from mm/dd/yyyy to dd/mm/yyyy if exists
	task = None
	flash(due_date)

	# If the latest_stage contains a note, update it (if data)
	if session['note_content']:
		note = latest_stage.notes.fist()
		note.content = form.note_content.data if form.note_content.data else ''
	# Otherwise create a new one (if data)
	else:
		note = Note(note_content=form.note_content.data) if form.note_content.data else None

	# Check that the user wants to create a task ans that all field are filled
	if form.status.data == 'A faire':
		if form.validate_task_fields() and due_date:
			# Create a new Task if there is no task associated with the previous stage
			if not latest_stage.task:			
				task = Task(user_id=current_user.id,
							task_title=form.task_title.data,
							task_content=form.task_content.data, 
							priority=form.task_priority.data, 
							due_date=due_date,
							done=request.form.get('task-done-value'))
			# Update the existing one otherwise
			else:
				task = latest_stage.task
				task.task_title = form.task_title.data
				task.task_content = form.task_content.data
				task.priority = form.task_priority.data
				task.task_due_date = due_date
				task.task_done = request.form.get('task-done-value')
			db.session.add(task)
			db.session.flush()
		# If not, display an error and return the edit form
		else:
			flash('Tous les champs concernant la tache doivent etre remplis') 
			return redirect(url_for('crm.view_opportunity_stage', id=opportunity.id))

	# Create a new stage since either commercial_stage or stage_status changed
	if form.stage.data != session.get('stage') or form.status.data != session.get('status'):
		stage_id = CommercialStage.query.filter_by(name=form.stage.data).first().id
		status_id = Status.query.filter_by(title=form.status.data).first().id
		# Create a new OpportunityStage
		latest_stage = CommercialStageStep(opportunity_id=opportunity.id, commercial_stage_id=stage_id, status_id=status_id)

	if note:
		flash('adding the note to stage')
		db.session.add(note)
		db.session.flush()
		latest_stage.note_id = note.id
	if task:
		flash('adding the task to stage')
		latest_stage.task_id = task.id
	
	db.session.add(latest_stage)

	db.session.commit()
	clear_session()
	return redirect(url_for('crm.view_opportunities_list'))




@crm.route('/opportunites/<id>/etape')
@login_required
def view_opportunity_step(id):

	if request.method=='POST':
		return redirect(url_for('crm.view_opportunities_list'))

	opportunity = Opportunity.query.get(id)

	# Condition to verify that the user that request the page is the owner of the requested opportunity
	if not opportunity.user_id == current_user.id:
		return redirect(url_for('crm.view_opportunities_list'))

	form = EditOpportunityStageForm()
	# form.initiate_choices()		
	latest_step = OpportunityStep.query.filter_by(opportunity_id=opportunity.id).order_by(OpportunityStep.creation_date.desc()).first()
	
	# Store data in session to compare the previous state with new state once the form is submitted
	session['stage'] = latest_step.commercial_stage.name
	session['status'] = latest_step.status.name
	session['stage_closing_perc'] = str(latest_step.commercial_stage.closing_perc*100)+' %'

	if session['status'] == 'A faire':
		session['note_content'] = ''
		session['task_title'] = Task.query.get(latest_step.task_id).title if latest_step.task_id else ''
		session['task_content'] = Task.query.get(latest_step.task_id).content if latest_step.task_id else ''
		session['task_priority'] = Task.query.get(latest_step.task_id).priority if latest_step.task_id else ''
		session['task_due_date'] = Task.query.get(latest_step.task_id).due_date if latest_step.task_id else ''
		session['task_done'] = Task.query.get(latest_step.task_id).done if latest_step.task_id else ''
	else:
		# session['note_content'] = Note.query.get(latest_step.note_id).note_content if latest_step.note else ''
		session['note_content'] = Note.query.filter_by(opportunity_step_id=latest_step.id).first().content 
		session['task_title'] = ''
		session['task_content'] = ''
		session['task_priority'] = ''
		session['task_due_date'] = ''
	
	form.prepopulate_values(session=session)
	return render_template('opportunity-step-view.html', form=form, opportunity=opportunity)




	




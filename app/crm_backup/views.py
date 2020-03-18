from flask import render_template, redirect, url_for, request, session, jsonify, flash, Response
from . import crm
from .forms import EditOpportunityStageForm, AddOpportunityForm, AddProspectForm
from app import db
from ..models import User, Subscription, Lead, LeadRequest, Contact, Opportunity, CommercialStageStep, CommercialStage, Task, Status, Note
from ..models import get_list_opportunities, get_list_prospects
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



@crm.route('/', methods=['GET','POST'])
@login_required
def index():
	flash('Test')
	return render_template('base2.html')



@crm.route('/dashboard')
@login_required
def home():
	return render_template('dashboard.html')



@crm.route('/prospects/liste')
@login_required
def view_prospect_list():
	form = AddProspectForm()
	token = request.args.get('page_token', None)
	if token:
		token = token.encode('utf-8')
	prospects, next_page, previous_page = get_list_prospects(user_id=current_user.id, limit=20, cursor=token)
	return render_template('prospects-list-view.html', prospects=prospects, form=form)


@crm.route('/prospects/ajout', methods=['POST'])
@login_required
def add_prospect():
	if not request.method=='POST':
		return redirect(url_for('crm.home'))

	form = AddProspectForm(request.form)
	data = request.form.to_dict(flat=True)
	data['user_id'] = current_user.id
	data.pop('csrf_token')
	prospect = Contact(**data)
	db.session.add(prospect)

	db.session.commit()
	return redirect(url_for('crm.view_prospect_list'))
	# except:
	# 	db.session.rollback()
	# 	# return redirect(url_for('main.home'))
	# 	return render_template('test.html')



@crm.route('/opportunites/liste')
@login_required
def view_opportunities_list():	
	form = AddOpportunityForm()
	edit_form = EditOpportunityStageForm()
	
	token = request.args.get('page_token', None)
	
	if token:
		token = token.encode('utf-8')
	
	opportunities, next_page, previous_page = get_list_opportunities(user_id=current_user.id, limit=20, cursor=token)
	latest_steps = [CommercialStageStep.query.filter_by(opportunity_id=opportunity.id).order_by(CommercialStageStep.creation_date.desc()).first() for opportunity in opportunities]
	# ids = [opp.id for opp in opportunities]
	# opportunities = dict(zip(ids,list(zip(opportunities, latest_steps)))) #dict of list: key is an integer, value is a list. Each list is compose of an opportunity and its latest stage. 
	opportunities = dict(zip(range(len(opportunities)),list(zip(opportunities, latest_steps)))) #dict of list: key is an integer, value is a list. Each list is compose of an opportunity and its latest stage. 
	
	return render_template('opportunities-list-view.html', form=form, opportunities=opportunities, next_page_token=next_page, previous_page_token=previous_page)



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
							 	  contact_id=form.contact.data.id,
							  	  name=form.name.data,
							  	  euros_value=form.euros_value.data)
		db.session.add(opportunity)
		db.session.flush()

		stage = CommercialStage.query.filter_by(name=request.form.get('stage')).first_or_404()
		status = Status.query.filter_by(title=request.form.get('status')).first_or_404()
		opportunity_stage=CommercialStageStep(opportunity_id=opportunity.id,
											  commercial_stage_id=stage.id,
											  status_id=status.id)
		db.session.add(opportunity_stage)

		if form.status.data=='A faire':
			due_date = request.form.get('due-date-value')
			due_date = datetime(year=int(due_date[-4:]), month=int(due_date[:2].replace('0','')), day=int(due_date[3:-5].replace('0',''))) if due_date else None # Parse due from mm/dd/yyyy to dd/mm/yyyy if exists

			task = Task(user_id=current_user.id,
						task_title=request.form.get('task_title'),
						task_content=request.form.get('task_content'), 
						priority=request.form.get('task_priority'), 
						due_date=due_date,
						done=request.form.get('task-done-value'))
			db.session.add(task)
			db.session.flush()
			opportunity_stage.task_id = task.id
		else:
			note = Note(note_content=request.form.get('note_content'))
			db.session.add(note)
			db.session.flush()
			opportunity_stage.note_id = note.id
	
		db.session.commit()
	except:
		db.session.rollback()
	return redirect(url_for('crm.view_opportunities_list'))	
	


@crm.route('/oppportunites/suppression', methods=['POST','GET'])
@login_required
def delete_opportunity():
	# try:
	if request.form.get('opp_id'):
		opp_ids = [request.form.get('opp_id')] #row by row deletion
	else:
		opp_ids = request.get_json()['opp_ids'] #multiple rows deletion
	# print(opp_ids)

	try:
		for id in opp_ids:
			id = int(id)
			opportunity = Opportunity.query.get(id)
			
			note_ids = [stage.note_id for stage in opportunity.commercial_stages if stage.note_id]
			if len(note_ids) > 0:
				for note_id in note_ids:
					note = Note.query.get(note_id)
					db.session.delete(note)

			task_ids = [stage.task_id for stage in opportunity.commercial_stages if stage.task_id]		
			if len(task_ids) > 0:
				for task_id in task_ids:
					task = Task.query.get(note_id)
					db.session.delete(task)
			db.session.delete(opportunity)
		db.session.commit()
	except:
		db.session.rollback()
	return redirect(url_for('crm.view_opportunities_list'))


	

@crm.route('/opportunites/<id>/etape')
@login_required
def view_opportunity_stage(id):

	if request.method=='POST':
		return redirect(url_for('crm.view_opportunities_list'))

	opportunity = Opportunity.query.get(id)

	# Condition to verify that the user that request the page is the owner of the requested opportunity
	if not opportunity.user_id == current_user.id:
		return redirect(url_for('crm.view_opportunities_list'))

	form = EditOpportunityStageForm()
	form.initiate_choices()		
	latest_stage = CommercialStageStep.query.filter_by(opportunity_id=opportunity.id).order_by(CommercialStageStep.creation_date.desc()).first()
	
	# Store data in session to compare to compare previous state with new state once the form is submitted
	session['stage'] = latest_stage.commercial_stage.name
	session['status'] = latest_stage.status.title
	session['stage_closing_perc'] = str(latest_stage.commercial_stage.closing_perc*100)+' %'

	if session['status'] == 'A faire':
		session['note_content'] = ''
		session['task_title'] = Task.query.get(latest_stage.task_id).task_title if latest_stage.task_id else ''
		session['task_content'] = Task.query.get(latest_stage.task_id).task_content if latest_stage.task_id else ''
		session['task_priority'] = Task.query.get(latest_stage.task_id).priority if latest_stage.task_id else ''
		session['task_due_date'] = Task.query.get(latest_stage.task_id).due_date if latest_stage.task_id else ''
		session['task_done'] = Task.query.get(latest_stage.task_id).done if latest_stage.task_id else ''
	else:
		session['note_content'] = Note.query.get(latest_stage.note_id).note_content if latest_stage.note else ''
		session['task_title'] = ''
		session['task_content'] = ''
		session['task_priority'] = ''
		session['task_due_date'] = ''
	
	form.prepopulate_values(session=session)
	return render_template('opportunity-stage-edit.html', form=form, opportunity=opportunity)



@crm.route('/opportunites/<id>/etape/edition', methods=['POST','GET'])
@login_required
def edit_opportunity_stage(id):

	if not request.method=='POST':
		return redirect(url_for('crm.home'))

	opportunity = Opportunity.query.get(id)
	form = EditOpportunityStageForm(request.form)

	if not opportunity.user_id == current_user.id:
		return redirect(url_for('crm.home'))

	# Condition that prevent to submit the form if the session has been cleared before  
	if not 'status' in session:	
		return redirect(url_for('crm.view_opportunity_stage', id=opportunity.id))

	latest_stage = CommercialStageStep.query.filter_by(opportunity_id=opportunity.id).order_by(CommercialStageStep.creation_date.desc()).first()
	due_date = request.form.get('due-date-value')
	due_date = datetime(year=int(due_date[-4:]), month=int(due_date[:2].replace('0','')), day=int(due_date[3:-5].replace('0',''))) if due_date else None # Parse due from mm/dd/yyyy to dd/mm/yyyy if exists
	task = None
	flash(due_date)

	# If the latest_stage contains a note, update it (if data)
	if session['note_content']:
		note = latest_stage.note
		note.note_content = form.note_content.data if form.note_content.data else ''
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

	


@crm.route('/error')
@login_required
@admin_login_required
def test():
	flash('{}'.format(session.keys()))	
	return render_template('test.html')


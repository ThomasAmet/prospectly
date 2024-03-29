from . import db, login_manager
from flask_login import UserMixin, current_user
from datetime import datetime
from operator import itemgetter
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import pandas as pd
import numpy as np
import random
# from db import Column, String, Integer, Boolean, DateTime, ForeignKey, relationship, backref


class Subscription(db.Model):
	__tablename__ = 'subscriptions'
	id = db.Column(db.Integer, primary_key=True)
	plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))# one side
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))# one side
	stripe_id = db.Column(db.String(60), nullable=True)
	subscription_date = db.Column(db.DateTime, default=datetime.utcnow)
	next_payment = db.Column(db.DateTime)
	cancellation_date = db.Column(db.DateTime, nullable=True)

	def is_valid(self):
		if Plan.query.get(self.plan_id).name == 'Beta':
			return True
		else:
			return self.next_payment > datetime.utcnow()

	def set_next_payment(self):
		'''
		Calling next payment shoud also set the cancelation date to None to remove the cancellation whenever a new payment is accepted
		'''
		self.cancelation_date = None
		plan = Plan.query.get(self.plan_id)

		if plan.name == 'Beta':
			self.next_payment = datetime.utcnow() + relativedelta(years=+4) # relativedelta accepts months and years

		# Case when to initiate the free trial period
		if self.next_payment is None and plan.name=='Basic':
			# try:
			self.next_payment = datetime.utcnow() + relativedelta(days=+plan.free_trial)# timedelta only accepts days
			# except ValueError:
			# 	self.next_payment = datetime.utcnow() + timedelta(days=+15)
		# Cases for subscriptions renewal or new Pro subscritpion
		else:
			if plan.yearly:
				self.next_payment = datetime.utcnow()  + relativedelta(years=1) # utcnow + 1 month or 1 year instead of next_payment + 1month or 1 year to handle when the user moves from yeary to monthly
			else:
				self.next_payment = datetime.utcnow()  + relativedelta(months=1) 
		print('Subscription {} next payment is set to: {}'.format(self.id, self.next_payment))		
		return 0


	def __init__(self, **kwargs):
		super(Subscription, self).__init__(**kwargs)
		# Create a next payment date when a new subscription is created 
		# self.set_next_payment()

	def __repr__(self):
		return "[On {}, user {} subscribed to a {} plan]".format(self.subscription_date, self.user_id, self.plan.name )
	# define next_paymnet date when initiate



class Plan(db.Model):
	__tablename__ = 'plans'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), index=True)
	category = db.Column(db.String(30))
	monthly_price = db.Column(db.Integer)
	free_trial = db.Column(db.Integer)#number of days for the free trial
	limit_daily_query = db.Column(db.Integer)
	lead_generator = db.Column(db.Boolean, default=False)
	yearly = db.Column(db.Boolean, default=False)
	stripe_id = db.Column(db.String(120))
	subscriptions = db.relationship('Subscription', foreign_keys=[Subscription.plan_id], backref=db.backref('plan', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side

	def __repr__(self):
		return "<{}>".format(self.name)



class LeadRequest(db.Model):
	__tablename__ = 'lead_requests'
	id = db.Column(db.Integer, primary_key=True)
	contact_lead_id = db.Column(db.Integer, db.ForeignKey('contact_leads.id'), default=None)# one side of a one-to-many with contact leads
	company_lead_id = db.Column(db.Integer, db.ForeignKey('company_leads.id'), default=None)# one side of a one-to-many with comapny leads
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))# one side
	company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), default=None)
	contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), default=None)
	query_date = db.Column(db.DateTime, default=datetime.utcnow)

	def exists(self):
		request = LeadRequest.query.filter(LeadRequest.lead_id==self.lead_id, LeadRequest.user_id==self.user_id).first()
		if not request:
			return False
		return True

	def __repr__(self):
		return "On {}, user {} queried lead {} ".format(self.query_date, self.user_id, self.company_lead_id if self.company_lead_id else self.contact_lead_id)



class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(30))
	last_name = db.Column(db.String(30))
	username = db.Column(db.String(60), index=True)
	email = db.Column(db.String(120), index=True, unique=True)
	contact_email = db.Column(db.String(120))
	phone = db.Column(db.String(60), nullable=True)
	address = db.Column(db.String(120), nullable=True)
	postal_code = db.Column(db.String(120), nullable=True)
	city = db.Column(db.String(120), nullable=True)
	stripe_customer_id = db.Column(db.String(256), nullable=True)
	last_token = db.Column(db.String(256), nullable=True)
	password_hash = db.Column(db.String(120))
	registration_date = db.Column(db.DateTime, default=datetime.utcnow)
	# avatar = db.Column(db.String(120))
	admin = db.Column(db.Boolean, default=False)
	subscriptions = db.relationship('Subscription', foreign_keys=[Subscription.user_id], backref=db.backref('user', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side
	requested_leads = db.relationship('LeadRequest', foreign_keys=[LeadRequest.user_id], backref=db.backref('user', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side
	companies = db.relationship('Company', backref='user', lazy='dynamic')# one-to-many (many side)
	contacts = db.relationship('Contact', backref='user', lazy='dynamic')
	opportunities = db.relationship('Opportunity', backref=db.backref('user', lazy='joined'), lazy='dynamic')# one-to-many (many-side)
	# Maybe delete the relationship below
	commercial_stages = db.relationship('CommercialStage', backref=db.backref('user', lazy='joined'), lazy='dynamic')# one-to-many (many-side)
	tasks =  db.relationship('Task', backref='user', lazy='dynamic')# many-to-one with Task (many-side)

	@validates(first_name, last_name)
	def capitalize(self, key, value):
		return value.capitalize()

	def set_username(self):
		self.username = str(self.first_name).capitalize() + '_' + str(self.last_name).capitalize()

	# def set_avatar(self):
	# 	digest = md5(self.email.lower().encode('utf-8')).hexdigest()
	# 	self.avatar = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, 400)

	def set_password(self, password_entry):
		self.password_hash = generate_password_hash(password_entry)

	def verify_password(self, password_entry):
		return check_password_hash(self.password_hash, password_entry)

	def is_admin(self):
		return self.admin

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.set_username()
		self.contact_email = self.email
		# self.set_avatar()

	def __repr__(self):
		return "<{}>".format(self.username)


class ContactLead(db.Model):
	__tablename__ = 'contact_leads'
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(60), index=False, unique=False, nullable=False)
	lastname = db.Column(db.String(60), index=False, unique=False, nullable=False)
	company_id = db.Column(db.Integer, db.ForeignKey('company_leads.id'), nullable=True)
	position = db.Column(db.String(60), index=False, unique=False, nullable=True)
	email = db.Column(db.String(120), index=False, unique=False, nullable=True)
	phone = db.Column(db.String(120), index=False, unique=False, nullable=True)
	linkedin = db.Column(db.String(240), index=False, unique=False, nullable=True)
	instagram = db.Column(db.String(240), index=False, unique=False, nullable=True)
	facebook = db.Column(db.String(240), index=False, unique=False, nullable=True)
	requests = db.relationship('LeadRequest', foreign_keys=[LeadRequest.contact_lead_id], backref='contact_lead', lazy='dynamic')# many side
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '{} {}'.format(self.firstname, self.lastname)


class CompanyLead(db.Model):
	__tablename__ = 'company_leads'
	id = db.Column(db.Integer, primary_key=True)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	name = db.Column(db.String(120), nullable=False)
	address = db.Column(db.String(120), index=False, unique=False, nullable=True)
	postal_code = db.Column(db.String(30), index=False, unique=False, nullable=True)
	city = db.Column(db.String(60), index=True, unique=False, nullable=True)
	country = db.Column(db.String(60), index=True, nullable=True)
	email = db.Column(db.String(60), index=False, unique=False, nullable=True)
	phone = db.Column(db.String(60), index=False, unique=False, nullable=True)
	website = db.Column(db.String(240), index=False, unique=False, nullable=True)
	facebook = db.Column(db.String(240), index=False, unique=False, nullable=True)
	instagram = db.Column(db.String(240), index=False, unique=False, nullable=True)
	linkedin = db.Column(db.String(240), index=False, unique=False, nullable=True)
	activity_field1 = db.Column(db.String(60), index=True, unique=False, nullable=False)
	activity_field2 = db.Column(db.String(60), index=True, unique=False, default=None)
	activity_field3 = db.Column(db.String(60), index=True, unique=False, default=None)
	contacts = db.relationship('ContactLead', backref='firm', lazy='dynamic')
	requests = db.relationship('LeadRequest', foreign_keys=[LeadRequest.company_lead_id], backref='company_lead', lazy='dynamic', cascade='all, delete-orphan')# many side
	
	# def exists(self):
	# 	lead = Lead.query.filter(Lead.company_name==self.company_name, Lead.company_postal_code==self.company_postal_code).first()
	# 	if not lead:
	# 		return False
	# 	return True

	def __repr__(self):
		return "{} situe a {}".format(self.name, self.city if self.city else '<information manquante>')



class OpportunityStep(db.Model):
	__tablename__ = 'opportunity_steps'
	id = db.Column(db.Integer, primary_key=True)
	opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'))
	stage_id = db.Column(db.Integer, db.ForeignKey('commercial_stages.id'))
	status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
	# notes = db.relationship('Note', backref='opportunity_step', lazy='dynamic', cascade='all, delete-orphan')
	tasks = db.relationship('Task', backref='opportunity_step', lazy='dynamic', cascade='all, delete-orphan')
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	last_update = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return "<Opp. {} on stage {} with status {} created on {}>".format(self.opportunity.name, self.commercial_stage.name, self.status.name, self.creation_date)



class Contact(db.Model):
	__tablename__ = 'contacts'
	id = db.Column(db.Integer, primary_key=True)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	first_name = db.Column(db.String(120), index=True, unique=False, nullable=True)
	last_name = db.Column(db.String(120), index=True, unique=False, nullable=True)
	company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), default=None) 
	position = db.Column(db.String(120), index=True, unique=False, nullable=True)
	linkedin = db.Column(db.String(240), index=False, unique=False, nullable=True)
	instagram = db.Column(db.String(240), index=False, unique=False, nullable=True)
	facebook = db.Column(db.String(240), index=False, unique=False, nullable=True)
	phone = db.Column(db.String(120), index=False, unique=False, nullable=True)
	emails = db.relationship('ContactsEmail', backref='contact', lazy='dynamic') # many-side of a one-to-many relationship with ContactsEmail
	notes = db.relationship('Note', backref='contact', lazy='dynamic', cascade='all, delete-orphan')# many-side of a one-to-many relationship with Notes
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # one-side of a many-to-one with User 
	request = db.relationship('LeadRequest', foreign_keys=[LeadRequest.contact_id], backref='contact', lazy='dynamic')# many side
	# opportunities = db.relationship('Opportunity', backref='contact', lazy='dynamic') # one-to-many (many side)

	def __repr__(self):
		return  "{} {}".format(self.first_name, self.last_name)



class Company(db.Model):
	__tablename__ = 'companies'
	id = db.Column(db.Integer, primary_key=True)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	name = db.Column(db.String(120), index=False, unique=False, nullable=True)
	address = db.Column(db.String(120), index=False, unique=False, nullable=True)
	postal_code = db.Column(db.String(30), index=False, unique=False, nullable=True)
	city = db.Column(db.String(60), index=False, unique=False, nullable=True)
	country = db.Column(db.String(60), index=False, unique=False, nullable=True)
	email = db.Column(db.String(120), index=False, unique=False, nullable=True)
	phone = db.Column(db.String(60), index=False, unique=False, nullable=True)
	activity_field = db.Column(db.String(60), index=True, unique=False, nullable=False)
	website = db.Column(db.String(120), index=False, unique=False, nullable=True)
	facebook = db.Column(db.String(240), index=False, unique=False, nullable=True)
	instagram = db.Column(db.String(240), index=False, unique=False, nullable=True)
	linkedin = db.Column(db.String(240), index=False, unique=False, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # one-side of a many-to-one with User 
	contacts = db.relationship('Contact', foreign_keys=[Contact.company_id], backref=db.backref('firm', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
	opportunities = db.relationship('Opportunity', backref='company', lazy='dynamic', cascade='all, delete-orphan') # one-to-many with Opportunity table (many side)
	notes = db.relationship('Note', backref='company', lazy='dynamic')
	request = db.relationship('LeadRequest', foreign_keys=[LeadRequest.company_id], backref='company', lazy='dynamic')# many side
	
	def __repr__(self):
		return  "{} situé à {}".format(self.name, self.city if self.city else '<information manquante>')



class ContactsEmail(db.Model):
	__tablename__= 'contacts_emails'
	id = db.Column(db.Integer, primary_key=True)
	contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
	email = db.Column(db.String(120), index=False, unique=False, nullable=True)
	is_main = db.Column(db.Boolean, default=True)
	
	#  Create a function that change all emails to secondary if a new email is set as main
	def __repr__(self):
		# return "{} email's is {}".format(self.contact.first_name+' '+self.contact.last_name, self.email)
		return "email principal: {}".format(self.email) if self.is_main else "Mail secondaire: {}".format(self.email)



class Opportunity(db.Model):
	__tablename__ = 'opportunities'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
	name = db.Column(db.String(120), nullable=False)
	euros_value = db.Column(db.Numeric(8,2))
	notes = db.relationship('Note', backref='opportunity_step', lazy='dynamic', cascade='all, delete-orphan')
	opportunity_steps = db.relationship('OpportunityStep', foreign_keys=[OpportunityStep.opportunity_id], backref=db.backref('opportunity', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	deal_closed = db.Column(db.Boolean, default=False)
	last_update = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return "<Opportunity's name: {}>".format(self.name)



class CommercialStage(db.Model):
	__tablename__ = 'commercial_stages'
	id = db.Column(db.Integer, primary_key=True)
	stage_steps = db.relationship('OpportunityStep', foreign_keys=[OpportunityStep.stage_id], backref=db.backref('commercial_stage', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many-to-many with Opportunity (many side of a many-to-one with CommercialStageStep)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # one-side (necessary when user wants to creata a custom Stage)
	name = db.Column(db.String(60))
	closing_perc = db.Column(db.Numeric(2,2))
	private = db.Column(db.Boolean(), default=True)

	def __repr__(self):
		return "<Stage: {}>".format(self.name)



class Status(db.Model):
	__tablename__ = 'status'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)
	stage_steps = db.relationship('OpportunityStep', foreign_keys=[OpportunityStep.status_id],  backref='status', lazy='dynamic', cascade='all, delete-orphan')	

	def __repr__(self):
		return "<{}>".format(self.name)



class Task(db.Model):
	__tablename__ = 'tasks'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # many-to-one with User (one side)
	opportunity_step_id = db.Column(db.Integer, db.ForeignKey('opportunity_steps.id'), default=None)
	title = db.Column(db.String(60))
	content = db.Column(db.String(240), nullable=True)
	priority = db.Column(db.String(30))
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	due_date = db.Column(db.DateTime)
	done = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return "<Task: {}>".format(self.title)



class Note(db.Model):
	__tablename__ = 'notes'
	id = db.Column(db.Integer, primary_key=True)
	opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), default=None)
	contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), default=None)
	company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), default=None)
	content = db.Column(db.String(2000), default='')
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return "<Note: {}.>".format(self.id)



# A function called by the flask-login extension when it needs to load a user based on its id
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)



def distinct_priority_values():
	values = ['Haute', 'Moyenne', 'Basse']
	# values = ["",'Haute', 'Moyenne', 'Basse']
	labels = ['Haute', 'Moyenne', 'Basse']
	# labels = ["---",'Haute', 'Moyenne', 'Basse']
	return list(zip(values, labels))



def distinct_stages_values():
	'''	Exctract distinct names from Status table.
		Return a dict with each value paired with a label that will be displayed on the form field '''
	try:
		distinct_stages = db.session.query(CommercialStage.name).distinct().all()
	except:
		distinct_stages = [('',)]
	# list_distinct_stages = [elt[0] for elt in distinct_stages]
	list_distinct_stages = list(map(itemgetter(0), distinct_stages))
	form_field_labels = [str(elt[0]).replace(' ','_').capitalize().replace('_',' ') for elt in distinct_stages] # not really necessary anymore since database value are the same as the one we shoul display
	dict_distinct_stages = list(zip(list_distinct_stages, form_field_labels))
	return dict_distinct_stages



def distinct_status_values():
	''' Exctract distinct status title's from Status table.
		Return a dict with each value paired with a label that will be displayed on the form field '''
	try:
		distinct_status = db.session.query(Status.name).distinct().order_by(Status.name.desc()).all()
	except:
		distinct_status = [('',)]
	list_distinct_status = [elt[0] for elt in distinct_status]
	form_field_labels = [str(elt[0]).capitalize().replace('_',' ') for elt in distinct_status]
	dict_distinct_status = list(zip(list_distinct_status, form_field_labels)) #we need a list to access it multiple times
	return dict_distinct_status


def get_list_contacts_positions():
	q1 = db.session.query(ContactLead.position.label('position')).distinct()
	# list_distinct_position = [elt.position for elt in q1.all()] # keeping None as position is not a required field
	list_distinct_position = map(itemgetter('position'), q1.all())# keeping None as position is not a required field
	return list_distinct_position


def get_list_companies_activities():
	q1 = db.session.query(CompanyLead.activity_field1.distinct().label("field"))
	# q2 = db.session.query(CompanyLead.activity_field2.distinct().label("field"))
	# q3 = db.session.query(CompanyLead.activity_field3.distinct().label("field"))
	# list_distinct_activities = [elt.field for elt in q1.union(q2).union(q3).all() if elt.field] # removing None as activty is a required field in db
	list_distinct_activities = [elt.field for elt in q1.all() if elt.field] 
	return list_distinct_activities



def distinct_companies_activity_values():
	''' Exctract distinct field_actvity from CompanyLead table.
		Query distinct field for each of the 3 field's column and join together.
	 	Then reformat data to return a list of tupple.
	 	Each value paired with a label that will be displayed on the form field '''
	list_distinct_activities = get_list_companies_activities()
	form_field_labels = [elt.capitalize() for elt in list_distinct_activities]
	dict_labels_activities = list(zip(list_distinct_activities, form_field_labels))
	companies_activities = [("", "-")] + dict_labels_activities
	return companies_activities


# def from_sql(row):
#     """	Translates a SQLAlchemy model instance into a dictionary """
#     data = row.__dict__.copy()
#     data['id'] = row.id
#     data.pop('_sa_instance_state')
#     return data

def from_sql(row):
	"""Translates a SQLAlchemy model instance into a dictionary"""
	if not row:
		return []
	else:	
	    data = row.__dict__.copy()
	    data['id'] = row.id
	    data.pop('_sa_instance_state')
	    return data


def get_list_companies(user_id, limit, cursor):
	user_id = int(user_id)
	cursor = int(cursor) if cursor else 0
	query = (Company.query
			.filter(Company.user_id==user_id)
			.order_by(Company.name, Company.creation_date.desc()) )
	size = len(query.all())
	query = (query.offset(cursor)
				  .limit(limit+1) ) # limit + 1 to check whether there is a need for a 'next_page' btn
	companies = list(query.all())
	# propsects =  query.all()# return a sqlalchemy obj
	next_page = cursor + limit if len(companies)>limit else None 
	previous_page = cursor - limit if cursor >= limit else None 
	return (companies[:limit], next_page, previous_page, size)



def get_list_contacts(user_id, limit, cursor):
	user_id = int(user_id)
	cursor = int(cursor) if cursor else 0
	query = (Contact.query
			.filter_by(user_id=user_id)
			.order_by(Contact.last_name, Contact.creation_date.desc()))
	size = len(query.all())
	query = (query.offset(cursor)
				  .limit(limit+1) )
	# contacts = list(map(from_sql, query.all())) # return a list of dict, we loose relationship
	contacts = list(query.all())
	next_page = cursor + limit if len(contacts) > limit else None
	previous_page = cursor - limit if cursor >= limit else None
	return (contacts[:limit], next_page, previous_page, size)



def get_list_opportunities(user_id, limit, cursor):
	user_id = int(user_id)
	cursor = int(cursor) if cursor else 0
	query = (Opportunity.query
			.filter_by(user_id=user_id)
			.outerjoin(Company)
			.order_by(Company.name, Opportunity.creation_date.desc())
			.offset(cursor)
			.limit(limit+1) ) # limit + 1 to check whether there is a need for a 'next_page' btn
	# opportunities = list(map(from_sql, query.all()))
	opportunities =  query.all()# return a sqlalchemy obj
	next_page = cursor + limit if len(opportunities)>limit else None 
	previous_page = cursor - limit if cursor > 0 else None
	return (opportunities[:limit], next_page, previous_page)



def get_leads_ids(data):
	"""
	"""	
	# To keep but not used in the way we operate now
	# max_exports = current_user.subscriptions.order_by(Subscription.subscription_date.desc()).first().plan.limit_daily_query
	# today_requests = [elt.id for elt in current_user.requested_leads.all() if elt.query_date.date()==datetime.utcnow().date()]
	# remaining_exports = min(max_exports, max_exports-len(today_requests))


	# Set a random seed to assure the same results if request is launched again
	random.seed(int(datetime.utcnow().strftime('%Y%m%d'))*current_user.id)	
	results_len = list(np.random.randint(low=4, high=14, size=1))[0]*10 # number of results to be displayed (random nb of page) * (number of results per page)
	# results_len = 3

	# Create a list from the value selected by the user in the activity_field.
	# We need to do that as the activities chosen will be passed in a "in_" filter which only supports list
	# Return a list of all activities if no specific acitvity is chosen
	activity_filter = [data.get('company_activity_field')] if data.get('company_activity_field') else get_list_companies_activities()
	print("activity: {}".format(activity_filter))

	# User requested company leads
	if data.get('leads_type') == 'company':
		# Ids from companies that already have been queried
		requested_companies_ids = [elt.company_lead_id for elt in current_user.requested_leads.all() if not elt.company_lead_id is None]
		# Query by filter on activity_field and removing previous query results
		leads_query = db.session.query(CompanyLead).filter((CompanyLead.activity_field1.in_(activity_filter) | 
												   CompanyLead.activity_field2.in_(activity_filter) |
												   CompanyLead.activity_field3.in_(activity_filter) ),
												   ~CompanyLead.id.in_(requested_companies_ids))
		# If exists, add location filter
		if data.get('company_location'):
			location_filter = "{}%".format(data.get('company_location'))
			print("location: {}".format(location_filter))
			leads_query = leads_query.filter(CompanyLead.postal_code.like(location_filter))			
	
	# User requested contact leads	
	else:
		requested_contacts_ids = [elt.contact_lead_id for elt in current_user.requested_leads.all() if not elt.contact_lead_id is None]
		# Get company with required filed of activity
		sub_query  = db.session.query(CompanyLead).filter(CompanyLead.activity_field1.in_(activity_filter) | 
											   			  CompanyLead.activity_field2.in_(activity_filter) |
											   			  CompanyLead.activity_field3.in_(activity_filter) ).subquery()
		if data.get('location'):
			location_filter = "{}%".format(data.get('location'))
			print("location: {}".format(location_filter))
			sub_query = sub_query.filter(CompanyLead.postal_code.like(location_filter))

		leads_query = db.session.query(ContactLead).filter(~ContactLead.id.in_(requested_contacts_ids))
		leads_query = leads_query.join(sub_query, ContactLead.company_id==sub_query.c.id)

		if data.get('position'):
			position_filter = "%{}%".format(data.get('position'))
			print("position: {}".format(position_filter))
			leads_query = leads_query.filter(ContactLead.position.like(position_filter))
	
	# Return a random list of the requested leads whom size is the mini btw all the results size and the number of results to be displayed (random nb of page) * (number of results per page)
	requested_leads_id = [elt.id for elt in list(leads_query.all())] 
	random_leads_id = random.sample(requested_leads_id, min(len(requested_leads_id), results_len))
	# print('random_ids: {}'.format(random_leads_id))
	return (random_leads_id, data.get('leads_type'))




def get_displayed_leads(leads_ids, leads_type, cursor, limit=10):
	"""
	"""	
	print('ids: {}'.format(leads_ids))
	print('type: {}'.format(leads_type))
	print('cursor: {}'.format(cursor))
	print('limit: {}'.format(limit))
	if leads_type is None:
		leads_to_show = []
	else:
		if leads_type=='company':
			leads_to_show = db.session.query(CompanyLead).filter(CompanyLead.id.in_(leads_ids)).offset(cursor).limit(limit+1).all()
		else:
			leads_to_show = db.session.query(ContactLead).filter(ContactLead.id.in_(leads_ids)).offset(cursor).limit(limit+1).all()

	next_page_token = cursor + limit if len(leads_to_show) > limit else None
	previous_page_token = cursor - limit if cursor >= limit else None	
	print('next_page_token: {}'.format(next_page_token))
	print('previous_page_token: {}'.format(previous_page_token))
	return (leads_to_show[:limit], next_page_token, previous_page_token)


def compute_remaining_leads():
	'''	Compute the number of leads left to be queried'''
	user = current_user
	todays_leads = [record.id for record in user.requested_leads.all() if datetime.strftime(record.query_date, '%Y-%m-%d')==datetime.strftime(datetime.utcnow(), '%Y-%m-%d')]
	latest_sub = db.session.query(Subscription).filter(Subscription.user_id==user.id).order_by(Subscription.subscription_date.desc()).first()
	max_requests = latest_sub.plan.limit_daily_query
	return max_requests-len(todays_leads)

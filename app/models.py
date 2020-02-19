from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from datetime import datetime
# from db import Column, String, Integer, Boolean, DateTime, ForeignKey, relationship, backref


class Subscription(db.Model):
	__tablename__ = 'subscriptions'
	plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), primary_key=True)# one side
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)# one side
	yearly = db.Column(db.Boolean, default=False)
	subscription_date = db.Column(db.DateTime, default=datetime.utcnow)

	def is_valid(self):
		if Plan.query.get(self.plan_id).plan_name == 'Beta':
			return True
		if self.yearly:
			limit_subscription =  self.subscription_date.replace(year=self.subscription_date.year+1)
		else:
			limit_subscription = self.subscription_date.replace(month=self.subscription_date.month+1)
		return limit_subscription >= datetime.utcnow()

	def __repr__(self):
		return "<On {}, user {} subscribed to a yearly({}) plan {}>".format(self.subscription_date, self.user_id, self.yearly, self.plan_id )



class LeadRequest(db.Model):
	__tablename__ = 'lead_requests'
	lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), primary_key=True)# one-to-many (one side)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)# one side
	query_date = db.Column(db.DateTime, default=datetime.utcnow)

	def exists(self):
		request = LeadRequest.query.filter(LeadRequest.lead_id==self.lead_id, LeadRequest.user_id==self.user_id).first()
		if not request:
			return False
		return True


	def __repr__(self):
		return "<On {}, user {} queried lead {}>".format(self.query_date, self.user_id, self.lead_id)



class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(30))
	last_name = db.Column(db.String(30))
	username = db.Column(db.String(60), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	stripe_customer_id = db.Column(db.String(256), nullable=True)
	password_hash = db.Column(db.String(120))
	registration_date = db.Column(db.DateTime, default=datetime.utcnow)
	# avatar = db.Column(db.String(120))
	admin = db.Column(db.Boolean, default=False)
	subscriptions = db.relationship('Subscription', foreign_keys=[Subscription.user_id], backref=db.backref('user', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side
	leads_requested = db.relationship('LeadRequest', foreign_keys=[LeadRequest.user_id], backref=db.backref('user', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side
	contacts = db.relationship('Contact', backref='user', lazy='dynamic')# one-to-many (many side)
	opportunities = db.relationship('Opportunity', backref='user', lazy='dynamic')# one-to-many (many-side)
	commercial_stages = db.relationship('CommercialStage', backref='user', lazy='dynamic')# one-to-many (many-side)
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
		# self.set_avatar()

	def __repr__(self):
		return "<{}>".format(self.username)



class Plan(db.Model):
	__tablename__ = 'plans'
	id = db.Column(db.Integer, primary_key=True)
	plan_name = db.Column(db.String(30), index=True)
	monthly_price = db.Column(db.Integer)
	yearly_price = db.Column(db.Integer)
	limit_daily_query = db.Column(db.Integer)
	crm_access = db.Column(db.Boolean, default=False)
	subscriptions = db.relationship('Subscription', foreign_keys=[Subscription.plan_id], backref=db.backref('plan', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side

	def __repr__(self):
		return "<{}>".format(self.plan_name)



class Lead(db.Model):
	__tablename__ = 'leads'
	id = db.Column(db.Integer, primary_key=True)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	company_name = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_address = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_postal_code = db.Column(db.String(30), index=False, unique=False, nullable=True)
	company_city = db.Column(db.String(60), index=False, unique=False, nullable=True)
	company_email = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_email_bcc = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_phone = db.Column(db.String(60), index=False, unique=False, nullable=True)
	company_activity_field = db.Column(db.String(60), index=True, unique=False, nullable=False)
	owner_firstname	= db.Column(db.String(60), index=True, unique=False, nullable=True)
	owner_lastname = db.Column(db.String(60), index=True, unique=False, nullable=True)
	requests = db.relationship('LeadRequest', foreign_keys=[LeadRequest.lead_id], backref=db.backref('lead', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side

	def exists(self):
		lead = Lead.query.filter(Lead.company_name==self.company_name, Lead.company_postal_code==self.company_postal_code).first()
		if not lead:
			return False
		return True

	def __repr__(self):
		return "<{} situe a {}>".format(self.company_name, self.company_city)



class CommercialStageStep(db.Model):
	__tablename__ = 'commercial_stage_steps'	
	opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), primary_key=True)# pk
	commercial_stage_id = db.Column(db.Integer, db.ForeignKey('commercial_stages.id'), primary_key=True)# pk
	status_id = db.Column(db.Integer, db.ForeignKey('status.id'), primary_key=True)# many-to-one (one side)
	note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)
	task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True) # task activated only when status == 'a faire'
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	last_update = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return "<Opp. {} on stage {} with status {} created on {}>".format(self.opportunity.name, self.commercial_stage.name, self.status.title, self.creation_date)


class Contact(db.Model):
	__tablename__ = 'contacts'
	id = db.Column(db.Integer, primary_key=True)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	company_name = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_address = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_postal_code = db.Column(db.String(30), index=False, unique=False, nullable=True)
	company_city = db.Column(db.String(60), index=False, unique=False, nullable=True)
	company_email = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_email_bcc = db.Column(db.String(120), index=False, unique=False, nullable=True)
	company_phone = db.Column(db.String(60), index=False, unique=False, nullable=True)
	company_activity_field = db.Column(db.String(60), index=True, unique=False, nullable=False)
	owner_firstname	= db.Column(db.String(60), index=True, unique=False, nullable=True)
	owner_lastname = db.Column(db.String(60), index=True, unique=False, nullable=True)
	website = db.Column(db.String(120), index=False, unique=False, nullable=True)
	facebook = db.Column(db.String(120), index=False, unique=False, nullable=True)
	instagram = db.Column(db.String(120), index=False, unique=False, nullable=True)
	linkedin = db.Column(db.String(120), index=False, unique=False, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # one-side of a many-to-one with User 
	opportunities = db.relationship('Opportunity', backref='contact', lazy='dynamic') # one-to-many (many side)

	def __repr__(self):
		return  "<{} situé à {}>".format(self.company_name, self.company_city)


class Opportunity(db.Model):
	__tablename__ = 'opportunities'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
	name = db.Column(db.String(120), nullable=False)
	euros_value = db.Column(db.Numeric(8,2))
	commercial_stages = db.relationship('CommercialStageStep', foreign_keys=[CommercialStageStep.opportunity_id], backref=db.backref('opportunity', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many-to-many with CommercialStage (many side of a many-to-one with CommercialStageStep)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	deal_closed = db.Column(db.Boolean, default=False)
	last_update = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return "<{}>".format(self.name)



class Task(db.Model):
	__tablename__ = 'tasks'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # many-to-one with User (one side)
	stage_step = db.relationship('CommercialStageStep', foreign_keys=[CommercialStageStep.task_id], backref=db.backref('task', uselist=False))# one-to-one
	task_title = db.Column(db.String(60))
	task_content = db.Column(db.String(240))
	priority = db.Column(db.String(30))
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)
	due_date = db.Column(db.DateTime)
	done = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return "<Task: {}. Stage: {}>".format(self.task_title, self.stage_step)



class Note(db.Model):
	__tablename__ = 'notes'
	id = db.Column(db.Integer, primary_key=True)
	stage_step = db.relationship('CommercialStageStep', foreign_keys=[CommercialStageStep.note_id], backref=db.backref('note', uselist=False))# one-to-one  
	note_content = db.Column(db.String(240), default='')
	creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class CommercialStage(db.Model):
	__tablename__ = 'commercial_stages'
	id = db.Column(db.Integer, primary_key=True)
	stage_steps = db.relationship('CommercialStageStep', foreign_keys=[CommercialStageStep.commercial_stage_id], backref=db.backref('commercial_stage', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many-to-many with Opportunity (many side of a many-to-one with CommercialStageStep)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # one-side (necessary when user wants to creata a custom Stage)
	name = db.Column(db.String(60))
	closing_perc = db.Column(db.Numeric(2,2))
	private = db.Column(db.Boolean(), default=True)

	def __repr__(self):
		return "<{}>".format(self.name)



class Status(db.Model):
	__tablename__ = 'status'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30), unique=True)
	stage_steps = db.relationship('CommercialStageStep', foreign_keys=[CommercialStageStep.status_id],  backref=db.backref('status', lazy='joined'))	

	def __repr__(self):
		return "<{}>".format(self.title)



# A function called by the flask-login extension when it needs to load a user based on its id
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)



def from_sql(row):
    """	Translates a SQLAlchemy model instance into a dictionary """
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data



def distinct_priority_values():
	values = ["",'Haute', 'Moyenne', 'Basse']
	labels = ["---",'Haute', 'Moyenne', 'Basse']
	return zip(values, labels)



def distinct_stages_values():
	'''	Exctract distinct names from Status table.
		Return a dict with each value paired with a label that will be displayed on the form field '''
	try:
		distinct_stages = db.session.query(CommercialStage.name).distinct().all()
	except:
		distinct_stages = [('',)]
	list_distinct_stages = [elt[0] for elt in distinct_stages]
	form_field_labels = [str(elt[0]).replace(' ','_').capitalize().replace('_',' ') for elt in distinct_stages]
	dict_distinct_stages = zip(list_distinct_stages, form_field_labels)
	return dict_distinct_stages



def distinct_status_values():
	''' Exctract distinct status title's from Status table.
		Return a dict with each value paired with a label that will be displayed on the form field '''
	try:
		distinct_status = db.session.query(Status.title).distinct().all()
	except:
		distinct_status = [('',)]
	list_distinct_status = [elt[0] for elt in distinct_status]
	form_field_labels = [str(elt[0]).capitalize().replace('_',' ') for elt in distinct_status]
	dict_distinct_status = zip(list_distinct_status, form_field_labels)
	return dict_distinct_status



def distinct_activity_values():
	''' Exctract distinct field_actvity from Lead table.
	 	Return a dict with each value paired with a label that will be displayed on the form field '''
	try:
		distinct_activities = db.session.query(Lead.company_activity_field).distinct().all()
	except:
		distinct_activities = [('fitness',)]
	list_distinct_activities = [elt[0] for elt in distinct_activities]
	form_field_labels = [str(elt[0]).capitalize() for elt in distinct_activities]
	dict_labels_activities = list(zip(list_distinct_activities, form_field_labels))
	dict_labels_activities = [("", "-")] + dict_labels_activities
	return dict_labels_activities


def get_list_prospects(user_id, limit, cursor):
	user_id = int(user_id)
	cursor = int(cursor) if cursor else 0
	query = (Contact.query
			.filter(Contact.user_id==user_id)
			.order_by(Contact.company_name, Contact.creation_date.desc())
			.offset(cursor)
			.limit(limit+1) ) # limit + 1 to check whether there is a need for a 'next_page' btn
	prospects = list(map(from_sql, query.all()))
	# propsects =  query.all()# return a sqlalchemy obj
	next_page = cursor + limit if len(prospects)>limit else None 
	previous_page = cursor - limit if cursor > 0 else None
	return (prospects[:limit], next_page, previous_page)


def get_list_opportunities(user_id, limit, cursor):
	user_id = int(user_id)
	cursor = int(cursor) if cursor else 0
	query = (Opportunity.query
			.filter_by(user_id=user_id)
			.outerjoin(Contact)
			.order_by(Contact.company_name, Opportunity.creation_date.desc())
			.offset(cursor)
			.limit(limit+1) ) # limit + 1 to check whether there is a need for a 'next_page' btn
	# opportunities = list(map(from_sql, query.all()))
	opportunities =  query.all()# return a sqlalchemy obj
	next_page = cursor + limit if len(opportunities)>limit else None 
	previous_page = cursor - limit if cursor > 0 else None
	return (opportunities[:limit], next_page, previous_page)



from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates



# A function called by the flask-login extension when it needs to load a user based on its id
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)



def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data



def distinct_activities_field():
	'''
		Exctract discting field_actvity from Lead table.
	 	Return a dict with activity paired with a label for the form fiel
	 '''
	try:
		distinct_activities = db.session.query(Lead.company_activity_field).distinct().all()
	except:
		distinct_activities = [('fitness',)]
	list_distinct_activities = [elt[0] for elt in distinct_activities]
	form_field_labels = [str(elt[0]).capitalize() for elt in distinct_activities]
	dict_labels_activities = list(zip(list_distinct_activities, form_field_labels))
	dict_labels_activities = [("", "-")] + dict_labels_activities
	return dict_labels_activities



class Subscription(db.Model):
	__tablename__ = 'subscriptions'
	plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), primary_key=True)# one side
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)# onde side
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
	lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), primary_key=True)# one side
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)# one side
	query_date = db.Column(db.DateTime, default=datetime.utcnow())

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
	password_hash = db.Column(db.String(120))
	registration_date = db.Column(db.DateTime, default=datetime.utcnow)
	admin = db.Column(db.Boolean, default=False)
	subscriptions = db.relationship('Subscription', foreign_keys=[Subscription.user_id], backref=db.backref('user', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side
	leads_requested = db.relationship('LeadRequest', foreign_keys=[LeadRequest.user_id], backref=db.backref('user', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')# many side
	customers = db.relationship('Customer', backref='user', lazy='dynamic')# many side 
	
	@validates(first_name, last_name)
	def capitalize(self, key, value):
		return value.capitalize()

	def set_username(self):
		self.username = str(self.first_name).capitalize() + '_' + str(self.last_name).capitalize()

	def set_password(self, password_entry):
		self.password_hash = generate_password_hash(password_entry)

	def verify_password(self, password_entry):
		return check_password_hash(self.password_hash, password_entry)

	def is_admin(self):
		return self.admin

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.set_username()

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
	creation_date = db.Column(db.DateTime, default=datetime.utcnow())
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
		return "<{} located at {}>".format(self.company_name, self.company_postal_code)



class Customer(db.Model):
	__tablename__ = 'customers'
	id = db.Column(db.Integer, primary_key=True)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow())
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
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))



# class CustomerStatus(db.Model):
	


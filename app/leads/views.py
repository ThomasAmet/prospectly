# >>> ql1 = db.session.query(CompanyLead).filter(CompanyLead.postal_code.like('75001%'))
# >>> ql2 = db.session.query(CompanyLead).filter(CompanyLead.postal_code.like('94%'))
# >>> ql3 = db.session.query(CompanyLead).filter(CompanyLead.activity_field1.in_(['Conseil']) | CompanyLead.activity_field2.in_(['Conseil']) | CompanyLead.activity_field3.in_(['Conseil']))
# >>> activity_filter ['Conseil', 'SMMA']
# >>> ql4 = db.session.query(CompanyLead).filter(CompanyLead.activity_field1.in_(activity_filter) | CompanyLead.activity_field2.in_(activity_filter) | CompanyLead.activity_field3.in_(activity_filter))
# >>> activity_filter ['Conseil']
# >>> ql5 = db.session.query(CompanyLead).filter((CompanyLead.activity_field1.in_(activity_filter) | CompanyLead.activity_field2.in_(activity_filter) | CompanyLead.activity_field3.in_(activity_filter)) & CompanyLead.postal_code.like('75%'))
# >>> activity_filter ['Conseil','Plombier']
# >>> ql6 = db.session.query(CompanyLead).filter((CompanyLead.activity_field1.in_(activity_filter) | CompanyLead.activity_field2.in_(activity_filter) | CompanyLead.activity_field3.in_(activity_filter)) & CompanyLead.postal_code.like('94%'))
# >>> ql7 = Patient.query.filter(Patient.mother.has(phenoscore=10)) #use has() on reltionship
# >>> ql8 = Patient.query.join(Patient.mother, aliased=True).filter_by(phenoscore=10)


import os
import pandas as pd
import numpy as np
import random
import logging
logging.basicConfig(level=logging.INFO)

from datetime import datetime
from flask import render_template, redirect, url_for, flash, session, make_response, request
from flask_login import current_user, login_required
from app.auth.views import admin_login_required, pro_plan_required, valid_subscription_required
from werkzeug.utils import secure_filename
from . import leads
from .forms import CompaniesQueryForm, ContactsQueryForm, LeadsQueryForm
from .. import app, db
from ..models import User, Subscription, Company, Contact, CompanyLead, ContactLead, LeadRequest, from_sql, get_list_companies_activities

# from ...bin import all_utils




@leads.route('/generator', methods=['POST', 'GET'])
# @leads.route('/prospectly-generator', methods=['POST', 'GET'])
@login_required
@admin_login_required
@valid_subscription_required
def view_leads():
	comp_lead_form = CompaniesQueryForm()
	
	# The following chunk is to handle when there is multiple pages to display, the ids are store in session so we can navigate through pages 
	leads_ids = session.get('leads_ids') if session.get('leads_ids') else None
	leads_type = request.args.get('leads_type') if request.args.get('leads_type') else None
	token = int(request.args.get('page_token')) if request.args.get('page_token') else 0
	# store the page token in session  for the user to be redirected back to it after importing leads
	session['leads_token'] = token
	

	if request.method=='POST':
		data = request.form.to_dict(flat=True)
		leads_ids, leads_type = get_leads_ids(data)
		session.pop('leads_ids') if session.get('leads_ids') else None
		session['leads_ids'] = leads_ids
		# print('session (POST): {}'.format(session.get('leads_ids')))
	
	all_leads_len = len(leads_ids) if leads_type  else 0	 
	leads_to_show, next_page_token, previous_page_token = get_displayed_leads(leads_ids, leads_type, token, limit=2) 
	# print('leads to display: {}'.format(leads_to_show))
	return render_template('generator.html', comp_lead_form=comp_lead_form, leads=leads_to_show, lead_type=leads_type, 
		next_page_token=next_page_token, previous_page_token=previous_page_token, current_page_token=token, all_leads_len=all_leads_len)




@leads.route('/import-entreprises', methods=['POST'])
@login_required
# @pro_plan_required
# @admin_login_required
# @valid_subscription_required
def upload_company_leads():

	data = request.get_json(silent=True)
	print('data: {}'.format(data))

	if not data.get('leads_ids'):
		return make_response(url_for('leads.view_leads'), 400)

	for lead_id in data.get('leads_ids'):
		lead = from_sql(CompanyLead.query.get(lead_id))
		print("lead dict: {}".format(lead))
		# Drop attribute that we wont use if we update an exisiting Company
		lead.pop('id')

		# It is possible that the user already imported a contact_lead from this company, hence this company should exists in user's companies table
		# Check if the company_lead to  uploqd already exists in user's Company's table (then update values) or if we have to create it
		# q1 retrieves the company_id (user side) if a former lead_request contains the same company_lead_id
		query1 = db.session.query(LeadRequest.company_id).filter(LeadRequest.user_id==current_user.id, LeadRequest.company_lead_id==lead_id) # checking if the user already requested a contact from that company. If yes we use the same Company's id
		# It is also possible that the user already has the company in its companies tables,
		# q2 checks whether there is a a company in user's table that has the same name as the company_leads one 
		query2 = db.session.query(Company.id).filter(Company.user_id==current_user.id, Company.name==lead.get('name'))
		
		if query1.first():
			company = Company.query.get(query1.first())
			for k,v in lead.items():
				setattr(company, k, v)
		elif query2.first():
			# We update the existing one but we should first throw a warning to the user
			company = Company.query.get(query2.first())
			for k,v in lead.items():
				setattr(company, k, v)
		else:
			lead.pop('creation_date')
			lead['user_id'] = current_user.id

			if data['activity_field']:
				lead['activity_field'] = data.get('activity_field')
			else:
				lead['activity_field'] = lead['activity_field1']

			lead.pop('activity_field1')
			lead.pop('activity_field2')
			lead.pop('activity_field3')
			
			company = Company(**lead)
			db.session.add(company)
			db.session.flush()
		
		# Record the query
		lead_request = LeadRequest(user_id=current_user.id, company_lead_id=lead_id, company_id=company.id)
		db.session.add(lead_request)

	db.session.commit()	
	flash('Les leads ont été importés')
	return make_response(url_for('leads.view_leads', token=session.get('leads_token')), 400)



@leads.route('/import-contacts', methods=['POST'])
# @pro_plan_required
@admin_login_required
@valid_subscription_required
def upload_contact_leads():
	data = request.get_json()
	print('Upload Contact data: {}'.format(data))

	for lead_id in data.get('leads_ids'):
		contact_lead = from_sql(ContactLead.query.get(lead_id))
		contact_lead.pop('creation_date')
		company_lead = from_sql(CompanyLead.query.get(contact_lead.get('company_id')))
		contact_lead.pop('company_id')
		company_lead.pop('creation_date')

		if data['activity_field']:
			company_lead['activity_field'] = data.get('activity_field')
		else:
			company_lead['activity_field'] = company_lead['activity_field1']

		# Look for the contact's associated company in user's companies table
		query1 = db.session.query(LeadRequest.company_id).filter_by(LeadRequest.user_id==current_user.id, LeadRequest.company_lead_id==company_lead.id) # checking if the user already requested a contact from that company. If yes we use the same Company's id
		query2 = db.session.query(Company.id).filter_by(Company.user_id==current_user.id, Company.name==company_lead.name)
		
		if query1.first():
			contact_lead['company_id'] = query1.first()
		elif query2.first():
			contact_lead['company_id'] = query2.first()
		# create the company if doesnt found in Company table (but limit the information that we provide to 'name, activity, postal_code, city')
		else:
			company = Company(name=company_lead.get('name'), activity_field=company_lead.get('activity_field'),
							  city=company_lead.get('city'), postal_code=company_lead.get('postal_code'))
			db.session.add(company)
			db.session.flush()
			contact_lead['company_id'] = company.id 
		
		contact = Contact(**contact_lead) 
		db.session.add(contact)
		db.session.flush()

		lead_request = LeadRequest(user_id=current_user.id, contact_lead_id=lead_id, contact_id=contact.id)
		db.session.add(lead_request)

		print('contact_lead: {}'.format(contact_lead))
		print('company_lead: {}'.format(company_lead))
		db.session.commit()

	return make_response(url_for('leads.view_leads', token=session.get('leads_token')), 400)



@leads.route('/generator2', methods=['POST', 'GET'])
@admin_login_required
def query():
	form = LeadsQueryForm()	
	cu = current_user

	# Get the latest subscription
	user_subscription = cu.subscriptions.order_by(Subscription.subscription_date.desc()).first()

	if not user_subscription or not user_subscription.is_valid:
		flash('Vous devez souscrire à un abonnement pour bénéficier de ce service')
		return redirect(url_for('main.pricing'))

	output_max_len = user_subscription.plan.limit_daily_query
	output_max_len = 5

	# Check if the current user already requested some leads today and store the result in cookies
	if not 'todays_output' in session:
		session['todays_output'] = list(map(from_sql, [record.lead for record in cu.leads_requested.all() if datetime.strftime(record.query_date, '%Y-%m-%d')==datetime.strftime(datetime.utcnow(), '%Y-%m-%d')]))
	
	# Click Download Button
	if request.method=='POST' and request.form['btn']=='Telecharger':
		return redirect(url_for('leads.download'))

	# Click New Leads Button
	if request.method=='POST' and request.form['btn']=='Nouveaux Leads':
		# try:
		# Check if the user already requested all exisiting leads
		if len(cu.leads_requested.all())==len(Lead.query.all()):
			flash('De nouveaux leads arrivent bientot ...')
		# If not, check whether the user already reached the daily limit for leads result
		elif len(session['todays_output'])>=output_max_len:
			flash('Revenez demain pour de nouveaux leads')
		# Last case scenario, the user has still some leads left to query (part of its daily limit or all of it)
		else:
			request_filters = [form.activity_field.data, form.postal_code.data]# get filter for the query from the form fields
			excluding_leads = [record.lead_id for record in cu.leads_requested.all()]# id of leads already requested to be excluded from the result
			query_output_all = Lead.query.filter(Lead.company_activity_field==request_filters[0], Lead.company_postal_code.like(request_filters[1]+'%'), ~Lead.id.in_(excluding_leads)).all()# use ~ not_() to negate 
			
			# No new result for that query
			if not query_output_all:
				flash("Aucun nouveau lead ne correspond a votre requete")
			else:
				# Output size is the minimum between the size of the query result and the nb of result left for the day
				new_output_len = min(output_max_len-len(session['todays_output']), len(query_output_all))
				# Extend the exisiting result of the day with a random selection of all possisble results
				new_query_output = list(map(from_sql, np.random.choice(query_output_all, new_output_len).tolist()))
				# As the result is store in user session, we add a new lead_request in db as soon as it has been requested to avoid the user to get the information from cookies and to avoid duplicating value in user session
				for lead in new_query_output:
					lead_request = LeadRequest(lead_id=lead['id'], user_id=cu.id) 
					if lead_request.exists():
						continue
					else:
						db.session.add(lead_request)
				db.session.commit()
				# flash('todays_output before extend:{}'.format(session['todays_output']))
				# flash('new_query_output: {}'.format(new_query_output))
				
				# We store the new query results + existing results for the day in session for later download. We ONLY do it AFTER storing lead requests in the table to avoid duplicating value in user session
				session['todays_output'].extend(new_query_output)
				
				flash('todays_output after extend:{}'.format(session['todays_output']))
		return redirect(url_for('leads.query', form=form, request_output=session['todays_output']))
		
		# except:
		# 	# If anything goes wrong we rollback the database
		# 	db.session.rollback()
		# 	return redirect(url_for('auth.login'))# change redirect to error page 505
	# flash('left to query: {}'.format(output_max_len-len(session['todays_output'])))
	flash(session['todays_output'])
	return render_template('generator.html', comp_lead_form=form, request_output=session['todays_output'])



@leads.route('/telechargement')
@admin_login_required
def download():
	# Transform session value into dataframe and reorder the columns
	df = pd.DataFrame(session['todays_output'])	
	df = df[['company_name', 'company_activity_field', 'company_address', 'company_postal_code', 'company_city', 'company_email', 'company_email_bcc', 'company_phone', 'owner_firstname', 'owner_lastname']]
	# Make the response to return a csv
	output = make_response(df.to_csv(index=False, encoding='utf-8'))
	output.headers["Content-Disposition"] = "attachment; filename=export.csv"
	output.headers["Content-Type"] = "text/csv"
	# Drop the session variable
	session.pop('todays_output', None)
	return output



@leads.route('/import', methods=['POST', 'GET'])
@login_required
@admin_login_required
def import_csv():
	# Create a necessary cookie to render the page
	if not 'uploaded' in session:
		session['uploaded'] = False

	# LOAD FILE
	if request.method == 'POST' and request.form['btn']=='Charger le fichier':
		# The 'request' method has a property 'form' which is a MultiDict object containing all uploaded files.
		logging.info('Loading file')
		# Same for 'files' method. Each key in files is the name from the <input type="file" name="">. Each value in files is a Werkzeug FileStorage object.
		file = request.files['csv_input']

		# Check if the post request has the file part
		if 'csv_input' not in request.files:
			flash('Pas de fichier selectionne.')
			return redirect(request.url)

		if file.filename == '':
			flash('Pas de fichier selectionne.')
			return redirect(request.url)

		if file and allowed_file(file.filename):
			filename = current_user.username.lower() + '_' + secure_filename(file.filename)
			filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			session['filepath'] = filepath
			file.save(filepath)
			flash('Chargement reussi')
			session['uploaded'] = True
			return redirect(url_for('leads.import_csv'))

	# DISPLAY DATA		
	if request.method=='POST' and request.form['btn']=='Afficher les donnees':
		logging.info('Displaying data')
		# Replace this line using utils.load_csv function
		leads_df = pd.read_csv(session['filepath'], sep=',', header=0, encoding='latin-1')#utf-8 or latin-1 
		# return redirect(url_for('leads.import_csv'))
		return render_template('leads/render.html', column_names=leads_df.columns.values, row_data=leads_df.values.tolist(), zip=zip)

	# IMPORT DATA
	if request.method=='POST' and request.form['btn']=='Importer les donnees':
		logging.info('Import data')
		# Replace this line using utils.load_csv function
		leads_df = pd.read_csv(session['filepath'], sep=',', encoding='latin-1')#utf-8 or latin-1 
		# Clean file: remove . in postal code / make sure phone starts by 0 and as not . but spaces
		leads_df = clean_leads_input(leads_df)
		logging.info(leads_df)
		# Replace by populate_leads_table function using function in utils
		try:
			# ix is index of the row, row is a pd.Series object reprensenting the row information
			for ix, row in leads_df.iterrows():
				# change from pd.Series to dict to pass it as **kwargs
				lead_data = dict(row)
				lead = Lead(**lead_data)
				if not lead.exists():
					logging.info('Import lead {}'.format(ix))
					db.session.add(lead)
				else:
					logging.info('This lead already exists')
					continue
			db.session.commit()
			logging.info('Import Done')
		except Exception as e:
			logging.info('Error while importing')
			db.session.rollback()
		flash('Donnees importees avec succes')
		# Remove imported file and clear cookies 
		os.remove(session['filepath'])
		session.pop('filepath', None)
		session.pop('uploaded', None)
		return redirect(url_for('main.home'))

	# CANCEL
	if request.method=='POST' and request.form['btn']=='Annuler':
		logging.info('Reseting cookies and deleting file')
		# Remove imported file and clear cookies 
		os.remove(session['filepath'])
		session.pop('filepath', None)
		session.pop('uploaded', None)
		return redirect(url_for('main.home'))

	return render_template('leads/upload.html', uploaded=session['uploaded'])



def get_displayed_leads(leads_ids, leads_type, cursor, limit):
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



def get_leads_ids(data):
	"""
	"""	
	max_exports = current_user.subscriptions.order_by(Subscription.subscription_date.desc()).first().plan.limit_daily_query
	today_requests = [elt.id for elt in current_user.requested_leads.all() if elt.query_date.date()==datetime.utcnow().date()]
	remaining_exports = min(max_exports, max_exports-len(today_requests))
	# Set a random seed to assure the same results if request is launched again
	random.seed(int(datetime.utcnow().strftime('%Y%m%d'))*current_user.id)	
	results_len = list(np.random.randint(low=4, high=14, size=1))[0]*10 # number of results to be displayed (random nb of page) * (number of results per page)
	# results_len = 3

	# Neet to create a list from activity_field input as it will be passed in a "in_" filter which only supports list
	activity_filter = [data.get('company_activity_field')] if data.get('company_activity_field') else get_list_companies_activities()
	print("activity: {}".format(activity_filter))

	# User requested company leads
	if data.get('leads_type') == 'company':
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
	requested_leads_id = [elt.id for elt in leads_query.all() ] 
	random_leads_id = random.sample(requested_leads_id, min(len(requested_leads_id), results_len))
	# print('random_ids: {}'.format(random_leads_id))
	return (random_leads_id, data.get('leads_type'))




# To be placed within utils
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'csv'




# To be placed within utils
def clean_leads_input(leads_df):
	'''
		This function aims at cleaning the company_postal_code and company_phone columns as well as removing nan.
		company_postal_code: 
			pandas usually read it as integer, hence we return the first 5 digits as a string.
			return series of type str

		company_phone:
			first remove '.' and '-' from the phone number and make sure every number starts with a 0.
			return series of type str wiht phone number in a format 0XXXXXXXXX
	'''
	df = leads_df
	df['company_postal_code'] = df.company_postal_code.apply(lambda x: str(x)[:5]) 
	df['company_phone'] = df.company_phone.str.replace('\.', '').str.replace('-', '').\
	apply(lambda x: '0' + str(x) if not (x is np.nan or str(x).startswith('0')) else x)
	df = df.replace(np.nan, '')
	return df

import os
import pandas as pd
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, session, make_response
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.auth.views import admin_login_required
from . import leads
from .forms import LeadsQueryForm
from .. import app, db
from ..models import User, Subscription, Lead, LeadRequest
# from ...bin import all_utils

def from_sql(row):
	"""Translates a SQLAlchemy model instance into a dictionary"""
	if not row:
		return []
	else:	
	    data = row.__dict__.copy()
	    data['id'] = row.id
	    data.pop('_sa_instance_state')
	    return data



@leads.route('/generator', methods=['POST', 'GET'])
@login_required
def query():
	form = LeadsQueryForm()	
	cu = current_user

	# Get the latest subscription
	user_subscription = cu.subscriptions.order_by(Subscription.subscription_date.desc()).first()

	if not user_subscription or not user_subscription.is_valid:
		flash('Vous devez souscrire a un abonnement pour beneficier de ce service')
		return redirect(url_for('landing.pricing'))

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
			query_output_all = Lead.query.filter(Lead.company_activity_field==request_filters[0], Lead.company_postal_code.like(request_filters[1]+'%'), ~Lead.id.in_(excluding_leads)).all()
			
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
	return render_template('leads/generator.html', form=form, request_output=session['todays_output'])



@leads.route('/telechargement')
@login_required
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

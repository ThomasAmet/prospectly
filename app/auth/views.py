from functools import wraps 
from datetime import datetime
from time import time

from flask import render_template, redirect, url_for, request, flash, abort, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from flask_talisman import ALLOW_FROM
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from app import db, app
from . import auth
from .forms import LoginForm, RegistrationForm, SetPasswordForm
from ..models import User

import stripe
import jwt
import json


import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


stripe.api_key = app.config.get('STRIPE_SECRET_KEY')

def admin_login_required(func):
	@wraps(func)
	def decorated_view(*args, **kwargs):
		if not current_user.is_admin():
			return abort(403)
		return func(*args, **kwargs)
	return decorated_view


@auth.route('/stripe-public-key', methods=['GET'])
def get_publishable_key():
    return jsonify({'publicKey': app.config.get('STRIPE_PUBLISHABLE_KEY')})



@auth.route('/inscription', methods=['GET', 'POST']) 
def signup():
	
	# plan = 'plan_GggQmCKZATWq0c'
	form = RegistrationForm()

	# if request.method == 'POST':
	if form.validate_on_submit():
		try:
			# User creation for admin doesnt require stripe payment
			if current_user.is_authenticated:
				if current_user.is_admin():
					user = User(first_name=form.first_name.data.capitalize(), last_name=form.last_name.data.capitalize(),
						email=form.email.data.lower(), stripe_customer_id=None)	
					user.set_username
					db.session.add(user)
					db.session.commit()
					data = {
						'user_id': user.id,
						'exp': time() + 600
					}
					token = jwt.encode(data, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

					send_email(receiver_email=user.email,
							   html_text=render_template('email/welcome-validation.html', user=user, token=token))

					flash('Utilisateur crée.')
					return Response('Success! Compte cree', 200)				
				else:
					return redirect(url_for('landing.home'))
			else:
				plan_id = get_plan_id(request.form.get('plan_name'))
				print(plan_id)
				customer = stripe.Customer.create(
					name = request.form['first_name'] + ' ' + request.form['last_name'],
					email=request.form['email']
				)
				print(customer)

				user = User(first_name=form.first_name.data.capitalize(), last_name=form.last_name.data.capitalize(),
					email=form.email.data.lower(), stripe_customer_id=customer.id)
				user.set_username()
				db.session.add(user)
				db.session.commit()

				print('User creation suceeded!')

				stripe_session = stripe.checkout.Session.create(
					customer = customer.id,
					# customer_email = customer.email,
					payment_method_types=['card'],
					subscription_data={
						'items': [{
							'plan': plan_id,
						}],
					}, # I think u r right.
					success_url='%sauth/connexion?session_id={CHECKOUT_SESSION_ID}' % request.host_url,
					cancel_url='%sauth/paiement-echec' %request.host_url,
					locale='fr'
				)

				return Response(stripe_session.id, status=200)
		except:
			print('User creation failed!')
			db.session.rollback()
			return Response('Fail', status=404)
	else:		

		if not current_user.is_authenticated:
			if not request.args.get('plan_name'):
				return redirect(url_for('landing.pricing'))
		else:
			if not current_user.is_admin:
				return redirect(url_for('app.home'))
		return render_template('register.html', form=form, plan_name=request.args.get('plan_name'))



@auth.route('/paiement-reussi', methods=['POST'])
def on_succeeded_payment():

	webhook_secret = app.config.get('STRIPE_WEBHOOK_SECRET')

	if webhook_secret:
		signature = request.headers.get('stripe-signature')
		try:
			event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
			data = event['data']
			event_type = event['type']
		except Exception as e:
			return e
		# Get the type of webhook event sent - used to check the status of PaymentIntents.
	else:
		request_data = json.loads(request.data)
		data = request_data['data']
		event_type = request_data['type']

	data_object = data['object']

	if event_type == 'checkout.session.completed':
		print(data_object['customer'])
		stripe_customer = stripe.Customer.retrieve(data_object['customer'])
		user = User.query.filter_by(stripe_customer_id=data_object['customer']).first_or_404()
		print(user.email)
		data = {
			# 'timestamp': datetime.now().timestamp(),
			'user_id': user.id,
			'exp': time() + 600
		}
		token = jwt.encode(data, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
		send_email(receiver_email=user.email,
				   html_text=render_template('email/welcome-validation.html', user=user, token=token))
		return Response('Success', 200)

	print('Other web hook')
	return jsonify({'status': 'success'})




@auth.route('/confirmation-compte', methods=['GET', 'POST'])
def confirm_account():
	if current_user.is_authenticated:
		redirect( url_for('landing.home'))

	token = request.args.get('token')
	# created_time = datetime.fromtimestamp(token_data['timestamp'])
	form = SetPasswordForm()
	if form.validate_on_submit():
		try:
			token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
			user = User.query.filter_by(id=token_data['user_id']).first_or_404()
			print(user)
			user.set_password(form.password.data)
			db.session.commit()
			flash('Votre mot de passe est enregistré')
			return redirect(url_for('auth.login', email=user.email))
		except:
			db.session.rollback()
			return redirect( url_for('landing.home'))
	return render_template('confirm-account.html', form=form)



@auth.route('/paiement-echec')
def on_fail_payment():
	return render_template('payment_failed.html')



@auth.route('/connexion', methods=['GET', 'POST'])
def login():
	# if current_user.is_authenticated:
	# 	redirect( url_for('landing.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, request.form.get('remember-me'))
			next = request.args.get('next')
			if next is None or not next.startswith('/'):
				next = url_for('crm.home')
			return redirect(next)
		else:
			flash('Email ou mot de passe invalide.')
	return render_template('login.html', form=form)



@auth.route('/deconnexion')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('landing.home'))



@auth.route('/profile')
@login_required
def profile():
	return render_template('profile.html')



class AdminMyIndexView(AdminIndexView):
	""" 
		Create a CustomAdminIndeView based on AdminIndexView in order to be accessible only by user who are admin 
	"""
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_admin()


class  AdminModelView(ModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_admin()

# class AdminHomeView(BaseView):
# 	@expose('/')
# 	def index(self):
# 		return self.render(url_for('landing.home'))



def send_email(receiver_email, html_text):
	print(receiver_email)
	print(html_text)

	subject = "Prospectly - Valider votre inscription"
	#
	# username_email = 'prospectly.test@gmail.com'
    # sender_email = 'prospectly.test@gmail.com'
	username_email = 'thomas@prospectly.fr'
	sender_email = 'hello@prospectly.fr'

	password = app.config.get('MAIL_PASSWORD')
	print(password)
	# password = 'Freelance2020#'
    # Create a multipart message and set headers
	message = MIMEMultipart('alternative')
	message["From"] = "Support - Prospectly <{}>".format(sender_email)
	message["To"] = receiver_email
	message["Subject"] = subject
	# message["Bcc"] = receiver_email  # Recommended for mass emails

	part2 = MIMEText(html_text, 'html')
	message.attach(part2)

	# Add body to email
	text = message.as_string()

	# Log in to server using secure context and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
		server.login(username_email, password)
		server.sendmail(sender_email, receiver_email, text)


# 	return plans[plan_name]
def get_plan_id(plan_name):
	plans = {
		'monthly_basic':app.config.get('PLAN_MONTHLY_BASIC'),
		'yearly_basic':app.config.get('PLAN_YEARLY_BASIC')
	}
	return plans[plan_name]
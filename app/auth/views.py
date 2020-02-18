from functools import wraps 
from datetime import datetime

from flask import render_template, redirect, url_for, request, flash, abort, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from flask_talisman import ALLOW_FROM
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from app import db, app
from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User

import stripe
import jwt
import json


import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


stripe.api_key = 'sk_test_jezU1v6w8mAaxIQMvWOs2JxD00Ps2BSFcQ'

def admin_login_required(func):
	@wraps(func)
	def decorated_view(*args, **kwargs):
		if not current_user.is_admin():
			return abort(403)
		return func(*args, **kwargs)
	return decorated_view


@app.route('/stripe-public-key', methods=['GET'])
def get_publishable_key():
	return jsonify({'publicKey': app.config.get('STRIPE_PUBLISHABLE_KEY')})


@auth.route('/inscription', methods=['GET', 'POST']) 
@login_required
@admin_login_required
def signup():

	# if current_user.is_authenticated:
		# return redirect(url_for('landing.home'))

	# plan = 'plan_GggQmCKZATWq0c'
	form = RegistrationForm()

	if request.method == 'POST':
		try:
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

			stripe_session = stripe.checkout.Session.create(
				customer = customer.id,
				customer_email = customer.email,
				payment_method_types=['card'],
				subscription_data={
					'items': [{
						'plan': plan_id,
					}],
				},
				success_url='%sauth/paiement-reussi?session_id={CHECKOUT_SESSION_ID}' %request.host_url,
				cancel_url='%sauth/paiement-echec' %request.host_url,
				locale='fr'
			)

			return Response('Success', status=200)
		except:
			db.session.rollback()
			return Response('Fail', status=404)

	# return render_template('register.html', form=form)
		# if 'register' in request.form:
		# if form.validate_on_submit():
	# 	user = User.query.filter_by(email=request.form['email']).first()
	# 	if user:
	# 		user.first_name = form.first_name.data.capitalize()
	# 		user.last_name = form.last_name.data.capitalize()
	# 		user.stripe_session_id = request.form['session_id']
	# 	else:
	# 		user = User(first_name=form.first_name.data.capitalize(), last_name=form.last_name.data.capitalize(), 
	# 	email=form.email.data.lower(), stripe_customer_id=request.form['session_id'])
	# 		# Check if username exists within form validates
	# 		db.session.add(user)
	# 	try:
	# 		db.session.commit()
	# 	except:
	# 		db.session.rollback()
	# 	print(user)
	# 	return Response('Success', status=200) 
	# 	# else:
	# 	# 	return redirect(url_for('landing.home'))
	else:		
		return render_template('register.html', form=form, plan_name=request.args.get('plan_name'))


# @auth.route("/nouvelle-inscription", methods=['POST'])
# def create_customer_and_session():
# 	print(request.form)
# 	plan_id = get_plan(request.form.get('plan_name'))
# 	# This creates a new Customer and attaches the PaymentMethod in one API call.
# 	try:
# 		customer = stripe.Customer.create(
# 			name = request.form['first_name'] + ' ' + request.form['last_name'],
# 			email=request.form['email']
# 		)
# 		print(customer)
# 		# At this point, associate the ID of the Customer object with your
# 		# own internal representation of a customer, if you have one.
# 		user = User(first_name=request.form['first_name'].capitalize(), last_name=request.form['last_name'].capitalize(),
# 					email=request.form['email'].data.lower(), stripe_customer_id=customer.id)
# 		# print(user)
# 		db.session.add(user)
# 		db.session.commit()
# 		# Subscribe the user to the subscription created
# 		stripe_session = stripe.checkout.Session.create(
# 			customer = customer.id,
# 			customer_email = customer.email,
# 			payment_method_types=['card'],
# 			subscription_data={
# 				'items': [{
# 					'plan': plan_id,
# 				}],
# 			},
# 			success_url='%sauth/paiement-reussi?session_id={CHECKOUT_SESSION_ID}' %request.host_url,
# 			cancel_url='%sauth/paiement-echec' %request.host_url,
# 			locale='fr'
# 		)
# 		print(stripe_session)
# 		return jsonify({'checkoutSessionId': stripe_session['id']})
# 	except Exception as e:
# 		db.session.rollback()
# 		return jsonify(error=str(e)), 403


@auth.route('/paiement-reussi', methods=['GET'])
def on_succeeded_payment():
	session_id = request.args.get('session_id')
	print(session_id)
	user = User.query.filter_by(stripe_session_id=session_id).first()
	print(user.email)
	data = {
		'timestamp': datetime.now().timestamp(),
		'user_id': user.id,
	}
	token = jwt.encode(data, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	send_email(receiver_email=user.email,
			   html_text='<a href="' + request.host_url + 'set-password?token=' + token + '">Cliquer ici</a> pour definir votre mot de passe.')

	return render_template('payment_succeeded.html')


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



@auth.route('/test')
@login_required
def test():
	form = RegistrationForm()
	return render_template('register.html', form=form)

class AdminMyIndexView(AdminIndexView):
	""" 
		Create a CustomAdminIndeView based on AdminIndexView in order to be accessible only by user who are admin 
	"""
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_admin()



class AdminHomeView(BaseView):
	@expose('/')
	def index(self):
		return self.render(url_for('landing.home'))



def send_email(receiver_email, html_text):
    print(receiver_email)
    print(html_text)

    subject = "Prospectly - Valider votre inscription"
    # sender_email = app.config.get('MAIL_USERNAME')
    sender_email = 'prospectly.test@gmail.com'
    
    
    # password = app.config.get('MAIL_PASSWORD')
    password = 'Freelance2020#'
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


def get_plan_id(plan_name):
	plans = {
		'monthly_basic':'plan_GgreHAs62bMtM8',
		'yearly_basic':'plan_GgrfmtKZAV6j1l'
	}

	return plans[plan_name]
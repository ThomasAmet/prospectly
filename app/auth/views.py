from functools import wraps 
from datetime import datetime, timedelta
from time import time
from threading import Thread 

from flask import render_template, redirect, url_for, request, flash, abort, jsonify, Response, session, Markup
from flask_login import login_user, logout_user, login_required, current_user
from flask_talisman import ALLOW_FROM
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from app import db, app
from . import auth
from .forms import LoginForm, RegistrationForm, SetPasswordForm, RequestNewPasswordForm, EmailSupportForm
from ..models import User, Subscription, Plan

import stripe
import jwt
import json
import math


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


def pro_plan_required(func):
	@wraps(func)
	def decorated_view(*args, **kwargs):
		latest_sub = db.session.query(Subscription).filter(Subscription.user_id==current_user.id).order_by(Subscription.subscription_date.desc()).first()
		if not latest_sub.plan.lead_generator:
			link = url_for('auth.profile')
			message = Markup("Pour accéder au générateur de prospects, vous devez souscrire à un abonnement <a href={}>Prospectly<sup><strong> +</strong></sup></a>.".format(link))
			flash(message)
			return redirect(url_for('crm.home'))
		return func(*args, **kwargs)
	return decorated_view


def valid_subscription_required(func):
	@wraps(func)
	def decorated_view(*args, **kwargs):
		latest_sub = db.session.query(Subscription).filter(Subscription.user_id==current_user.id).first()
		if datetime.utcnow() > latest_sub.next_payment + timedelta(days=2):
			message = Markup("Votre paiement n'est pas à jour, nous vous invitons à mettre à jour vos informations de paiement ou à contacter le support.")
			flash(message)
			return redirect(url_for('auth.profile'))
		return func(*args, **kwargs)
	return decorated_view



@auth.route('/profil', methods=['GET', 'POST'])
@login_required
def profile():
	latest_sub_query = Subscription.query.filter_by(user_id=current_user.id).order_by(Subscription.subscription_date.desc())
	latest_sub = latest_sub_query.first()

	monthly_cost = 0
	yearly_cost = 0

	if request.method=='POST':
		data = request.form.to_dict(flat=True)
		print('form data: {}'.format(data))

		user = User.query.get(current_user.id)
		for k,v in data.items():
			print('{}:{}'.format(k,v))
			setattr(user, k, v)

		# try:
		db.session.commit()
		flash('Vos informations ont été mises à jour.')
		# except:
			# flash('Une erreur est survenue.')
		return redirect(url_for('auth.profile'))


	# Compute the proration amount should a user switch to a Pro plan
	if current_user.stripe_customer_id and latest_sub.plan.category=='Basic':
		# Set proration date to this moment:
		proration_date = int(time())
		# try:
		stripe_subscription = stripe.Subscription.retrieve(latest_sub.stripe_id)

		# See what the next invoice would look like with a monthly plan switch:
		monthly_items=[{
		  'id': stripe_subscription['items']['data'][0].id,
		  'plan': app.config.get('PLAN_MONTHLY_PRO'), # Switch to new plan
		}]
		monthly_invoice = stripe.Invoice.upcoming(
		  customer=current_user.stripe_customer_id,
		  subscription=latest_sub.stripe_id,
		  subscription_items=monthly_items,
		  subscription_proration_date=proration_date,
		  subscription_trial_end=proration_date, # when necessary, simulate the trial ending #https://stripe.com/docs/api/invoices/upcoming#upcoming_invoice-subscription_trial_end
		)
		print("monthly_invoice request id: {}".format(monthly_invoice.last_response.request_id))

		# Calculate the proration cost:
		current_prorations = [ii for ii in monthly_invoice.lines.data if ii.period.start - proration_date <= 1]
		monthly_cost = math.floor(sum([p.amount for p in current_prorations])/100)

		# See what the next invoice would look like with a monthly plan switch:
		yearly_items=[{
		  'id': stripe_subscription['items']['data'][0].id,
		  'plan': app.config.get('PLAN_YEARLY_PRO'), # Switch to new plan
		}]
		yearly_invoice = stripe.Invoice.upcoming(
		  customer=current_user.stripe_customer_id,
		  subscription=latest_sub.stripe_id,
		  subscription_items=yearly_items,
		  subscription_proration_date=proration_date,
		  subscription_trial_end=proration_date, # when necessary, simulate the trial ending #https://stripe.com/docs/api/invoices/upcoming#upcoming_invoice-subscription_trial_end
		)
		# print("yearly_invoice request id: {}".format(yearly_invoice.last_response.request_id)) #get stripe request id for stripe support
		# Calculate the proration cost:
		current_prorations = [ii for ii in yearly_invoice.lines.data if ii.period.start - proration_date <= 1]
		yearly_cost = math.floor(sum([p.amount for p in current_prorations])/100)
 
	return render_template('profile.html', latest_sub=latest_sub, monthly_cost=monthly_cost, yearly_cost=yearly_cost)



@auth.route('/stripe-public-key', methods=['GET'])
def get_publishable_key():
    return jsonify({'publicKey': app.config.get('STRIPE_PUBLISHABLE_KEY')})



@auth.route('/inscription', methods=['GET', 'POST']) 
def signup():
	if current_user.is_authenticated:
			if not current_user.is_admin:
				return redirect(url_for('app.home'))

	form = RegistrationForm()

	# POST method part
# try:
	if request.method=='POST':
		
		print(dict(request.form))
		requested_email = request.form.get('email').lower().strip()
		
		plan = Plan.query.filter_by(stripe_id=request.form.get('plan_stripe_id')).first() #
		# user = User.query.filter_by(email=request.form.get('email')).first()
		user = User.query.filter_by(email=requested_email).first()
		print('Plan: {}'.format(plan.__dict__.copy()))
		# Case to handle custome who enter email but didn't pay
		if user:
			print('Exisiting user!')
			print(user.__dict__.copy())
			# If a subscription is associated with a user, it means customer paid so we redirect to login
			if Subscription.query.filter_by(user_id=user.id).first():
				print('User with subscription')
				# print(Subscription.query.filter_by(user_id=user.id).first().__dict__.copy())
			# # If user password exists, it means customer paid so we redirect to login
			# if user.last_token:
				flash('Oups... Cet email est utilisé. Connectez-vous ou choisissez un autre email.')
				return Response(url_for('auth.signup', plan_stripe_id=request.form.get('plan_stripe_id')), status=404) # use 404 to throw an error in ajax call and not redirect to stripe session
			# Else retrieve user and update infos in both database and stripe
			else:
				print('Updating user infos')
				user.first_name = request.form.get('first_name').capitalize()
				user.last_name = request.form.get('last_name').capitalize()
				user.set_username()
				customer = stripe.Customer.retrieve(user.stripe_customer_id)
				customer.name = request.form.get('first_name').capitalize() + ' ' + request.form.get('last_name').capitalize()		
		# If User is none, create a new one		
		else:
			print('New user!')
			customer = stripe.Customer.create(
				name = request.form.get('first_name').capitalize() + ' ' + request.form.get('last_name').capitalize(),
				email=request.form.get('email').lower()
			)
			user = User(first_name=form.first_name.data.capitalize(),
						last_name=form.last_name.data.capitalize(),
						email=requested_email, stripe_customer_id=customer.id)
			db.session.add(user)

		db.session.commit()
		print('Customer succesfully created!')
		stripe_session = stripe.checkout.Session.create(
			customer = customer.id,
			# customer_email = customer.email,
			payment_method_types=['card'],
			subscription_data={
				'items': [{
					'plan':plan.stripe_id,
				}],
				# 'trial_period_days':int(plan.free_trial), #use a variable that will depend on plan_id and will be return by from_plan_name()
				'trial_from_plan':True, # tell the subscription to pull the trial from the plan! https://stripe.com/docs/api/subscriptions/create#create_subscription-trial_from_plan	
			}, 
			success_url='%sauth/paiement-reussi?session_id={CHECKOUT_SESSION_ID}&msg=Vous+allez+recevoir+un+email+contenant+un+lien+pour+activer+votre+compte' % request.host_url,
			cancel_url='%sauth/paiement-echec' %request.host_url,
			locale='fr'
		)
		# session['stripe_session_id'] = stripe_session.id #load stripe session in cookie to allow only one time success message
		return Response(stripe_session.id, status=200)
# except:
# 	flash('Une erreur est survenue. Merci de contacter le support.')
# 	print('User creation failed!')
# 	db.session.rollback()
# 	return Response(url_for('main.home'), status=404)
		
	# GET method part (needs to be below POST method to make stripe work)
	if request.method == 'GET' :
		if not request.args.get('plan_stripe_id'):
			return redirect(url_for('main.pricing'))
	message = Markup("<strong>Pour votre sécurité</strong>, vous serez invité à renseigner vos informations de paiement après cette page.<br>Cette étape permet de vérfier votre identité. <strong>Aucun prélévement ne sera effectué.</strong>")
	flash(message)
	return render_template('register.html', form=form, plan_stripe_id=request.args.get('plan_stripe_id'))



@auth.route('/webhooks', methods=['POST'])
def webhooks():

	webhook_secret = app.config.get('STRIPE_WEBHOOK_SECRET')

	# Make sure the request is from stripe or accept request that are not from Stripe only in Development Mode
	if webhook_secret:
		signature = request.headers.get('stripe-signature')
		event = stripe.Webhook.construct_event(
            payload=request.data, sig_header=signature, secret=webhook_secret)
		data = event['data']
		event_type = event['type']
	else:
		# Handle webhooks in dev mode using stripe CLI
		if app.config['DEBUG']:
			request_data = json.loads(request.data)
			data = request_data['data']
			event_type = request_data['type']


	# Create a subscription and automatically set the next_payment_date based on the type of plan
	if event_type=='customer.subscription.created':
		print('Subscription Created Webhook')
		# stripe object with multiple informations		
		data_object = data['object']
		print('Data object:{}'.format(data_object)) 
		
		# Retrieve user in database from stripe_user_id
		user = User.query.filter_by(stripe_customer_id=data_object['customer']).first_or_404()
		# Get subscription id from stripe webhook data
		stripe_sub_id = data_object['items']['data'][0]['subscription']
		# Retrieve plan_id in our database from the stripe_plan_id
		plan = Plan.query.filter_by(stripe_id=data_object['items']['data'][0]['plan']['id']).first()
		# Creata a subscription associated with the user
		if user:
			sub = Subscription(user_id=user.id, plan_id=plan.id, stripe_id=stripe_sub_id)
			db.session.add(sub)
			db.session.commit()
			return Response('Success', 200)
		else:
			return Response('No user found from stripe_customer_id', 400)


	# Update 'next_payment' in subscription when the payment succeeded
	if event_type=='invoice.payment_succeeded':
		print('Invoice Payment Succeeded Webhook')
		# stripe object with multiple informations		
		data_object = data['object']
		print('Data object:{}'.format(data_object))
		
		# Retrieve user in database from stripe_user_id
		user = User.query.filter_by(stripe_customer_id=data_object['customer']).first_or_404()
		# Get stripe_subscription_id from stripe webhook data
		stripe_sub_id = data_object['lines']['data'][0]['subscription']
		# Retrieve the lateste active subscription in our databased filtered by user_id and subsription_stripe_id
		latest_sub = Subscription.query.filter_by(user_id=user.id, stripe_id=stripe_sub_id).order_by(Subscription.subscription_date.desc()).first()
		# If there is an exisiting subscription update the next_payment_date
		if latest_sub:
			latest_sub.set_next_payment()
			return Response('Success', 200)
		else:
			print('No subscription found for customer with id:{}'.format(user.id))
			return Response('Error', 400)


	# Send the password validation email when the Checkout session is completed			
	if event_type == 'checkout.session.completed':
		print('Checkout Session Completed Webhook')
		# stripe object with multiple informations		
		data_object = data['object']
		print('Data object:{}'.format(data_object)) 
		# Retrieve stripe_user_id from the Stripe webhook
		stripe_customer = stripe.Customer.retrieve(data_object['customer'])
		# Retrieve user in database from stripe_user_id
		user = User.query.filter_by(stripe_customer_id=data_object['customer']).first_or_404()
		# Retrieve Stripes' subscription_id 
		stripe_sub_id = stripe_customer.subscriptions.data[0].id
		print('Webhook Stripe Subscription id: {}'.format(stripe_sub_id))


		# Prepare the data to be send by email
		data = {
			'user_id': user.id,
			'exp': time() + 86400			
		}
		token = jwt.encode(data, app.config.get('SECRET_KEY'), algorithm='HS256')
		receiver_email = user.email
		subject = "Prospectly - Valider votre inscription"
		html_text=render_template('email/welcome-validation.html', user=user, token=token)
		Thread(target=send_async_email, args=(receiver_email, subject, html_text)).start()
		user.last_token = stripe_customer.id		
		
		return Response('Success', 200)

	print('Other web hook')
	return jsonify({'status': 'success'})



@auth.route('/validation-compte', methods=['GET', 'POST'])
def confirm_account():
	form = SetPasswordForm()

	if current_user.is_authenticated:
		if current_user.is_admin:
			render_template('password-set.html', form=form)
		else:
			redirect( url_for('main.home'))

	token = request.args.get('token')
	# print(token)
	
	if form.validate_on_submit():
		try:
			token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
			user = User.query.filter_by(id=token_data['user_id']).first_or_404()
			if token == user.last_token:
				flash('Ce lien a déjà été utilisé pour définir un mot de passe.')
				return redirect(url_for('auth.login', email=user.email))
			user.set_password(form.password.data)
			user.last_token = token
			db.session.commit()
			flash('Votre mot de passe est enregistré.')
			return redirect(url_for('auth.login', email=user.email))
		except:
			db.session.rollback()
			flash('Une erreur est survenue. Merci de contacter le support.')
			return redirect( url_for('main.home'))
	return render_template('password-set.html', form=form)



@auth.route('/oubli-mot-de-passe', methods=['GET','POST'])
def request_new_password():
	if current_user.is_authenticated:
		return redirect(url_for('crm.home'))

	form = RequestNewPasswordForm()
	if form.validate_on_submit():
		# user = User.query.filter_by(email=form.email.data).first_or_404()
		requested_email = request.form.get('email').lower().strip()
		user = User.query.filter_by(email=requested_email).first_or_404()
		if user is None:
			flash("Un email de réinitialisation vient d'être envoyé à l'addresse indiquée.")
			return redirect(url_for('auth.login'))
		data = {'user_id':user.id,
				'exp':time() + 600}
		token = jwt.encode(data, user.password_hash, algorithm='HS256') if user.password_hash else None# use of password hash as secret key to encode to ensure single use password
		receiver_email = user.email
		subject = "Prospectly - Réinitialiser votre mot de passe"
		html_text=render_template('email/reset-password.html', user=user, token=token)
		Thread(target=send_async_email, args=(receiver_email, subject, html_text)).start()
		
		flash("Un email de réinitialisation vient d'être envoyé à l'adresse indiquée.")
		return redirect(url_for('auth.login'))
	return render_template('new-password-request.html', form=form)



@auth.route('/reinitialisation-mot-de-passe', methods=['GET','POST'])
def reset_password():
	form = SetPasswordForm()

	if current_user.is_authenticated:
		if current_user.is_admin:
			render_template('password-set.html', form=form)
		else:
			flash("Déconnectez-vous avant de changer votre mot de passe.")
			redirect( url_for('main.home'))

	token = request.args.get('token')
	# print(token)
	
	if form.validate_on_submit():
		try:
			secret = User.query.get(jwt.decode(token, verify=False)['user_id']).password_hash
			token_data = jwt.decode(token, secret, algorithms=['HS256'])
			user = User.query.filter_by(id=token_data['user_id']).first_or_404()
			user.set_password(form.password.data)
			db.session.commit()
			flash('Votre mot de passe a bien été changé.')
			return redirect(url_for('auth.login', email=user.email))
		except:
			db.session.rollback()
			flash("Ce lien n'est plus valide. Si l'erreur persiste, merci de contacter le support.")
			return redirect( url_for('main.home'))
	return render_template('password-set.html', form=form)


# Routes for stripe checkout session
@auth.route('/paiement-echec')
def on_fail_payment():
	return render_template('payment-failed.html')


# Routes for stripe checkout session
@auth.route('/paiement-reussi')
def on_success_payment():
	return render_template('payment-succeeded.html')



@auth.route('/connexion', methods=['GET', 'POST'])
def login():

	if current_user.is_authenticated:
		redirect( url_for('main.home'))

	form = LoginForm()
	
	if form.validate_on_submit():
		requested_email = request.form.get('email').lower().strip()
		user = User.query.filter_by(email=requested_email).first()
		# user = User.query.filter_by(email=form.email.data.lower()).first()
		password_hash = user.password_hash if user else None
		if password_hash is not None and user.verify_password(form.password.data):
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
	flash('Vous êtes maintenant déconnecté.')
	return redirect(url_for('main.home'))



@auth.route('/edition-abonnement', methods=['POST','GET'])
@admin_login_required
def edit_subscription():

	if request.method == 'POST':
		data = request.form.to_dict(flat=True)
		print('Requested form data: {}'.format(data))
		
		# Retrieve user first
		user = User.query.filter_by(email=data.get('email'))
		if not user:
			flash('No user found with this email')
			return redirect(url_for('auth.edit_subscription'))
		if data.get('action')=='cancel_trial':
			try:
				latest_sub = db.session.query(Subscription).filter(Subscription.user_id==current_user.id).order_by(Subscription.subscription_date.desc()).first()
				stripe_sub = stripe.Subscription.modify(latest_sub.stripe_id,
					trial_end='now',
				)
				flash('Trial period for {} has been stoped'.format(user))
			except e:
				flash('Error: {}'.format(e))
			return redirect(url_for('auth.edit_subscription'))

	if request.method == 'GET':
		None
	users_list = User.query.all()
	return render_template('subscription-edition.html', users_list=users_list)



@auth.route('/account-upgrade')
@login_required
def upgrade_account():
	# Retrieve the latest active subscription
	latest_sub_query = db.session.query(Subscription).filter(Subscription.user_id==current_user.id).order_by(Subscription.subscription_date.desc())
	latest_sub = latest_sub_query.first()
	
	if not latest_sub.stripe_id or latest_sub.plan.category in ['Pro','Beta']:
		return redirect(url_for('auth.profile'))

	stripe_subscription = stripe.Subscription.retrieve(latest_sub.stripe_id)

	if request.args.get('type') == 'monthly':
		# Change the subscription in stripe
		new_subscription = stripe.Subscription.modify(
		  stripe_subscription.id,
		  cancel_at_period_end=False,
		  items=[{
		    'id': stripe_subscription['items']['data'][0].id,
		    'plan': app.config.get('PLAN_MONTHLY_PRO'),
		  }],
		  proration_behavior='always_invoice',#ensure that the proration is computed and invoiced straight away
		  trial_end='now',
		)
		# Retrieve the plan assoicated in database
		new_plan = Plan.query.filter_by(stripe_id=app.config.get('PLAN_MONTHLY_PRO')).first()
	else:
		new_subscription = stripe.Subscription.modify(
		  stripe_subscription.id,
		  cancel_at_period_end=False,
		  items=[{
		    'id': stripe_subscription['items']['data'][0].id,
		    'plan': app.config.get('PLAN_YEARLY_PRO'),
		  }],
		  proration_behavior='always_invoice',
		  trial_end='now',
		)
		# Retrieve the plan assoicated in database
		new_plan = Plan.query.filter_by(stripe_id=app.config.get('PLAN_YEARLY_PRO')).first()

	# Create a new subscription in database
	new_sub = Subscription(stripe_id=new_subscription.id, user_id=current_user.id, plan_id=new_plan.id)
	db.session.add(new_sub)
	try:
		db.session.commit()
		message = Markup('Félicitations! Vous faites désormais parti des membres Prospeclty<sup><strong> +</strong></sup>. Votre nouvel abonnement est disponible dès maintenant.')
		
	except:
		message="Une erreur est survenue. Merci de contacter le support. Pensez à détailler l'opération que vous souhaitez effectuer"
	flash(message)
	return redirect(url_for('auth.profile'))



@auth.route('/account-downgrade')
@login_required
def downgrade_plan():

	# Downgrade from a Pro plan to a Basic plan without proration

	# Retrieve the latest_active subscription
	latest_sub_query = db.session.query(Subscription).filter(Subscription.user_id==current_user.id).order_by(Subscription.subscription_date.desc())
	latest_sub = latest_sub_query.first()

	if not latest_sub.stripe_id or latest_sub.plan.category in ['Basic','Beta']:
		return redirect(url_for('auth.profile'))

	stripe_subscription = stripe.Subscription.retrieve(latest_sub.stripe_id)
	#  Set the current subscription to be canceled at the end of the period
	stripe.Subscription.modify(
		  stripe_subscription.id,
		  cancel_at_period_end=True
		)
	sub_end_date = datetime.fromtimestamp(stripe_subscription['current_period_end']).date()
	# Then set a new subscription with the new plan to start at the end of the period		
	if request.args.get('type')=='monthly':
		stripe_sub_schedule = stripe.SubscriptionSchedule.create(
								  customer=current_user.stripe_customer_id,
								  start_date=stripe_subscription['current_period_end'],
								  end_behavior='release',
								  phases=[
								    {
								      'plans': [
								        {'plan': app.config.get('PLAN_MONTHLY_BASIC'),
								         'quantity': 1},
								      ],
								      'iterations': 12,
								    },
								  ],
								)
	else:
		stripe_sub_schedule = stripe.SubscriptionSchedule.create(
						  customer=current_user.stripe_customer_id,
						  start_date=stripe_subscription['current_period_end'],
						  end_behavior='release',
						  phases=[
						    {
						      'plans': [
						        {'plan': app.config.get('PLAN_MONTHLY_BASIC'),
						         'quantity': 1},
						      ],
						      'iterations': 12,
						    },
						  ],
						)

	try:
		message = Markup("Nous sommes navrés d'apprendre que Prospeclty<sup><strong> +</strong></sup> ne correspond pas à vos attends.<br>Vous aurez  toutefois encore accès à toutes les fonctionnalités jusqu'au {}.".format(sub_end_date))
		flash(message)
	except:
		flash("Une erreur est survenue. Merci de contacter le support. Pensez à détailler l'opération que vous souhaitez effectuer.")
		db.session.rollback()
	
	return redirect(url_for('auth.profile'))



@auth.route('email-support', methods=['POST', 'GET'])
@login_required
@admin_login_required
def email_support():
	form = EmailSupportForm()

	if form.validate_on_submit():
		email = form.email.data
		user = User.query.filter_by(email=email).first_or_404()
		
		data = {
			'user_id': user.id,
			'exp': time() + 7200			
		}
		token = jwt.encode(data, app.config['SECRET_KEY'], algorithm='HS256')
		receiver_email = user.email
		subject = "Prospectly - Valider votre inscription"
		html_text = render_template('email/welcome-validation.html', user=user, token=token)
		Thread(target=send_async_email, args=(receiver_email, subject, html_text)).start()
		flash('Password validation email has been sent.')

	return render_template('email-support.html', form=form)


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
# 		return self.render(url_for('main.home'))



def send_async_email(receiver_email, subject, html_text):
	# print(receiver_email)
	# print(html_text)

	# username_email = 'prospectly.test@gmail.com'
    # sender_email = 'prospectly.test@gmail.com'
	username_email = 'thomas@prospectly.fr'
	sender_email = 'hello@prospectly.fr'

	password = app.config.get('MAIL_PASSWORD')
	# password = 'Freelance2020#'
    # Create a multipart message and set headers
	message = MIMEMultipart('alternative')
	message["From"] = "Support - Prospectly <{}>".format(sender_email) #customizing how the sender is displayed when receiving the email
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
def from_plan_name(plan_name):
	plans = {
		'monthly_basic':app.config.get('PLAN_MONTHLY_BASIC'),
		'yearly_basic':app.config.get('PLAN_YEARLY_BASIC'),
		'monthly_pro':app.config.get('PLAN_MONTHLY_PRO'),
		'yearly_pro':app.config.get('PLAN_YEARLY_PRO')
	}
	free_trial = {
		'monthly_basic':14,
		'yearly_basic':14,
		'monthly_pro':0,
		'yearly_pro':0
	}
	return (plans[plan_name], free_trial[plan_name])

def from_stripe_plan_id(stripe_plan_id):
	plans = {
		app.config.get('PLAN_MONTHLY_BASIC'):{'name':'monthly_basic'},
		app.config.get('PLAN_YEARLY_BASIC'):{'name':'yearly_basic'},
		app.config.get('PLAN_MONTHLY_PRO'):{'name':'monthly_pro'},
		app.config.get('PLAN_YEARLY_PRO'):{'name':'yearly_pro'},
	}
	plan_id = Plan.query.filter_by(name=plans[stripe_plan_id]['name']).first().id
	
	return plan_id


# token = jwt.encode({'user_id':1, 'exp':time()+600}, 'secret', algorithm='HS256')
# jwt.deconde(token)
# secret = User.query.get(jwt.decode(token, verify=False)['user_id']).password_hash


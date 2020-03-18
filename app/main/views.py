from datetime import datetime 
from flask import render_template, url_for, redirect, session, flash, request, jsonify, Response
from . import main
from app import app
from threading import Thread

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..models import User, Subscription, Plan

from app import auth, affiliation

import stripe
stripe.api_key = app.config.get('STRIPE_SECRET_KEY')


@main.route('/')
def index():
	if app.config['DEBUG'] or app.config['TESTING']:
		flash('This is a test')
		return render_template('main_base.html', title='Prospectly - Bienvenue')
	else:
		return redirect('https://app.prospectly.fr/accueil')


@main.route('/accueil')
def home():
	return render_template('home.html', title='Prospectly - Accueil')


@main.route('/offres')
def pricing():
	return render_template('pricing.html', title='Prospectly - Offre')

@main.route('/conditions-generales')
def terms_conditions():
	return render_template('terms-conditions.html', title='Prospectly - CGV')

@main.route('/contact', methods=['POST','GET'])
def contact():
	if request.method == 'POST':
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		email = request.form.get('email')
		message_content = request.form.get('message')

		receiver_email= 'contact@prospectly.fr'
		subject = "Question de la part de {} {}".format(first_name, last_name)
		html_text=render_template('email/question-request.html', 
								  first_name=first_name,
								  last_name=last_name,
								  email=email,
								  message_content=message_content)
		Thread(target=send_async_email, args=(receiver_email, subject, html_text)).start()
		flash('Votre message a bien été envoyé.')	

	return render_template('contact.html')


def send_async_email(receiver_email, subject, html_text):
	print(receiver_email)
	print(html_text)

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


# @main.route('/on_stripe_event', methods=['POST'])
# def on_stripe_event():
# 	webhook_secret = app.config.get('STRIPE_WEBHOOK_SECRET')

# 	if webhook_secret:
# 		signature = request.headers.get('stripe-signature')
# 		try:
# 			event = stripe.Webhook.construct_event(
# 				payload=request.data, sig_header=signature, secret=webhook_secret)
# 			data = event['data']
# 			event_type = event['type']
# 		except Exception as e:
# 			print(e)
# 			return Response('Stripe error', 500)
# 		# Get the type of webhook event sent - used to check the status of PaymentIntents.
# 	else:
# 		request_data = json.loads(request.data)
# 		data = request_data['data']
# 		event_type = request_data['type']

# 	data_object = data['object']

# 	if event_type == 'checkout.session.completed':
# 	# if event_type == 'customer.subscription.created':
# 		print('Data object:{}'.format(data_object))
# 		if data_object['mode'] == 'subscription':
# 			# Retrieve user from stripe customer id
# 			user = User.query.filter_by(stripe_customer_id=data_object['customer']).first_or_404()

# 			# Retrieve subscription data from subscription id
# 			stripe_subscription_id = data_object['subscription']
# 			stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
# 			if stripe_subscription:
# 				if stripe_subscription['metadata']['is_affiliation'] == 'False': # Subscription is created when registering
# 					auth.views.setup_stripe_payment(user, data_object)
# 				elif stripe_subscription['metadata']['is_affiliation'] == 'True':
# 					affiliation.views.add_affiliation(user, data_object, stripe_subscription)

# 				return Response('Success', 200)

# 	print('Other web hook')
# 	return jsonify({'status': 'success'})
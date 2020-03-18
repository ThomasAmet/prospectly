from functools import wraps 
from datetime import datetime
from time import time
from threading import Thread 

import stripe
import jwt
import json

from flask import render_template, redirect, url_for, request, flash, abort, jsonify, Response, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_talisman import ALLOW_FROM
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.exc import SQLAlchemyError
from ..models import User, Subscription, Plan, Affiliation
from sqlalchemy import and_

# from app.auth.views import send_async_email
from app import db, app

from . import affiliation


stripe.api_key = app.config.get('STRIPE_SECRET_KEY')


@affiliation.route('/affiliation')
@login_required
def render_affiliation():
	return render_template('affiliation.html')


@affiliation.route('/send-affiliation-email', methods=['POST']) 
@login_required
def send_affiliation_email():
	sender_email = current_user.email
	receiver_email = request.form['email']
	if sender_email == receiver_email:
		return Response('Sending email failed', 511)

	data = {
		'user_id': current_user.id,
		'subscriber_email': request.form['email']
	}
	token = jwt.encode(data, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
	receiver = User.query.filter_by(email=receiver_email).first()
	if receiver:
		# current_user.affiliates
		affiliation = Affiliation.query.filter_by(user_id=receiver.id, affiliate_id=current_user.id).first()
		if affiliation:
			return 'Duplicated Affiliation', 510
		else:
			subject = 'Invitation for affiliation'
			html_text = render_template('email/affiliation_email.html', token=token)
			print(html_text)
			# Thread(target=send_async_email, args=(receiver_email, current_user.email, subject, html_text)).start()
			return Response('Success', 200)
	else:
		return Response('Sending email failed', 511)


@affiliation.route('/setup-affiliation-payment', methods=['GET']) 
def setup_affiliation_payment():
	token = request.args.get('token')
	token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
	print(token_data)

	if current_user.is_authenticated:
		affiliation_json_str = json.dumps({
			'affiliated_by_user_id': token_data['user_id'],
			'subscriber_email': token_data['subscriber_email']
		})
		print(affiliation_json_str)

		return render_template('setup_affiliation_payment.html', data={
			'user_name': current_user.first_name + ' ' + current_user.last_name,
			'affiliation_json_str': affiliation_json_str
		})
	else:
		return redirect(url_for('auth.login', email=token_data['subscriber_email']))


@affiliation.route('/subscription-stripe', methods=['POST']) 
def setup_affiliation_payment_stripe():
	stripe_plan_id = 'plan_GtiMRf9eJq6f3e'
	
	affiliation_data = json.loads(request.form['affiliation_json_str'])
	affiliated_user = User.query.filter_by(email=affiliation_data['subscriber_email']).first()
	customer = stripe.Customer.retrieve(affiliated_user.stripe_customer_id)
	if affiliated_user:
		stripe_session = stripe.checkout.Session.create(
			customer = customer.id,
			# customer_email = customer.email,
			payment_method_types=['card'],
			subscription_data={
				'items': [{
					'plan': stripe_plan_id,
				}],
				'trial_period_days':14,
				'metadata': {
					'is_affiliation': True,
					'affiliate_id': affiliation_data['affiliated_by_user_id'],
				}
			}, 
			success_url='%saffiliation/affiliation-succeeded?session_id={CHECKOUT_SESSION_ID}&msg=Vous+allez+recevoir+un+email+contenant+un+lien+pour+activer+votre+compte' % request.host_url,
			cancel_url='%saffiliation/paiement-echec' %request.host_url,
			locale='fr'
		)
		return Response(stripe_session.id, status=200)
	else:
		return Response("User not found.", status=500)


@affiliation.route('/affiliation-succeeded') 
def affiliation_payment_succeeded():
	return render_template('affiliation_succeeded.html')


@affiliation.route('/paiement-echec') 
def affiliation_payment_failed():
	return render_template('payment-failed.html')


def add_affiliation(user, stripe_data, subscription_data):
	affiliation = Affiliation(user_id=user.id, affiliate_id=subscription_data['metadata']['affiliate_id'], subscription_id=stripe_data['subscription'])
	db.session.add(affiliation)
	db.session.commit()


def affiliation_invoice_succeeded(invoice):
	for line in invoice['lines']['data']:
		affiliation = Affiliation.query.filter_by(subscription_id=line['subscription']).first()
		if affiliation:
			transaction = Transaction(affiliation_id=affiliation.id, invoice_id=invoice['id'], amount=invoice['amount_paid'])
			db.session.add(transaction)
			db.session.commit()

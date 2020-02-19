from datetime import datetime 
from flask import render_template, url_for, redirect, session
from app.landing import landing
from app import app

@landing.route('/')
def index():
	if app.config['DEBUG'] or app.config['TESTING']:
		return render_template('layout/landing_base.html', title='ProspectLy - Bienvenue')
	else:
		return redirect('https://app.prospectly.fr/accueil')


@landing.route('/accueil')
def home():
	return render_template('landing/home.html', title='ProspectLy - Accueil')


@landing.route('/offres')
def pricing():
	return render_template('landing/pricing.html', title='ProspectLy - Offre')

@landing.route('/conditions-generales')
def terms_conditions():
	return render_template('landing/terms-conditions.html', title='ProspectLy - CGV')
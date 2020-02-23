from datetime import datetime 
from flask import render_template, url_for, redirect, session, flash
from . import main
from app import app

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
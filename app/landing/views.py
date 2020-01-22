from datetime import datetime 
from flask import render_template, url_for, redirect, session
from app.landing import landing


@landing.route('/')
def index():
	return render_template('layout/landing_base.html', title='ProspectLy - Bienvenue')


@landing.route('/accueil')
def home():
	return render_template('landing/home.html', title='ProspectLy - Accueil')


@landing.route('/offre')
def pricing():
	return render_template('landing/pricing.html', title='ProspectLy - Offre')

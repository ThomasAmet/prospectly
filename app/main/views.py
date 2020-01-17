from datetime import datetime 
from flask import render_template, url_for, redirect, session
from app.main import main


@main.route('/')
def index():
	return render_template('base.html', title='ProspectLy - Bienvenue')


@main.route('/accueil')
def home():
	return render_template('main/home.html', title='ProspectLy - Accueil')


@main.route('/offre')
def pricing():
	return render_template('main/pricing.html', title='ProspectLy - Offre')

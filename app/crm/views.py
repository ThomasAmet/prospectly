from flask import render_template, redirect, url_for, request
from . import crm

@crm.route('/')
def index():
	return render_template('index.html')

@crm.route('/dashboard')
def home():
	return render_template('dashboard.html')

@crm.route('/opportunites/list')
def opportunities_list():
	return render_template('opportunities-list.html')
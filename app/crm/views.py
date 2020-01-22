from flask import render_template, redirect, url_for, request
from . import crm

@crm.route('/')
def index:
	return render_template('layout/application_base.html')
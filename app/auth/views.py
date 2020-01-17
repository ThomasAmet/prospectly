from functools import wraps 
from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_talisman import ALLOW_FROM
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from app import db
from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User



def admin_login_required(func):
	@wraps(func)
	def decorated_view(*args, **kwargs):
		if not current_user.is_admin():
			return abort(403)
		return func(*args, **kwargs)
	return decorated_view



@auth.route('/inscription', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		try:
			user = User(first_name=form.first_name.data.capitalize(), last_name=form.last_name.data.capitalize(), 
			email=form.email.data.lower())
			user.set_password(form.password.data)
			user.set_username()
			db.session.add(user)
			db.session.commit()
			flash('Vous pouvez vous connecter.')
		except:
			db.session.rollback()
		return redirect(url_for('auth.login'))
	return render_template('auth/signup.html', form=form)



@auth.route('/connexion', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		redirect( url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			next = request.args.get('next')
			if next is None or not next.startswith('/'):
				next = url_for('main.home')
			return redirect(next)
		else:
			flash('Email ou mot de passe invalide.')
	return render_template('auth/login.html', form=form)



@auth.route('/deconnexion')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.home'))



class AdminMyIndexView(AdminIndexView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_admin()



class AdminHomeView(BaseView):
	@expose('/')
	def index(self):
		return self.render('main/home.html')
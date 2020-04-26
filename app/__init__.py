from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_admin import Admin # Initial solution but at the end, required to built own admin view
from flask_admin.contrib.sqla import ModelView
from flask_talisman import Talisman, ALLOW_FROM
from config import DevelopmentConfig, TestConfig, ProductionConfig


app = Flask(__name__, static_folder='./static', template_folder='./layouts')
app.config.from_object(DevelopmentConfig) # Dont forget to switch stripe key in prospectly.js


talisman = Talisman(app, 
	content_security_policy=app.config['CSP'],
	content_security_policy_nonce_in=['script-src'])
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# bootstrap = Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'# set the endpoint for the login page
login_manager.login_message = 'Vous devez etre connecté pour voir cette page.'


from .models import *

from .errors import errors as errors_blueprint
app.register_blueprint(errors_blueprint)
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)
from .leads import leads as leads_blueprint
app.register_blueprint(leads_blueprint)
from .crm import crm as crm_blueprint
app.register_blueprint(crm_blueprint)

from .auth.views import *

admin = Admin(app, name='ProspectLy', index_view=AdminMyIndexView(), template_mode='bootstrap3')
# admin.add_view(AdminHomeView(name='Home'))
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(CompanyLead, db.session))
admin.add_view(AdminModelView(ContactLead, db.session))
admin.add_view(AdminModelView(LeadRequest, db.session))
admin.add_view(AdminModelView(Subscription, db.session))
admin.add_view(AdminModelView(Plan, db.session))
admin.add_view(AdminModelView(Company, db.session))
admin.add_view(AdminModelView(Contact, db.session))
admin.add_view(AdminModelView(ContactsEmail, db.session))
admin.add_view(AdminModelView(Opportunity, db.session))
admin.add_view(AdminModelView(OpportunityStep, db.session))
admin.add_view(AdminModelView(CommercialStage, db.session))
admin.add_view(AdminModelView(Status, db.session))
admin.add_view(AdminModelView(Task, db.session))
admin.add_view(AdminModelView(Note, db.session))


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_admin import Admin # Initial solution but at the end, required to built own admin view
from flask_admin.contrib.sqla import ModelView
from flask_talisman import Talisman, ALLOW_FROM
from config import DevelopmentConfig, TestConfig


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

talisman = Talisman(app, content_security_policy=app.config['CSP'])
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# bootstrap = Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'# set the endpoint for the login page
login_manager.login_message = 'Vous devez etre connectes pour voir cette page'


from .models import *

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')
from .leads import leads as leads_blueprint
app.register_blueprint(leads_blueprint)

from .auth.views import *

admin = Admin(app, name='ProspectLy', index_view=AdminMyIndexView(), template_mode='bootstrap3')
admin.add_view(AdminHomeView(name='Home'))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Lead, db.session))
admin.add_view(ModelView(Subscription, db.session))
admin.add_view(ModelView(Plan, db.session))
admin.add_view(ModelView(LeadRequest, db.session))
admin.add_view(ModelView(Contact, db.session))
admin.add_view(ModelView(Opportunity, db.session))
admin.add_view(ModelView(CommercialStage, db.session))
admin.add_view(ModelView(Status, db.session))
admin.add_view(ModelView(CommercialStageStep, db.session))

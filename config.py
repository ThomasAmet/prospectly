import os

basedir = os.path.abspath(os.path.dirname(__file__))

# There are three different ways to store the data in the application.
# You can choose 'datastore', 'cloudsql', or 'mongodb'. Be sure to
# configure the respective settings for the one you choose below.
# You do not have to configure the other data backends. If unsure, choose
# 'datastore' as it does not require any additional configuration.
DATA_BACKEND = 'cloudsql'

# Google Cloud Project ID. This can be found on the 'Overview' page at
# https://console.developers.google.com
PROJECT_ID = 'prospectly-app'

# Set this value to the Cloud SQL connection name, e.g.
#   "project:region:cloudsql-instance".
# You must also update the value in app.yaml.
CLOUDSQL_CONNECTION_NAME = 'prospectly-app:europe-west1:mysql-instance'



class BaseConfig():
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USE_SSL = False
	# MAIL_PORT = 465
	# MAIL_USE_TLS = False
	# MAIL_USE_SSL = True
	MAIL_USERNAME = 'thomas@prospecly.fr'
	MAIL_PASSWORD = 'Helloworld2020#'
	STRIPE_SECRET_KEY = 'sk_test_jezU1v6w8mAaxIQMvWOs2JxD00Ps2BSFcQ'
	STRIPE_PUBLISHABLE_KEY = 'pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5'
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-a-temp-key'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAX_CONTENT_LENGTH = 0.2 * 1024 * 1024 # limit size of uploaded file to 200kb
	UPLOAD_FOLDER = 'csv/uploads/'
	CSP = {
    # Fonts from fonts.google.com
    'font-src': '\'self\' themes.googleusercontent.com *.gstatic.com static/fonts/',
    # <iframe> based embedding for Maps and Youtube.
    'frame-src': '\'self\' www.google.com www.youtube.com https://js.stripe.com https://hooks.stripe.com', 
    # Assorted Google-hosted Libraries/APIs.
    'script-src': ['\'self\' ajax.googleapis.com *.googleanalytics.com static/js/*'
                  '*.google-analytics.com stackpath.bootstrapcdn.com cdnjs.cloudflare.com https://js.stripe.com'],
    # Used by generated code from http://www.google.com/fonts
    'style-src': ['\'self\'', 'ajax.googleapis.com', 'fonts.googleapis.com', '\'unsafe-inline\'',
                 '*.gstatic.com stackpath.bootstrapcdn.com'],
    'default-src': '\'self\' *.gstatic.com https://js.stripe.com/',
    'connect-src': 'https://api.stripe.com'
	}
	

	# MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
	# MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
	# MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in 'true', 'on', '1
	# MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test-config.db')


class DevelopmentConfig(BaseConfig):
	DEBUG = True
	CLOUDSQL_USER = 'thomas_admin'
	CLOUDSQL_PASSWORD = 'difficult-password-to-guess' or os.environ.get('CLOUDSQL_PASSWORD')
	
	# CloudSQL & SQLAlchemy configuration
	CLOUDSQL_DATABASE = 'prospectly_development_database'
	# To start the proxy, use:
	#
	#	$ cloud_sql_proxy -instances=your-connection-name=tcp:3306
	#
	LOCAL_SQLALCHEMY_DATABASE_URI = (
		'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
		user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD, database=CLOUDSQL_DATABASE
		)
	# When running on App Engine a unix socket is used to connect to the cloudsql instance.
	LIVE_SQLALCHEMY_DATABASE_URI = (
		'mysql+pymysql://{user}:{password}@localhost/{database}'
		'?unix_socket=/cloudsql/{connection_name}').format(
		user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
		database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)

	if os.environ.get('GAE_INSTANCE'):
		SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
	else:
		SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI



class ProductionConfig(BaseConfig):
	
	CLOUDSQL_USER = 'thomas_admin'
	CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD') or 'difficult-password-to-guess'
	
	# CloudSQL & SQLAlchemy configuration
	CLOUDSQL_DATABASE = 'prospectly_production_database'
	# To start the proxy, use:
	#
	#	$ cloud_sql_proxy -instances=your-connection-name=tcp:3306
	#
	LOCAL_SQLALCHEMY_DATABASE_URI = (
		'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
		user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD, database=CLOUDSQL_DATABASE
		)
	# When running on App Engine a unix socket is used to connect to the cloudsql instance.
	LIVE_SQLALCHEMY_DATABASE_URI = (
		'mysql+pymysql://{user}:{password}@localhost/{database}'
		'?unix_socket=/cloudsql/{connection_name}').format(
		user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
		database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)

	if os.environ.get('GAE_INSTANCE'):
		SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
		DEBUG = False
	else:
		SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI
		DEBUG = True
		
# class DevelopmentConfig(BaseConfig):
# 	DEBUG = True

# 	# CloudSQL & SQLAlchemy configuration
# 	# Replace the following values the respective values of your Cloud SQL
# 	# instance.
# 	CLOUDSQL_DATABASE = 'prospectly_development_database'
# 	# The CloudSQL proxy is used locally to connect to the cloudsql instance.
# 	# To start the proxy, use:
# 	#
# 	#   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
# 	#
# 	# Port 3306 is the standard MySQL port. If you need to use a different port,
# 	# change the 3306 to a different port number.
# 	# Alternatively, you could use a local MySQL instance for testing.

# 	LOCAL_SQLALCHEMY_DATABASE_URI = ('mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
# 		'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format()
# 	# When running on App Engine a unix socket is used to connect to the cloudsql
# 	# instance.
# 	LIVE_SQLALCHEMY_DATABASE_URI = ('mysql+pymysql://{user}:{password}@localhost/{database}'
# 		'?unix_socket=/cloudsql/{connection_name}').format(
# 		user=gcp_config['CLOUDSQL_USER'], password=gcp_config['CLOUDSQL_PASSWORD'],
# 		database=gcp_config['CLOUDSQL_DATABASE'], connection_name=CLOUDSQL_CONNECTION_NAME)

# 	if os.environ.get('GAE_INSTANCE'):
# 		SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
# 	else:
# 		SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI

# class ProductionConfig(BaseConfig):
#     # CloudSQL & SQLAlchemy configuration
# 	# Replace the following values the respective values of your Cloud SQL
# 	# instance.

# 	CLOUDSQL_USER ='thomas_admin',
# 	CLOUDSQL_PASSWORD = 'difficult-password-to-guess',
# 	CLOUDSQL_DATABASE = 'prospectly_database'


#     # The CloudSQL proxy is used locally to connect to the cloudsql instance.
# 	# To start the proxy, use:
# 	#
# 	#   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
# 	#
# 	# Port 3306 is the standard MySQL port. If you need to use a different port,
# 	# change the 3306 to a different port number.

# 	# Alternatively, you could use a local MySQL instance for testing.
# 	LOCAL_SQLALCHEMY_DATABASE_URI = (
# 	    'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
# 	        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
# 	        database=CLOUDSQL_DATABASE)

#     # When running on App Engine a unix socket is used to connect to the cloudsql
# 	# instance.
# 	LIVE_SQLALCHEMY_DATABASE_URI = (
# 	    'mysql+pymysql://{user}:{password}@localhost/{database}'
# 	    '?unix_socket=/cloudsql/{connection_name}').format(
# 	        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
# 	        database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)

#     if os.environ.get('GAE_INSTANCE'):
#         SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
#     else:
#         SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI
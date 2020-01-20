from . import crm

@crm.route('/')
def index:
	return 'Hello'
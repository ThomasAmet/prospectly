from app import app
from app.models import *


@app.shell_context_processor
def configure_shell_context():
	return {'db': db, 'User': User, 'Plan':Plan, 'Lead': Lead, 'LeadRequest': LeadRequest, 'Subscription': Subscription, 'Note':Note,
	 'Contact':Contact, 'Status':Status, 'Task':Task, 'CommercialStageStep':CommercialStageStep, 'Opportunity':Opportunity}


if __name__ == '__main__':
	app.run(debug=True, port=9191)
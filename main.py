from app import app
from app.models import *


@app.shell_context_processor
def configure_shell_context():
	return {'db': db, 'User': User, 'Plan':Plan, 'Lead': Lead, 'Lead_Request': LeadRequest, 'Subscription': Subscription, 'Note':Note, 'Company':Company, 'Commercial_Stage_Step':CommercialStageStep,
	 'Contact':Contact, 'Contacts_Email':ContactsEmail, 'Status':Status, 'Task':Task, 'Commercial_Step':CommercialStage, 'Opportunity':Opportunity, 'Opportunity_Steps':OpportunityStep}


if __name__ == '__main__':
	app.run(debug=app.config['DEBUG'], port=9191)
from app import app
from app.models import *


@app.shell_context_processor
def configure_shell_context():
	return {'db': db, 'User': User, 'Subscription': Subscription, 'Plan':Plan, 'CompanyLead': CompanyLead, 'ContactLead': ContactLead, 'LeadRequest':LeadRequest, 'Note':Note, 'Company':Company,
	 'Contact':Contact, 'ContactsEmail':ContactsEmail, 'Status':Status, 'Task':Task, 'CommercialStep':CommercialStage, 'Opportunity':Opportunity, 'OpportunityStep':OpportunityStep}



if __name__ == '__main__':
	app.run(debug=True, port=9191)
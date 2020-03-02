from app import app
from app.models import *


@app.shell_context_processor
def configure_shell_context():
	return {'db': db, 'User': User, 'Plan':Plan, 'Lead': Lead, 'Lead_Request': LeadRequest, 'Subscription': Subscription, 'Note':Note,
	 'Contact':Contact, 'Status':Status, 'Task':Task, 'Commercial_Step':CommercialStage, 'Opportunity':Opportunity, 'Opportunity_Stage':CommercialStageStep}


if __name__ == '__main__':
	app.run(debug=True, port=9191)
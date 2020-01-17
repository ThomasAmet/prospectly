# import logging
# logging.basicConfig(level=logging.INFO)
import pandas as pd
import numpy as np
from app import db
from app.models import Lead
from datetime import datetime


def load_csv(csv_file_path):
	try:
		data = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
		if len(data.columns) == 1:
			data = pd.read_csv(csv_file_path, sep=',', encoding='utf-8')
	except:
		data = pd.read_csv(csv_file_path,  sep=';', encoding='latin1')
		if len(data.columns) == 1:
			data = pd.read_csv(csv_file_path, sep=',', encoding='latin1')
	logging.info('CSV successfully loaded.')
	return data


def subscription_plans():

	subscription_plans = {
		'Basic': {
			'max_results': 10,
			'monthly_price_eur': 99,
			'unlimited': False
		},
		'Premium': {
			'max_results': 25,
			'monthly_price_eur': 149,
			'unlimited': False
		},
		'Beta': {
			'max_results': 25,
			'monthly_price_eur': 250,
			'unlimited': True
		}
	}
	return subscription_plans



def query_result_to_df(query_results):

	df = pd.DataFrame([[r.company_name, r.company_address, r.company_postal_code, r.company_city, r.company_email,
						 r.company_email_bcc, r.company_phone, r.owner_firstname, r.owner_lastname] for r in query_results],
					    columns=['company_name', 'company_address', 'company_postal_code', 'company_city', 'company_email',
								 'company_email_bcc', 'company_phone', 'owner_firstname', 'owner_lastname'])
	return df


def record_query(lead_id, user_id):

	lr = Lead_Request(user_id=user_id, lead_id=lead_id)
	db.session.add(lr)
	return True


def set_debug_parser(**kwargs):
	"""
        Generate an object of class parser while in debug mode or in developement mode
        The parser object can get its argument defined when creating the object or using the 'add_argument' method

        Arguments:
            **kwargs: list of arguments with their value assigmes
        Example:
            new_parser = set_debug_parser(argument1 = 'value1')
            new_parser.add_argument(argument2 = 'value2'

        Return:
        An object from class parser
    """

	class parser:
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				setattr(self, key, value)

		def add_argument(self, **kwargs):
			self.__dict__.update(kwargs)

	return parser(**kwargs)
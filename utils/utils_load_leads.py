# This method uses SQLAlchemy or Flask SQLAlcheny
from time import time
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# export PYTHONPATH="/Users/Thomas/Documents/Data Science/Projects/ProspectLy"

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import db
from app.models import Lead
from bin.all_utils import set_debug_parser, load_csv
import glob
import argparse
from functools import partial



def lead_to_dict(csv_row):
    # This function is equivalent to what df.iterrows() does
    leads_infos_col = ['company_name', 'company_address', 'company_postal_code', 'company_city', 'company_email','company_email_bcc',
                       'company_phone', 'company_activity_field', 'owner_firstname', 'owner_lastname']
    zip_dic = zip(leads_infos_col, list(csv_row))
    return dict(zip_dic)


def add_lead_flaskalch(row):
    l = Lead(company_name=row['company_name'],
             company_address=row['company_address'],
             company_postal_code=row['company_postal_code'],
             company_city=row['company_city'],
             company_email=row['company_email'],
             company_email_bcc=row['company_email_bcc'],
             company_phone=row['company_phone'],
             company_activity_field=row['company_activity_field'],
             owner_firstname=row['owner_firstname'],
             owner_lastname=row['owner_lastname'])

    if Lead.exists(l):
        logging.info('This company already exists')
        return False
    db.session.add(l)
    logging.info('Lead succesfully added')
    return True


def add_lead_regalch(session, row):
    print('Adding: ' + row['company_name'])
    record = Lead(**{
        'company_name': row['company_name'],
        'company_address': row['company_address'],
        'company_postal_code': row['company_postal_code'],
        'company_city': row['company_city'],
        'company_email': row['company_email'],
        'company_email_bcc': row['company_email_bcc'],
        'company_phone': row['company_phone'],
        'company_activity_field': row['company_activity'],
        'owner_firstname': row['owner_firstname'],
        'owner_lastname': row['owner_lastname'],
    })
    if Lead.exists(record):
        print('This company already exists')
        response = False
    else:
        session.add(record) #Add all the records
        print('Lead succesfully added')
        response = True
    return response


def populate_lead_flaskalch(csv_file_path):
        logging.info('csv path: {}'.format(csv_file_path))

        csv_data = load_csv(csv_file_path)
        logging.info('csv successfuly loaded')

        for i, row in csv_data.iterrows():
            add_lead_flaskalch(row=row)

        db.session.commit()
        logging.info('All leads have been imported !')
        return True

def populate_lead_regalch(database_path, csv_path_file):
    Base = declarative_base()

    #Create the database
    engine = create_engine('sqlite:///' + database_path)
    metadata = Base.metadata
    metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    session = session()

    data = load_csv(csv_path_file)
    # row = data.iloc[18]
    for i, row in data.iterrows():
       add_lead_regalch(session=session, row=row)

    session.commit() #Attempt to commit all the records
    print('Done')
    return True



# [START ...]
def populate_leads_table(leads_data):
    try:
        # i is index of the row, row is a pd.Series object
        for i, row in leads_data.iterrows():
            # change from pd.Series to dict to pass it as **kwargs
            lead_data = dict(row)
            lead = Lead(**lead_data)
            if not lead.exists():
                db.session.add(lead)
            else:
                continue
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False     
# [... END]

# [START ...]
def main(args):
    try:
        if args.file_name == 'all':
            logging.info('multi file')
            csv_file_path = glob.glob('csv/leads_*.csv')
            leads_data = load_csv(csv_file_path)
            populate_lead_table(leads_data)
        else:
            logging.info('single file')
            csv_file_path = "csv/" + args.file_name
            leads_data = load_csv(csv_file_path)
            populate_lead_table(leads_data)
    except:
        print('Error !')
        db.session.rollback()  # Rollback the changes on error
    finally:
        db.session.close()  # Close the connection
# [... END]


# csv_file_path = 'bin/csv/leads_test.csv'
# database_path = 'app/prospectly.db'

parser = set_debug_parser()
parser.add_argument(file_name='leads_gym_2019-09-27.csv')
args = parser

parser = argparse.ArgumentParser()
parser.add_argument("file_name", help="File's name of the csv containing the leads to be uploaded. The file must be located in 'csv/' folder. Enter 'all' to load all the csv starting with 'leads_'")
args = parser.parse_args()

if __name__ == "__main__":
    t = time()
    main(args)
    logging.info("Time elapsed: " + str(time() - t) + " s.")#0.091s

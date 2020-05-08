# You can start the proxy using TCP sockets. Start the proxy using Cloud SDK authentication:
# ./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME>=tcp:3306

# You can connect to the proxy from any language that enables you to connect to a Unix or TCP socket (Python+sqlalchemy)

# https://github.com/mardix/active-alchemy

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("..")

import argparse
import logging
import pandas as pd
from time import time
from app import db
from app.models import *

logging.basicConfig(level=logging.INFO)



from dotenv import load_dotenv, find_dotenv
from active_alchemy import ActiveAlchemy
from sqlalchemy import create_engine


# load_dotenv(find_dotenv())
#
# CLOUDSQL_USER = os.getenv('CLOUDSQL_USER')
# CLOUDSQL_PASSWORD = os.getenv('CLOUDSQL_PASSWORD')
# CLOUDSQL_DATABASE = os.getenv('CLOUDSQL_DATABASE')
#
# engine_path = "mysql+pymysql://{user}:{password}@127.0.0.1/{database}".format(user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD, database=CLOUDSQL_DATABASE)
# engine = create_engine(engine_path)
# db = ActiveAlchemy(engine_path)

os.getcwd()
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)

print(''.format(dirname))

logging.info(' app root is: ' + str(dirname))
# will return /Users/Thomas/Documents/Data Science/Training/WebApp/flask_prospectly/utils

# class Loader():

# Part that will read the csv and reformat it  from csv to scsv or tsv to scsv (manual)
# filename = '2020-04-27_all_immo_937'
# filename = '2020-04-26_all_fitness'
filename = '2020-05-04_ecomm'
filepath = os.path.join(dirname, 'scraping', 'output', 'import', filename)
df = pd.read_csv(filepath+'.tsv', encoding='utf-8', sep='\t', header=0)
df.to_csv(filepath+'.csv', encoding='utf-8', sep=';', index=False)




########################################################
# Manual transformation and clean for fitness dataframe

filename = '2020-04-26_all_fitness'
filepath = os.path.join(dirname, 'scraping', 'output', 'import', filename)
df = pd.read_csv(filepath+'.csv', encoding='utf-8', sep=';', header=0)

df['contact_position'] = df['contact_position'].str.replace(r'(\.\.\..*)', '')
df['contact_position'] = df['contact_position'].str.replace(r'(Fr\.Linkedin\.Com.*)', '')
df['contact_position'] = df['contact_position'].str.replace(r'(\s>.*)', '')
df['contact_position'] = df['contact_position'].str.replace(r'(\s\|.*)', '')
df.loc[3123,['contact_lastname']] = 'Racouchot'
df.loc[3123,['contact_position']] = 'Owner'

df.loc[df['contact_lastname'].str.len()>20, df.columns[-8:]] = np.nan
df.loc[df['contact_position'].str.len()>60, 'contact_position'] = df.loc[df['contact_position'].str.len()>60, 'contact_position'].str.slice(0, 23)
df = df.fillna('')
df['contact_position'] = df['contact_position'].str.replace(r'Barontini(.*)', '')


########################################################




parser = argparse.ArgumentParser()
parser.add_argument("--file_path", help="File's path for the csv with the leads to be uploaded. Ex:'input/leads.csv'")
args = parser.parse_args()


def main(args):

    df = pd.read_csv(args.file_path, encoding='utf-8', sep=';')
    df_company, df_contact = parse_df(df)
    load_leads(df_company, df_contact)


def read_csv(filepath):
    df = pd.read_csv(filepath, encoding='utf-8', sep=';', header=0)
    df = df.fillna('')
    return df


def parse_df(df):
    '''
    Take the full df and split it into a company_df and a contact_df
    return 2 df, one for companys, one for contacts
    '''
    # Subset the df into 2 df (1 for company, 1 for contact)
    df_company = df[df.columns[:-8]]
    df_contact = df[df.columns[-8:]]

    # Rename the contact df by removing the contact part in the colnames
    newcols = df.columns[-8:].str.replace('contact_', '')
    df_contact.columns = newcols

    return df_company, df_contact


def load_leads(df_company, df_contact):
    '''
    iterate through the df object and return a index and a serie object
    we use .to_dict() method on the serie object to feed our db.Model object (Lead Table)
    '''

    logging.info('start loading data...')

    # for i in df_company.index:
    for i in range(1):
        # try:
        load_rows(df_company.iloc[i], df_contact.iloc[i])
            # logging.info('row {}, success'.format(i))
        # except:
        #     logging.info('row {}, fail'.format(i))
        #     continue
    db.session.commit()

    logging.info('... loading done')


def company_exists(company_dict):
    data = company_dict
    company_lead = CompanyLead.query.filter_by(name=data.get('name'), address=data.get('address')).first()
    return company_lead


def load_rows(company_row, contact_row):
    # Parse company serie to dict and create a leadcompany

    # CHeck if the company already exisits (based on name and address
    company_data = company_row.to_dict()
    lead_company = company_exists(company_data)

    # Create a new company
    if not lead_company:
        leadcompany = CompanyLead(**company_data)
        db.session.add(leadcompany)
        db.session.flush()

    # Parse contact serie into a dict, add a 'company_id' attribute and create a contactlead
    contact_data = contact_row.to_dict()
    if contact_data.get('firstname') and contact_data.get('last_name'):
        contact_data['company_id'] = leadcompany.id
        ContactLead(**contact_data)
        db.session.add()



if __name__=='__main__':
    t = time()
    # main()
    logging.info("Time elapsed: " + str(time() - t) + " s.")

#
# # This method uses SQLAlchemy or Flask SQLAlcheny



# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#
# # export PYTHONPATH="/Users/Thomas/Documents/Data Science/Projects/ProspectLy"
#
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# from app import db
# from app.models import Lead
# from utils.all_utils import set_debug_parser, load_csv
# import glob
# import argparse
# from functools import partial
#
#
#
# def lead_to_dict(csv_row):
#     # This function is equivalent to what df.iterrows() does
#     leads_infos_col = ['company_name', 'company_address', 'company_postal_code', 'company_city', 'company_email','company_email_bcc',
#                        'company_phone', 'company_activity_field', 'owner_firstname', 'owner_lastname']
#     zip_dic = zip(leads_infos_col, list(csv_row))
#     return dict(zip_dic)
#
#
# def add_lead_flaskalch(row):
#     l = Lead(company_name=row['company_name'],
#              company_address=row['company_address'],
#              company_postal_code=row['company_postal_code'],
#              company_city=row['company_city'],
#              company_email=row['company_email'],
#              company_email_bcc=row['company_email_bcc'],
#              company_phone=row['company_phone'],
#              company_activity_field=row['company_activity_field'],
#              owner_firstname=row['owner_firstname'],
#              owner_lastname=row['owner_lastname'])
#
#     if Lead.exists(l):
#         logging.info('This company already exists')
#         return False
#     db.session.add(l)
#     logging.info('Lead succesfully added')
#     return True
#
#
# def add_lead_regalch(session, row):
#     print('Adding: ' + row['company_name'])
#     record = Lead(**{
#         'company_name': row['company_name'],
#         'company_address': row['company_address'],
#         'company_postal_code': row['company_postal_code'],
#         'company_city': row['company_city'],
#         'company_email': row['company_email'],
#         'company_email_bcc': row['company_email_bcc'],
#         'company_phone': row['company_phone'],
#         'company_activity_field': row['company_activity'],
#         'owner_firstname': row['owner_firstname'],
#         'owner_lastname': row['owner_lastname'],
#     })
#     if Lead.exists(record):
#         print('This company already exists')
#         response = False
#     else:
#         session.add(record) #Add all the records
#         print('Lead succesfully added')
#         response = True
#     return response
#
#
# def populate_lead_flaskalch(csv_file_path):
#         logging.info('csv path: {}'.format(csv_file_path))
#
#         csv_data = load_csv(csv_file_path)
#         logging.info('csv successfuly loaded')
#
#         for i, row in csv_data.iterrows():
#             add_lead_flaskalch(row=row)
#
#         db.session.commit()
#         logging.info('All leads have been imported !')
#         return True
#
# def populate_lead_regalch(database_path, csv_path_file):
#     Base = declarative_base()
#
#     #Create the database
#     engine = create_engine('sqlite:///' + database_path)
#     metadata = Base.metadata
#     metadata.create_all(engine)
#
#     #Create the session
#     session = sessionmaker()
#     session.configure(bind=engine)
#     session = session()
#
#     data = load_csv(csv_path_file)
#     # row = data.iloc[18]
#     for i, row in data.iterrows():
#        add_lead_regalch(session=session, row=row)
#
#     session.commit() #Attempt to commit all the records
#     print('Done')
#     return True
#
#
#
# # [START ...]
# def populate_leads_table(leads_data):
#     try:
#         # i is index of the row, row is a pd.Series object
#         for i, row in leads_data.iterrows():
#             # change from pd.Series to dict to pass it as **kwargs
#             lead_data = dict(row)
#             lead = Lead(**lead_data)
#             if not lead.exists():
#                 db.session.add(lead)
#             else:
#                 continue
#         db.session.commit()
#         return True
#     except Exception as e:
#         db.session.rollback()
#         return False
# # [... END]
#
# # [START ...]
# def main(args):
#     try:
#         if args.file_name == 'all':
#             logging.info('multi file')
#             csv_file_path = glob.glob('csv/leads_*.csv')
#             leads_data = load_csv(csv_file_path)
#             populate_lead_table(leads_data)
#         else:
#             logging.info('single file')
#             csv_file_path = "csv/" + args.file_name
#             leads_data = load_csv(csv_file_path)
#             populate_lead_table(leads_data)
#     except:
#         print('Error !')
#         db.session.rollback()  # Rollback the changes on error
#     finally:
#         db.session.close()  # Close the connection
# # [... END]
#
#
# # csv_file_path = 'bin/csv/leads_test.csv'
# # database_path = 'app/prospectly.db'
#
# parser = set_debug_parser()
# parser.add_argument(file_name='leads_gym_2019-09-27.csv')
# args = parser
#
# parser = argparse.ArgumentParser()
# parser.add_argument("file_name", help="File's name of the csv containing the leads to be uploaded. The file must be located in 'csv/' folder. Enter 'all' to load all the csv starting with 'leads_'")
# args = parser.parse_args()
#
# if __name__ == "__main__":
#     t = time()
#     main(args)
#     logging.info("Time elapsed: " + str(time() - t) + " s.")#0.091s

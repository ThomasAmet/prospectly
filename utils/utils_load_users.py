import os
import logging
import argparse

logging.basicConfig(level=logging.INFO)
basedir = os.path.abspath(os.path.dirname(__file__))
logging.info(' app root is: ' + str(basedir))

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# export PYTHONPATH="/Users/Thomas/Documents/Data Science/Projects/ProspectLy"

from app import db
from app.models import User, Subscription
from bin.all_utils import subscription_plans, set_debug_parser, load_csv



def create_user(user_infos, password='firstPassword'):
    u = User(first_name=user_infos['first_name'].strip(), last_name=user_infos['last_name'].strip(), email=user_infos['email'].strip())
    u.set_username()
    exists = User.exist_user(u)
    if exists:
        logging.info('User already exists !')
        u = User.query.filter_by(email=user_infos['email'].strip()).first()
        return u.id
    else:
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        logging.info('User correctly added!')
        return u.id


def record_subscription(user_id, plan_type='Basic'):
    exists = User.query.get(user_id).subscription.all()
    if exists:
        logging.info('User already have a subscription !')
        return 0
    else:
        s = Subscription(plan_type=plan_type,
                         user_id=user_id,
                         max_results=subscription_plans()[plan_type]['max_results'],
                         monthly_price_eur=subscription_plans()[plan_type]['monthly_price_eur'],
                         unlimited=subscription_plans()[plan_type]['unlimited'])
        db.session.add(s)
        db.session.commit()
        logging.info("User's subscription correctly set!")
        return s.id

def upload_user(user_infos):
    """
    Create a user, and associate a subscription
    :param user_infos:
    :return:
    """
    user_id = create_user(user_infos)
    # if user_infos['admin']:
    #     u = User.query.filter(User.id == user_id).first()
    #     u.username = str(u.first_name).capitalize()+'_Admin'
    record_subscription(user_id, user_infos['plan_type'].strip())
    return 0


def load_unique_user(args):
    logging.info('Loading only one user')
    try:
        cols = ['first_name', 'last_name', 'email', 'plan_type']
        values = [args.first_name.strip(), args.last_name.strip(), args.email.strip(), args.plan_type.strip()]
        user_infos = dict(zip(cols, values))
        logging.info('User information ready.')
        upload_user(user_infos=user_infos)
        logging.info("Operation done with success!")
        return 0
    except:
        logging.info('User loading failed')


def load_multiple_users(args):
    logging.info('Loading multiple users')
    try:
        csv_file_path = "csv/" + args.file_name
        data = load_csv(csv_file_path=csv_file_path)
        for i, row in data.iterrows():
            upload_user(user_infos=row)
        logging.info("Operation done with success!")
        return 0
    except:
        logging.info('User loading failed')



def check_parser_error(args):
    """
    This function is deprecated now but the logic is interesting
    :param args:
    :return:
    """
    if not args.file_name:
        if not (args.first_name and args.last_name and args.email and args.plan_type):
            args.error("Without a csv_file_name, argument 'first_name', 'last_name', 'email', 'plan_type and 'admin' are required.")
    print(args)
    return 0


def main():
    # command_parser = argparse.ArgumentParser()
    # subparsers = command_parser.add_subparsers(help="Choose whether you wish to load a 'unique' or 'multiple' user(s)", dest="command")
    #
    # # Create 2 subparsers
    # unique_user_parser = subparsers.add_parser('unique')
    # multiple_users_parser = subparsers.add_parser('multiple')
    #
    # # Unique user
    # unique_user_parser.add_argument("first_name", help="New user's first name")
    # unique_user_parser.add_argument("last_name", help="New user's last name")
    # unique_user_parser.add_argument("email", help="New user's email ")
    # unique_user_parser.add_argument("plan_type", choices=['Basic', 'Premium', 'Beta'])
    # unique_user_parser.add_argument("admin", action="store_true")
    # unique_user_parser.set_defaults(func=load_unique_user)
    #
    # # Multiple users
    # multiple_users_parser.add_argument("file_name",
    #                                    help="csv's name containing users details. File needs to be located within csv folder")
    # multiple_users_parser.set_defaults(func=load_multiple_users)
    #
    # # Parse argument
    # command_parser.parse_args()

    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name", help="File's name for the csv with the users to be uploaded. Ex:'users.csv'")
    parser.add_argument("--first_name", help="New user's first name", default="Thomas")
    parser.add_argument("--last_name", help="New user's last name", default="Amet")
    parser.add_argument("--email", help="New user's email ", default="admin@example.com")
    parser.add_argument("--plan_type", choices=['Basic', 'Premium', 'Beta'])
    parser.add_argument("--admin", action="store_true")
    args = parser.parse_args()

    # parser = set_debug_parser()
    # parser.add_argument(first_name='Thomas')
    # parser.add_argument(last_name='Amet')
    # parser.add_argument(email='thomasamet@yahoo.fr')
    # parser.add_argument(plan_type='Beta')
    # parser.add_argument(admin=True)
    # parser.add_argument(file_name='users.csv')
    # args = parser

    if not check_parser_error(args):
        if args.file_name:
            load_multiple_users(args)
        else:
            load_unique_user(args)



if __name__ == '__main__':
    # python utils_load_users --filename users.csv
    # python utils_load_users --firstname thomas --lastname amet --email test@test.com ....
    main()

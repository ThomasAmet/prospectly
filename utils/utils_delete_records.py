import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# export PYTHONPATH="/Users/Thomas/Documents/Data Science/Projects/ProspectLy"

import logging
logging.basicConfig(level=logging.INFO)

from app import db
from app.models import User, Subscription, Lead, Lead_Request

from bin.all_utils import set_debug_parser
import argparse


def delete_user_requests(id):
    user_requests = Lead_Request.query.filter_by(user_id=id).all()
    if len(user_requests) > 0:
        for req in user_requests:
            db.session.delete(req)
        logging.info("< User's requests have been deleted>")
        return 0
    return "<No requests found for user {} or something went wrong>".format(User.query.get(id))

def delete_user_subs(id):
    user_subs = Subscription.query.filter(Subscription.user_id==id).all()
    if len(user_subs) > 0:
        for sub in user_subs:
            db.session.delete(sub)
        logging.info("<User's subscriptions have been deleted>")
        return True
    logging.info("<No subscription found for user {}".format(id))
    return 0


def delete_user(id):
    try:
        id = int(id)
        u = User.query.get(id)
    except:
        u = User.query.filter(User.username == id).first()
    if not u:
        logging.info('This user doesnt exist')
    else:
        delete_user_requests(id)
        delete_user_subs(id)
        db.session.delete(u)
        logging.info("User {} properly deleted")
        return 0


def delete_all_users():
    users = User.query.all()
    for u in users:
        delete_user_requests(id=u.id)
        delete_user_subs(id=u.id)
        db.session.delete(u)
        logging.info("All users properly deleted")
    return 0

def main(args):

    try:
        logging.info("You chose the table {}".format(args.table_name))
        if args.table_name == 'User':
            if args.record_id == 'all':
                delete_all_users()
            else:
                delete_user(args.record_id)
        else:
            logging.info('This features is not ready yet')

        db.session.commit()
        return "Operation done with success!"
    except:
        db.session.rollback()
        return "Operation failed!"


# parser = set_debug_parser()
# parser.add_argument("table_name")
# parser.add_argument("record_id")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("table_name", choices=['User', 'Lead'], help="Choose between the User table or Lead table")
    parser.add_argument("record_id", help="Username or ID for User Table, Company name or ID for Lead Table. Type 'all' to remove all records")
    args = parser.parse_args()


    main(args=args)
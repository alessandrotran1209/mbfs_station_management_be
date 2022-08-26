import hashlib

from db.MongoConn import MongoConn

import logging

logger = logging.getLogger(__name__)

class Account:

    def authenticate(self, client, username, password):
        user_collection = client['user']
        user = user_collection.find({"username" : username})
        for record in user:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashed_password == record['password']:
                print('Password matched')
                return True
        return False

    def get_user(self, username):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        user_collection = client['user']
        user = user_collection.find({"username": username})
        for record in user:
            u = record
            logger.info(record)
            return u

    def insert_user(self, data):
        try:
            mongo_conn = MongoConn()
            client = mongo_conn.conn()
            user_collection = client['user']

            user_collection.insert_one(data)
        except Exception as e:
            raise Exception(e)
        return True

    def get_statistics(self, operator):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        user_collection = client['user']
        fullname = ''
        records = user_collection.find({"username": operator}, {})
        for record in records:
            fullname = record['fullname']

        operation_collection = client['operation']
        total_operation = operation_collection.count_documents({"operator": operator})
        total_completed_operation = operation_collection.count_documents({"operator": operator, 'status': 1})
        total_uncompleted_operation = operation_collection.count_documents({"operator": operator, 'status': 0})

        station_collection = client['station']
        total_station = station_collection.count_documents({"operator": fullname})

        result = {
            "total_operation": total_operation,
            "total_completed_operation": total_completed_operation,
            "total_uncompleted_operation": total_uncompleted_operation,
            "total_station": total_station
        }
        return result
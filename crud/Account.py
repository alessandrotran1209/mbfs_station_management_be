import hashlib

from db.MongoConn import MongoConn

import logging

logger = logging.getLogger(__name__)


class Account:

    def authenticate(self, username, password):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        logger.info('Connection initiated')
        user_collection = client['user']
        user = user_collection.find({"username": username})
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

    def get_statistics(self, operator, fullname, role):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        operation_collection = client['operation']
        station_collection = client['station']

        if role == 'operator':
            total_operation = operation_collection.count_documents({"operator": operator})
            total_completed_operation = operation_collection.count_documents({"operator": operator, 'status': "1"})
            total_uncompleted_operation = operation_collection.count_documents({"operator": operator, 'status': "0"})
            total_station = station_collection.count_documents({"operator": fullname})
        elif role == 'group leader':
            total_operation = operation_collection.count_documents({"assigner": operator})
            total_completed_operation = operation_collection.count_documents({"assigner": operator, 'status': "1"})
            total_uncompleted_operation = operation_collection.count_documents({"assigner": operator, 'status': "0"})
            total_station = station_collection.count_documents({"group_leader": fullname})

        result = {
            "total_operation": total_operation,
            "total_completed_operation": total_completed_operation,
            "total_uncompleted_operation": total_uncompleted_operation,
            "total_station": total_station
        }
        return result

    def get_role(self, username):
        if username == 'admin':
            return 'admin'
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        group_leader_collection = client['group-leader']
        records = group_leader_collection.find_one({"username": username}, {"_id": 0})
        if records != None:
            return "group leader"
        return 'operator'

    def get_username_by_fullname(self, fullname):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        user_collection = client['user']
        record = user_collection.find_one({"fullname": fullname}, {"username": 1})
        username = record["username"]
        return username

    def get_top_work(self, username, role):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        operation_collection = client['operation']
        if role == 'operator':
            agg = [
                {"$match": {"operator":username} },
                {"$group" : {"_id" : "$work_code", "count" : {"$sum" : 1}}},
                {"$sort" : {"count" : -1}},
                {"$limit" : 3}
            ]
        elif role == 'group leader':
            agg = [
                {"$match": {"assigner":username} },
                {"$group" : {"_id" : "$work_code", "count" : {"$sum" : 1}}},
                {"$sort" : {"count" : -1}},
                {"$limit" : 3}
            ]

        records = operation_collection.aggregate(agg)
        ret = []
        for record in records:
            ret.append({"work_code": record["_id"], "count": record["count"]})
        return ret

    def change_password(self, username, password):
        try:
            mongo_conn = MongoConn()
            client = mongo_conn.conn()
            user_collection = client['user']
            result = user_collection.update_one({"username": username}, { "$set": { 'password': password } })
            return result.matched_count > 0 
        except:
            return False
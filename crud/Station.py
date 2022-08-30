from crud.Account import Account
from db.MongoConn import MongoConn
import logging

logger = logging.getLogger(__name__)

class Station:
    def list_stations(self, page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        total = station_collection.count_documents({})
        records = station_collection.find({}, {"_id": 0}).skip((page - 1) * 10).limit(10)

        list_station_detail = []
        index = 1
        for station in records:
            station['index'] = index + (page - 1) * 10
            list_station_detail.append(station)
            index += 1
        return list_station_detail, total

    def list_station_code(self):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        records = station_collection.find({}, {"_id": 0, "station_code": 1, "province": 1})
        list_station_code = []
        for station in records:
            list_station_code.append(station)

        return list_station_code

    def search_station(self, code='', province='', district='', page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']

        total = station_collection.count_documents(
            {"station_code": {'$regex': code}, "province": {'$regex': province}, "district": {'$regex': district}})
        records = station_collection.find(
            {"station_code": {'$regex': code}, "province": {'$regex': province}, "district": {'$regex': district}},
            {"_id": 0}).skip((page - 1) * 10).limit(10)
        list_station_code = []

        index = 1
        for station in records:
            station['index'] = index + (page - 1) * 10
            list_station_code.append(station)
            index += 1

        return list_station_code, total

    def list_operator_station(self, operator):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        user_collection = client['user']
        fullname = ''
        records = user_collection.find({"username": operator}, {})
        for record in records:
            fullname = record['fullname']

        station_collection = client['station']
        records = station_collection.find({"operator": fullname}, {"_id": 0, "station_code": 1, "province": 1})
        list_station_code = []
        for station in records:
            list_station_code.append(station)

        return list_station_code

    def list_group_station(self, operator):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        group_leader_collection = client['group-leader']
        fullname = ''
        record = group_leader_collection.find_one({"username": operator}, {})
        group_name = record['group']

        station_collection = client['station']
        records = station_collection.find({"group": group_name}, {"_id": 0, "station_code": 1})
        list_station_code = []
        for station in records:
            list_station_code.append(station)

        return list_station_code

    def get_station_coord(self, station_code):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']

        record = station_collection.find_one(
            {"station_code": station_code})
        return record['lat'], record['long']

    def get_operators_by_group_leader(self, username):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        group_leader_collection = client['group-leader']
        record = group_leader_collection.find_one({'username': username}, {"_id": 0, "group": 1})
        group_name = record["group"]
        logger.info(group_name)
        station_collection = client['station']
        records = station_collection.find({"group": group_name}, {"_id": 0, "operator": 1})

        set_operator = set()
        account = Account()
        list_operators = []
        for record in records:
            if len(record) == 0: continue
            fullname = record["operator"]
            if fullname in set_operator:
                continue
            set_operator.add(fullname)
            operator_username = account.get_username_by_fullname(fullname)
            data = {
                "username": operator_username,
                "fullname": fullname
            }
            list_operators.append(data)

        return list_operators

    def get_user_group(self, username):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        user_collection = client['user']
        record = user_collection.find_one({'username': username}, {"_id": 0, "fullname": 1})
        fullname = record["fullname"]
        station_collection = client['station']
        record = station_collection.find_one({'operator': fullname}, {"_id": 0, "group": 1})
        group_name = record["group"]
        return group_name

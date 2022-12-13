from crud.Account import Account
from db.MongoConn import MongoConn
from utils.groups import get_group_username
import utils.mock as mock
from utils.utils import get_hashed_password
import logging

logger = logging.getLogger(__name__)


class Station:
    def list_stations(self, role='', fullname='', page=1, group=''):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        query = {"operator": fullname, "group": {'$regex': group}
                 } if role != 'group leader' else {"group_leader": fullname}
        if role == 'admin':
            query = {}
        total = station_collection.count_documents(query)
        records = station_collection.find(
            query, {"_id": 0}).skip((page - 1) * 10).limit(10)

        list_station_detail = []
        index = 1
        for station in records:
            station['index'] = index + (page - 1) * 10
            list_station_detail.append(station)
            index += 1
        return list_station_detail, total

    def list_station_code(self, role, fullname, group):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        if role == 'operator':
            query = {"operator": fullname, "group": group}
        elif role == 'group leader':
            query = {"group_leader": fullname}
        elif role == 'admin':
            query = {}
        records = station_collection.find(query, {"_id": 0, "district": 1})
        list_station_code = []
        for station in records:
            list_station_code.append(station["district"])
        return list(set(list_station_code))

    def search_station(self, code='', province='', district='', page=1, fullname='', role='', group=''):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        station_collection = client['station']
        if role == 'operator':
            query = {"operator": fullname, "station_code": {'$regex': code}, "group": {
                '$regex': group}, "province": province, "district": {'$regex': district}}
        elif role == 'group leader':
            query = {"group_leader": fullname, "station_code": {
                '$regex': code}, "province": province, "district": {'$regex': district}}
        elif role == 'admin':
            query = {"station_code": {'$regex': code},
                     "province": province, "district": {'$regex': district}}
        total = station_collection.count_documents(query)
        records = station_collection.find(
            query,
            {"_id": 0}).skip((page - 1) * 10).limit(10)
        list_station_code = []

        index = 1
        for station in records:
            station['index'] = index + (page - 1) * 10
            list_station_code.append(station)
            index += 1

        return list_station_code, total

    def list_operator_station(self, operator_fullname, group):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        records = station_collection.find({"operator": operator_fullname, "group": group}, {
                                          "_id": 0, "station_code": 1, "province": 1})
        list_station_code = []
        for station in records:
            list_station_code.append(station)

        return list_station_code

    def list_group_station(self, leader_fullname):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        if leader_fullname == 'Cà Mau':
            records = station_collection.find({"group": leader_fullname}, {
                                              "_id": 0, "station_code": 1})
        else:
            records = station_collection.find({"group_leader": leader_fullname}, {
                                              "_id": 0, "station_code": 1})
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
        user_collection = client['user']
        record = group_leader_collection.find_one(
            {'username': username}, {"_id": 0, "group": 1})
        group_name = record["group"]
        station_collection = client['station']
        records = station_collection.distinct(
            "operator", {"group": group_name})
        list_operators = []
        for record in records:
            number_of_users = user_collection.count_documents(
                {"fullname": record})
            if number_of_users == 1:
                operator_username = user_collection.find_one(
                    {"fullname": record})
            else:
                group_leader_usernames = get_group_username()
                results = user_collection.find({"fullname": record})
                for result in results:
                    if "group" in result:
                        if result["group"] == group_name:
                            operator_username = {
                                "username": result["username"]}
                            continue
                    else:
                        print(group_leader_usernames)
                        if result["username"] in group_leader_usernames:
                            continue
                        else:
                            print(result)
                            operator_username = {
                                "username": result["username"]}
            data = {
                "username": operator_username['username'],
                "fullname": record
            }
            list_operators.append(data)

        return list_operators

    def get_user_group(self, username):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        user_collection = client['user']
        record = user_collection.find_one({'username': username})
        group_name = record["group"]
        return group_name

    def insert_update_stations(self, stations):
        print(stations)
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        account = Account()

        station_collection = client['station']
        for station in stations:
            print(station)
            query = {'station_code': station["station_code"]}
            duplicated_query = {
                'group': station["group"], 'operator': station["operator"]}
            duplicated_user_count = station_collection.count_documents(
                duplicated_query)
            deletion_result = station_collection.delete_one(query)
            insert_result = station_collection.insert_one(station)

            if insert_result.inserted_id:
                if duplicated_user_count == 0:
                    new_account = {
                        'username': mock.get_username(station["operator"]),
                        'password': get_hashed_password('Mobi$12345'),
                        'fullname': station["operator"]
                    }
                    user_creation_result = account.insert_user(new_account)
                    if not user_creation_result:
                        logger.info(station)
        return True

    def prefetch_zone_search_data(self, zone: str):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']

        query = {"zone": zone}
        records = station_collection.find(
            query, {"_id": 0, "station_code": 1, "province": 1, "district": 1})

        stations_list = []
        for station in records:
            stations_list.append(station)
        return stations_list

    def prefetch_search_data(self):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']

        query = {}
        records = station_collection.find(
            query, {"_id": 0, "station_code": 1, "province": 1, "district": 1})

        stations_list = []
        for station in records:
            stations_list.append(station)
        return stations_list

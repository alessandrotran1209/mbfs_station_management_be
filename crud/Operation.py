import logging

from crud.Station import Station
from db.MongoConn import MongoConn
from datetime import datetime, timedelta
from pymongo.collation import Collation

logger = logging.getLogger(__name__)

class Operation():
    def get_operations(self, operator_name, page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        operation_collection = client['operation']
        total = operation_collection.count_documents({"operator": operator_name})
        records = operation_collection.find({"operator": operator_name}, {"_id": 0}).skip((page - 1) * 10).limit(
            10).sort([("status", 1), ("start_date", -1)]).collation(Collation(locale="en_US", numericOrdering=True))

        list_operations_detail = []
        index = 1
        for operation in records:
            operation["start_date"] = operation["start_date"].strftime("%d/%m/%Y %H:%M:%S")
            if "end_date" in operation:
                operation["end_date"] = operation["end_date"].strftime("%d/%m/%Y %H:%M:%S")
            operation['index'] = index + (page - 1) * 10
            list_operations_detail.append(operation)
            index += 1
        return list_operations_detail, total

    def get_group_operations(self, operator_name, page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        group_leader_collection = client['group-leader']
        record = group_leader_collection.find_one({'username': operator_name}, {"_id": 0, "group": 1})
        group_name = record["group"]

        operation_collection = client['operation']
        total = operation_collection.count_documents({"group": group_name})
        records = operation_collection.find({"group": group_name}, {"_id": 0}).skip((page - 1) * 10).limit(
            10).sort([("status", 1), ("start_date", -1)]).collation(Collation(locale="en_US", numericOrdering=True))

        list_operations_detail = []
        index = 1
        for operation in records:
            operation["start_date"] = operation["start_date"].strftime("%d/%m/%Y %H:%M:%S")
            if "end_date" in operation:
                operation["end_date"] = operation["end_date"].strftime("%d/%m/%Y %H:%M:%S")
            operation['index'] = index + (page - 1) * 10
            list_operations_detail.append(operation)
            index += 1
        return list_operations_detail, total

    def complete_operation(self, operation, operator):
        try:
            mongo_conn = MongoConn()
            client = mongo_conn.conn()

            operation_collection = client['operation']
            station_code = operation["station_code"]
            operation_date = datetime.fromisoformat(operation["date"])
            word_code = str(operation["work_code"])
            query = {"operator": operator, "station_code": station_code, "start_date": operation_date,
                     "work_code": word_code, "status": 0}
            new_values = {"$set": {"status": 1, "end_date": datetime.today()}}

            operation_collection.update_one(query, new_values)
        except Exception as e:
            raise Exception(e)
        return True

    def search_operation(self, operator_name='', station_code='', start_date='', end_date='', status='', page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        end_date = datetime.today() + timedelta(days=1) if end_date == '' else datetime.strptime(end_date,
                                                                                                 '%d/%m/%Y') + timedelta(
            days=1)
        start_date = datetime(1, 1, 1, 0, 0) if start_date == '' else datetime.strptime(start_date, '%d/%m/%Y')

        operation_collection = client['operation']

        if status == '':
            total = operation_collection.count_documents(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}
                 })
            records = operation_collection.find(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}},
                {"_id": 0}).skip((page - 1) * 10).limit(10).sort([("status", 1), ("start_date", -1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        else:
            total = operation_collection.count_documents(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$lt': end_date, '$gte': start_date},
                 "status": int(status)})
            records = operation_collection.find(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date},
                 "status": int(status)},
                {"_id": 0}).skip((page - 1) * 10).limit(10).sort([("status", 1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        list_operations = []

        index = 1
        for operation in records:
            operation['index'] = index + (page - 1) * 10
            operation['start_date'] = operation['start_date'].strftime("%d/%m/%Y")
            operation['end_date'] = operation['end_date'].strftime("%d/%m/%Y") if 'end_date' in operation else ''
            list_operations.append(operation)
            index += 1
        return list_operations, total

    def update_operation(self, operation, operator):
        try:
            mongo_conn = MongoConn()
            client = mongo_conn.conn()

            operation_collection = client['operation']
            station_code = operation["station_code"]
            old_station_code = operation['old_station_code']
            operation_date = datetime.strptime(operation["date"], '%d/%m/%Y')
            old_operation_date = datetime.strptime(operation["old_date"], '%d/%m/%Y')
            word_code = str(operation["work_code"])
            old_work_code = str(operation["old_work_code"])
            query = {"operator": operator, "station_code": old_station_code, "date": old_operation_date,
                     "work_code": old_work_code}
            new_values = {"$set": {"station_code": station_code, "date": operation_date,
                                   "work_code": word_code}}

            operation_collection.update_one(query, new_values)
        except Exception as e:
            raise Exception(e)
        return True

    def insert_operation(self, operation, operator):
        try:
            mongo_conn = MongoConn()
            client = mongo_conn.conn()
            station = Station()
            operation_collection = client['operation']
            station_code = operation["station_code"]
            date = datetime.fromisoformat(operation["date"])
            work_code = operation["work_code"]
            status = 0
            note = operation["note"]
            group_name = station.get_user_group(operator)

            operation_data = {"operator": operator, "assigner": operator, "group": group_name,
                              "station_code": station_code,
                              "start_date": date,
                              "work_code": work_code, "status": status, "note": note}

            operation_collection.insert_one(operation_data)
        except Exception as e:
            raise Exception(e)
        return True

    def insert_operation_by_group_leader(self, operation, assigner):
        try:
            mongo_conn = MongoConn()
            station = Station()
            client = mongo_conn.conn()
            operation_collection = client['operation']
            operator = operation['operator']
            station_code = operation["station_code"]
            date = datetime.fromisoformat(operation["date"])
            work_code = operation["work_code"]
            status = 0
            note = operation["note"]
            group_name = station.get_user_group(operator)

            operation_data = {"assigner": assigner, "operator": operator, "group": group_name,
                              "station_code": station_code,
                              "start_date": date,
                              "work_code": work_code, "status": status, "note": note, }

            operation_collection.insert_one(operation_data)
        except Exception as e:
            raise Exception(e)
        return True

    def get_all_operations(self, page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        operation_collection = client['operation']
        total = operation_collection.count_documents({})
        records = operation_collection.find({}, {"_id": 0}).skip((page - 1) * 10).limit(
            10).sort([("status", 1)]).collation(Collation(locale="en_US", numericOrdering=True))

        list_operations_detail = []
        index = 1
        for operation in records:
            operation["start_date"] = operation["start_date"].strftime("%d/%m/%Y %H:%M:%S")
            if "end_date" in operation:
                operation["end_date"] = operation["end_date"].strftime("%d/%m/%Y %H:%M:%S")
            operation['index'] = index + (page - 1) * 10
            list_operations_detail.append(operation)
            index += 1
        return list_operations_detail, total

import logging
from tokenize import group
import dateutil.parser
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
        total = operation_collection.count_documents(
            {"operator": operator_name})
        records = operation_collection.find({"operator": operator_name}, {"_id": 0}).skip((page - 1) * 10).limit(
            10).sort([("status", 1), ("start_date", -1)]).collation(Collation(locale="en_US", numericOrdering=True))

        list_operations_detail = []
        index = 1
        for operation in records:
            operation["start_date"] = operation["start_date"].strftime(
                "%d/%m/%Y %H:%M:%S")
            if "end_date" in operation:
                operation["end_date"] = operation["end_date"].strftime(
                    "%d/%m/%Y %H:%M:%S")
            operation['index'] = index + (page - 1) * 10
            list_operations_detail.append(operation)
            index += 1
        return list_operations_detail, total

    def get_group_operations(self, operator_name, page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        group_leader_collection = client['group-leader']
        record = group_leader_collection.find_one(
            {'username': operator_name}, {"_id": 0, "group": 1})
        group_name = record["group"]
        print(group_name)
        operation_collection = client['operation']
        total = operation_collection.count_documents({"group": group_name})
        records = operation_collection.find({"group": group_name}, {"_id": 0}).skip((page - 1) * 10).limit(
            10).sort([("status", 1), ("start_date", -1)]).collation(Collation(locale="en_US", numericOrdering=True))

        list_operations_detail = []
        index = 1
        for operation in records:
            operation["start_date"] = operation["start_date"].strftime(
                "%d/%m/%Y %H:%M:%S")
            if "end_date" in operation:
                operation["end_date"] = operation["end_date"].strftime(
                    "%d/%m/%Y %H:%M:%S")
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
            operation_date = dateutil.parser.isoparse(operation["date"])
            word_code = str(operation["work_code"])
            query = {"operator": operation["operator"], "station_code": station_code, "start_date": operation_date,
                     "work_code": word_code, "status": "0"}
            new_values = {"$set": {"status": "1",
                                   "end_date": datetime.today()}}

            operation_collection.update_one(query, new_values)
        except Exception as e:
            raise Exception(e)
        return True

    def search_operation(self, operator_name='', station_code='', start_date='', end_date='', work_code='', status='', page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        end_date = datetime.today() + timedelta(days=1) if end_date == '' else datetime.strptime(end_date,
                                                                                                 '%d/%m/%Y') + timedelta(
            days=1)
        start_date = datetime(1, 1, 1, 0, 0) if start_date == '' else datetime.strptime(
            start_date, '%d/%m/%Y')

        operation_collection = client['operation']

        if status == '':
            total = operation_collection.count_documents(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code}
                 })
            records = operation_collection.find(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code}},
                {"_id": 0}).skip((page - 1) * 10).limit(10).sort([("status", 1), ("start_date", -1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        else:
            total = operation_collection.count_documents(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$lt': end_date, '$gte': start_date}, "work_code": {'$regex': work_code},
                 "status": str(status)})
            records = operation_collection.find(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code},
                 "status": str(status)},
                {"_id": 0}).skip((page - 1) * 10).limit(10).sort([("status", 1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        list_operations = []

        index = 1
        for operation in records:
            operation['index'] = index + (page - 1) * 10
            operation['start_date'] = operation['start_date'].strftime(
                "%d/%m/%Y %H:%M:%S")
            operation['end_date'] = operation['end_date'].strftime(
                "%d/%m/%Y %H:%M:%S") if 'end_date' in operation else ''
            list_operations.append(operation)
            index += 1
        return list_operations, total

    def search_group_operation(self, operator_name='', station_code='', start_date='', end_date='', work_code='', status='', page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        end_date = datetime.today() + timedelta(days=1) if end_date == '' else datetime.strptime(end_date,
                                                                                                 '%d/%m/%Y') + timedelta(
            days=1)
        start_date = datetime(1, 1, 1, 0, 0) if start_date == '' else datetime.strptime(
            start_date, '%d/%m/%Y')

        operation_collection = client['operation']

        if status == '':
            total = operation_collection.count_documents(
                {"assigner": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code}
                 })
            records = operation_collection.find(
                {"assigner": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code}},
                {"_id": 0}).skip((page - 1) * 10).limit(10).sort([("status", 1), ("start_date", -1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        else:
            total = operation_collection.count_documents(
                {"assigner": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$lt': end_date, '$gte': start_date}, "work_code": {'$regex': work_code},
                 "status": str(status)})
            records = operation_collection.find(
                {"assigner": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code},
                 "status": str(status)},
                {"_id": 0}).skip((page - 1) * 10).limit(10).sort([("status", 1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        list_operations = []

        index = 1
        for operation in records:
            operation['index'] = index + (page - 1) * 10
            operation['start_date'] = operation['start_date'].strftime(
                "%d/%m/%Y %H:%M:%S")
            operation['end_date'] = operation['end_date'].strftime(
                "%d/%m/%Y %H:%M:%S") if 'end_date' in operation else ''
            list_operations.append(operation)
            index += 1
        return list_operations, total

    def search_admin_operation(self, group='', role='admin', operator_name='', station_code='', start_date='', end_date='', work_code='', status='', page=1, province='', district=''):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        end_date = datetime.today() + timedelta(days=1) if end_date == '' else datetime.strptime(end_date,
                                                                                                 '%d/%m/%Y') + timedelta(
            days=1)
        start_date = datetime(1, 1, 1, 0, 0) if start_date == '' else datetime.strptime(
            start_date, '%d/%m/%Y')

        operation_collection = client['operation']

        pagination_query = {'$facet': {
            'paginatedResults': [{'$skip': (page-1)*10}, {'$limit': 10}],
            'totalCount': [
                {'$count': 'count'
                 }
            ]
        }
        }
        sort_query = {
            "$sort": {"status": 1, "start_date": -1}
        }
        lookup_query = {
            "$lookup":
            {"from": "station", "localField": "station_code",
             "foreignField": "station_code", "as": "new"}
        }

        match_query = {
            '$match': {
                'station_code': {'$regex': station_code},
                'start_date': {'$gte': start_date, '$lt': end_date},
                'work_code': {'$regex': work_code},
                'status': {'$regex': str(status)},
                'new.province': {'$regex': province},
                'new.district': {'$regex': district}
            }
        }

        if role == 'operator':
            match_query['$match']['operator'] = operator_name
        elif role == 'group leader':
            match_query['$match']['group'] = group
        pipeline = [lookup_query, match_query,
                    pagination_query, sort_query]

        records = operation_collection.aggregate(pipeline)

        list_operations = []
        index = 1
        logger.info(match_query)
        for result in records:
            total = result['totalCount'][0]['count'] if result['totalCount'] else 0
            for operation in result['paginatedResults']:
                if 'new' in operation:
                    del operation['new']
                if '_id' in operation:
                    del operation['_id']
                operation['index'] = index + (page - 1) * 10
                operation['start_date'] = operation['start_date'].strftime(
                    "%d/%m/%Y %H:%M:%S")
                operation['end_date'] = operation['end_date'].strftime(
                    "%d/%m/%Y %H:%M:%S") if 'end_date' in operation else ''
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
            old_operation_date = datetime.strptime(
                operation["old_date"], '%d/%m/%Y')
            word_code = str(operation["work_code"])
            old_work_code = str(operation["old_work_code"])
            note = operation["note"]
            query = {"operator": operation["operator"], "station_code": old_station_code, "date": old_operation_date,
                     "work_code": old_work_code}
            new_values = {"$set": {"station_code": station_code, "date": operation_date,
                                   "work_code": word_code, "note": note}}

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
            date = dateutil.parser.isoparse(operation["date"])
            work_code = operation["work_code"]
            status = "0"
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
            date = dateutil.parser.isoparse(operation["date"])
            work_code = operation["work_code"]
            status = "0"
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
            operation["start_date"] = operation["start_date"].strftime(
                "%d/%m/%Y %H:%M:%S")
            if "end_date" in operation:
                operation["end_date"] = operation["end_date"].strftime(
                    "%d/%m/%Y %H:%M:%S")
            operation['index'] = index + (page - 1) * 10
            list_operations_detail.append(operation)
            index += 1
        return list_operations_detail, total

    def get_group_progress(self):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        operation_collection = client['operation']

        pipeline = [
            {"$group": {"_id": "$group", "count": {"$sum": 1}}}
        ]
        result = operation_collection.aggregate(pipeline)
        total = operation_collection.count_documents({})
        ret = []
        for group_count in result:
            ret.append({
                "Tổ": group_count["_id"],
                "Số bản ghi": group_count["count"]
            })
        return ret, total

    def search_all_operation(self, fullname='', operator_name='', station_code='', start_date='', end_date='', work_code='', status=''):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        end_date = datetime.today() + timedelta(days=1) if end_date == '' else datetime.strptime(end_date,
                                                                                                 '%d/%m/%Y') + timedelta(
            days=1)
        start_date = datetime(1, 1, 1, 0, 0) if start_date == '' else datetime.strptime(
            start_date, '%d/%m/%Y')

        operation_collection = client['operation']

        if status == '':
            records = operation_collection.find(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code}},
                {"_id": 0}).sort([("status", 1), ("start_date", -1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        else:
            records = operation_collection.find(
                {"operator": operator_name, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}, "work_code": {'$regex': work_code},
                 "status": str(status)},
                {"_id": 0}).sort([("status", 1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        list_operations = []

        index = 1
        for operation in records:
            operation['index'] = index
            operation['start_date'] = operation['start_date'].strftime(
                "%d/%m/%Y %H:%M:%S")
            operation['end_date'] = operation['end_date'].strftime(
                "%d/%m/%Y %H:%M:%S") if 'end_date' in operation else ''
            operation['operator'] = fullname
            list_operations.append(operation)
            index += 1
        return list_operations

    def search_all_group_operation(self, group='', station_code='', start_date='', end_date='', status=''):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        end_date = datetime.today() + timedelta(days=1) if end_date == '' else datetime.strptime(end_date,
                                                                                                 '%d/%m/%Y') + timedelta(
            days=1)
        start_date = datetime(1, 1, 1, 0, 0) if start_date == '' else datetime.strptime(
            start_date, '%d/%m/%Y')

        operation_collection = client['operation']

        if status == '':
            records = operation_collection.find(
                {"group": group, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date}},
                {"_id": 0}).sort([("status", 1), ("start_date", -1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        else:
            records = operation_collection.find(
                {"group": group, "station_code": {'$regex': station_code},
                 "start_date": {'$gte': start_date, '$lt': end_date},
                 "status": str(status)},
                {"_id": 0}).sort([("status", 1)]).collation(
                Collation(locale="en_US", numericOrdering=True))
        list_operations = []

        index = 1
        for operation in records:
            operation['index'] = index
            operation['start_date'] = operation['start_date'].strftime(
                "%d/%m/%Y %H:%M:%S")
            operation['end_date'] = operation['end_date'].strftime(
                "%d/%m/%Y %H:%M:%S") if 'end_date' in operation else ''
            user_collection = client['user']
            user_record = user_collection.find_one(
                {"username": operation['operator']})
            if user_record:
                operation["operator_fullname"] = user_record["fullname"]
            
            list_operations.append(operation)
            index += 1
        return list_operations

    def search_admin_all_operation(self, work_code='', station_code='', start_date='', end_date='', status='', province='', district=''):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        end_date = datetime.today() + timedelta(days=1) if end_date == '' else datetime.strptime(end_date,
                                                                                                 '%d/%m/%Y') + timedelta(
            days=1)
        start_date = datetime(1, 1, 1, 0, 0) if start_date == '' else datetime.strptime(
            start_date, '%d/%m/%Y')

        operation_collection = client['operation']

        sort_query = {
            "$sort": {"status": 1, "start_date": -1}
        }
        lookup_query = {
            "$lookup":
            {"from": "station", "localField": "station_code",
             "foreignField": "station_code", "as": "new"}
        }

        match_query = {
            '$match': {
                'station_code': {'$regex': station_code},
                'start_date': {'$gte': start_date, '$lt': end_date},
                'work_code': {'$regex': work_code},
                'status': {'$regex': str(status)},
                'new.province': {'$regex': province},
                'new.district': {'$regex': district}
            }
        }

        pipeline = [lookup_query, match_query,
                    sort_query]
        records = operation_collection.aggregate(pipeline)
        list_operations = []

        index = 1
        for operation in records:
            try:
                if '_id' in operation:
                    del operation['_id']
                if 'new' in operation:
                    del operation['new']
                operator = operation['operator']
                user_collection = client['user']
                user_record = user_collection.find_one({"username": operator})
                if user_record:
                    operation["operator_fullname"] = user_record["fullname"]
                else:
                    raise Exception(operation)
                operation["group"] = operation["group"]
                operation['index'] = index
                operation['start_date'] = operation['start_date'].strftime(
                    "%d/%m/%Y %H:%M:%S")
                operation['end_date'] = operation['end_date'].strftime(
                    "%d/%m/%Y %H:%M:%S") if 'end_date' in operation else ''
                list_operations.append(operation)
                index += 1
            except Exception as e:
                logger.info(operation)
                logger.info(e.args)
        return list_operations

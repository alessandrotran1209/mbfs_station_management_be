import pandas as pd
from pymongo import MongoClient
import time


connection_string = "mongodb://vhkt:Vhkt%402022@103.21.148.67:27017/?authMechanism=DEFAULT&authSource=hatang-db"

conn = MongoClient(connection_string)
client = conn['hatang-db']
operation_collection = client['operation']
zone = 'MLMB'

lookup_query = {
    "$lookup":
    {"from": "station", "localField": "group",
     "foreignField": "group", "as": "station"}
}
match_query = {
    '$match': {
        'station.zone': zone,
    }
}
# pipeline = [lookup_query, match_query]
# start_time = time.time()
# records = operation_collection.aggregate(pipeline)
# completed, uncompleted = 0, 0
# for record in records:
#     if record["status"] == '1':
#         completed += 1
#     else:
#         uncompleted += 1
# print(completed, uncompleted, f'elapsed time: {time.time()-start_time}')

province = 'Hà Nội'
district = ''
page = 2
station_collection = client['station']
alt_match_query = {
    '$match': {
        'zone': zone,
        'province': {'$regex': province},
        'district': {'$regex': district}
    }
}
alt_lookup_query = {
    "$lookup": {
        "from": "operation", "localField": "group",
        "foreignField": "group", "as": "operation"
    }
}
alt_match_postquery = {
    '$match': {
        'operation.station_code': 'tuongnv'
    }
}
alt_pagination_query = {
    '$facet': {
        'paginatedResults': [{'$limit': page*10}, {'$skip': (page-1)*10}],
        'totalCount': [
            {'$count': 'count'}
        ]
    }
}
alt_pipeline = [alt_match_query, alt_lookup_query,
                alt_match_postquery, {
                    "$project": {"_id": 0, "operation": 0}
                }, alt_pagination_query]
start_time = time.time()
records = station_collection.aggregate(alt_pipeline)
completed, uncompleted = 0, 0
for record in records:
    print(record)
print(completed, uncompleted)
print(f'elapsed time: {time.time()-start_time}')

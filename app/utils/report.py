import pandas as pd
from pymongo import MongoClient


connection_string = "mongodb://vhkt:Vhkt%402022@103.21.148.67:27017/?authMechanism=DEFAULT&authSource=hatang-db"

conn = MongoClient(connection_string)
client = conn['hatang-db']
user_collection = client['user']
station_collection = client["station"]
data = []
records = user_collection.find({})
for record in records:
    try:
        if 'group' in record:
            continue
        operator_fullname = record["fullname"]
        operator_username = record["username"]

        station_record = station_collection.find_one({"operator": operator_fullname})
        group_name = station_record["group"]

        user_collection.update_one({"username": operator_username}, {"$set": {"group": group_name}})
    except Exception as e:
        print(record)
        print(e)


